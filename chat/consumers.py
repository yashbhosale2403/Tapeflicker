import json
import re
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.db import models
from .models import CourseChatRoom, ChatMessage, ChatParticipantState, ChatReaction, ChatReport, ChatModerationLog
from .utils import can_moderate_chat


class CourseChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.message_timestamps = []
        self.user = self.scope["user"]
        self.course_id = self.scope["url_route"]["kwargs"]["course_id"]
        self.room_key = f"course_chat_{self.course_id}"
        self.room = await self.get_room()
        if not self.room or not await self.has_access():
            await self.close(code=4003)
            return
        await self.channel_layer.group_add(self.room_key, self.channel_name)
        await self.accept()
        await self.mark_online(True)
        await self.channel_layer.group_send(self.room_key, {
            "type": "presence.event",
            "user_id": self.user.id,
            "username": self.user.username,
            "online": True,
        })

    async def disconnect(self, close_code):
        if getattr(self, "room", None):
            await self.channel_layer.group_discard(self.room_key, self.channel_name)
            await self.mark_online(False)
            await self.channel_layer.group_send(self.room_key, {
                "type": "presence.event",
                "user_id": self.user.id,
                "username": self.user.username,
                "online": False,
            })

    async def receive(self, text_data=None, bytes_data=None):
        import time
        now = time.time()
        self.message_timestamps = [t for t in self.message_timestamps if now - t < 5.0]
        if len(self.message_timestamps) >= 10:
            await self.send(text_data=json.dumps({
                "event": "flood_warning",
                "message": "You are sending messages too quickly. Please slow down."
            }))
            return
        self.message_timestamps.append(now)

        payload = json.loads(text_data or "{}")
        event = payload.get("event")

        if event == "typing":
            await self.channel_layer.group_send(self.room_key, {
                "type": "typing.event",
                "user_id": self.user.id,
                "username": self.user.username,
                "is_typing": bool(payload.get("is_typing")),
            })
            return

        if event == "send_message":
            message = await self.create_message(payload)
            if not message:
                return
            await self.channel_layer.group_send(self.room_key, {
                "type": "message.created",
                "message": message,
            })
            return

        if event == "edit_message":
            updated = await self.edit_message(payload)
            if updated:
                await self.channel_layer.group_send(self.room_key, {
                    "type": "message.updated",
                    "message": updated,
                })
            return

        if event == "delete_message":
            deleted = await self.delete_message(payload)
            if deleted:
                await self.channel_layer.group_send(self.room_key, {
                    "type": "message.deleted",
                    "message_id": deleted,
                })
            return

        if event == "react":
            reaction = await self.react(payload)
            if reaction:
                await self.channel_layer.group_send(self.room_key, {
                    "type": "reaction.updated",
                    "payload": reaction,
                })
            return

    async def message_created(self, event):
        await self.send(text_data=json.dumps({"event": "message_created", **event}))

    async def message_updated(self, event):
        await self.send(text_data=json.dumps({"event": "message_updated", **event}))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({"event": "message_deleted", **event}))

    async def typing_event(self, event):
        await self.send(text_data=json.dumps({"event": "typing", **event}))

    async def presence_event(self, event):
        await self.send(text_data=json.dumps({"event": "presence", **event}))

    async def reaction_updated(self, event):
        await self.send(text_data=json.dumps({"event": "reaction_updated", **event}))

    @database_sync_to_async
    def get_room(self):
        return CourseChatRoom.objects.filter(course_id=self.course_id).first()

    @database_sync_to_async
    def has_access(self):
        return self.room and self.room.can_access(self.user) and not self.room.is_archived

    @database_sync_to_async
    def mark_online(self, is_online):
        if not self.user.is_authenticated:
            return
        state, _ = ChatParticipantState.objects.get_or_create(room=self.room, user=self.user)
        state.last_read_at = timezone.now()
        state.save(update_fields=["last_read_at", "updated_at"])

    @database_sync_to_async
    def create_message(self, payload):
        state, _ = ChatParticipantState.objects.get_or_create(room=self.room, user=self.user)
        if state.is_banned or state.is_muted or self.room.read_only:
            return None
        content = (payload.get("content") or "").strip()
        if not content:
            return None
        reply_to_id = payload.get("reply_to")
        reply_to = ChatMessage.objects.filter(id=reply_to_id, room=self.room).first() if reply_to_id else None
        msg = ChatMessage.objects.create(room=self.room, user=self.user, content=content, reply_to=reply_to)
        usernames = set(re.findall(r'@([A-Za-z0-9_.-]+)', content))
        if usernames:
            mentioned_users = list(self.room.course.enrollments.filter(user__username__in=usernames).values_list('user_id', flat=True))
            if mentioned_users:
                msg.mentions.add(*mentioned_users)
        ChatParticipantState.objects.filter(room=self.room).exclude(user=self.user).update(unread_count=models.F('unread_count') + 1)
        return self.serialize_message(msg)

    @database_sync_to_async
    def edit_message(self, payload):
        msg = ChatMessage.objects.filter(id=payload.get("message_id"), room=self.room, is_deleted=False).first()
        if not msg:
            return None
        if msg.user_id != self.user.id and not can_moderate_chat(self.user):
            return None
        msg.content = (payload.get("content") or "").strip()
        msg.is_edited = True
        msg.save(update_fields=["content", "is_edited", "updated_at"])
        return self.serialize_message(msg)

    @database_sync_to_async
    def delete_message(self, payload):
        msg = ChatMessage.objects.filter(id=payload.get("message_id"), room=self.room, is_deleted=False).first()
        if not msg:
            return None
        if msg.user_id != self.user.id and not can_moderate_chat(self.user):
            return None
        msg.is_deleted = True
        msg.content = ""
        msg.save(update_fields=["is_deleted", "content", "updated_at"])
        return msg.id

    @database_sync_to_async
    def react(self, payload):
        message_id = payload.get("message_id")
        emoji = (payload.get("emoji") or "").strip()
        msg = ChatMessage.objects.filter(id=message_id, room=self.room, is_deleted=False).first()
        if not msg or not emoji:
            return None
        obj, created = ChatReaction.objects.get_or_create(message=msg, user=self.user, emoji=emoji)
        if not created:
            obj.delete()
        reactions = list(
            ChatReaction.objects.filter(message=msg).values("emoji").order_by("emoji")
        )
        aggregated = {}
        for item in reactions:
            aggregated[item["emoji"]] = aggregated.get(item["emoji"], 0) + 1
        return {"message_id": msg.id, "reactions": aggregated}

    def serialize_message(self, msg):
        return {
            "id": msg.id,
            "user_id": msg.user_id,
            "username": msg.user.get_full_name() or msg.user.username,
            "avatar": getattr(getattr(msg.user, "profile", None), "avatar_url", ""),
            "content": msg.content,
            "created_at": msg.created_at.isoformat(),
            "updated_at": msg.updated_at.isoformat(),
            "is_edited": msg.is_edited,
            "is_deleted": msg.is_deleted,
            "reply_to": msg.reply_to_id,
            "is_pinned": msg.is_pinned,
            "is_announcement": msg.is_announcement,
        }
