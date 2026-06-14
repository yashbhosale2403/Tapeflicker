from django.contrib import admin
from .models import CourseChatRoom, ChatParticipantState, ChatMessage, ChatReaction, ChatReport, ChatModerationLog


@admin.register(CourseChatRoom)
class CourseChatRoomAdmin(admin.ModelAdmin):
    list_display = ('course', 'is_locked', 'is_archived', 'read_only', 'created_at')
    list_filter = ('is_locked', 'is_archived', 'read_only')


@admin.register(ChatParticipantState)
class ChatParticipantStateAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'unread_count', 'is_banned', 'muted_until', 'updated_at')
    search_fields = ('user__username', 'room__course__title')
    list_filter = ('is_banned',)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'user', 'is_deleted', 'is_pinned', 'is_announcement', 'created_at')
    search_fields = ('content', 'user__username', 'room__course__title')
    list_filter = ('is_deleted', 'is_pinned', 'is_announcement')


@admin.register(ChatReaction)
class ChatReactionAdmin(admin.ModelAdmin):
    list_display = ('message', 'user', 'emoji', 'created_at')


@admin.register(ChatReport)
class ChatReportAdmin(admin.ModelAdmin):
    list_display = ('message', 'reporter', 'reason', 'resolved', 'created_at')
    list_filter = ('resolved',)


@admin.register(ChatModerationLog)
class ChatModerationLogAdmin(admin.ModelAdmin):
    list_display = ('room', 'actor', 'action', 'target_user', 'created_at')
    search_fields = ('action', 'details', 'actor__username', 'target_user__username')

# Register your models here.
