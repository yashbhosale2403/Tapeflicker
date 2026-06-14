from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from courses.models import Course, Enrollment
from .models import CourseChatRoom, ChatMessage, ChatParticipantState, ChatReaction, ChatReport, ChatModerationLog
from .utils import can_moderate_chat
import os


ALLOWED_UPLOAD_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.pdf', '.zip'}
MAX_UPLOAD_BYTES = 12 * 1024 * 1024


def _ensure_room(course):
    room, _ = CourseChatRoom.objects.get_or_create(course=course, defaults={"title": f"{course.title} Community"})
    return room


def _is_enrolled(user, course):
    if user.is_authenticated and (user.is_staff or user.is_superuser):
        return True
    return Enrollment.objects.filter(user=user, course=course, is_active=True).exists()


@login_required(login_url='accounts:login')
def chat_hub(request):
    enrollments = Enrollment.objects.filter(user=request.user, is_active=True).select_related("course")
    rooms = []
    for enrollment in enrollments:
        room = _ensure_room(enrollment.course)
        if not room.is_archived:
            rooms.append(room)
    return render(request, "chat/hub.html", {"rooms": rooms})


@login_required(login_url='accounts:login')
def course_chat_room(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if not _is_enrolled(request.user, course):
        return redirect(f"/courses/{course.id}/?locked=1")
    room = _ensure_room(course)
    if room.is_archived:
        return redirect("chat:hub")
    state, _ = ChatParticipantState.objects.get_or_create(room=room, user=request.user)
    state.last_read_at = timezone.now()
    state.unread_count = 0
    state.save(update_fields=["last_read_at", "unread_count", "updated_at"])
    messages = room.messages.select_related("user", "reply_to").prefetch_related("reactions").order_by("created_at")[:150]
    online_count = room.participants.filter(updated_at__gte=timezone.now() - timezone.timedelta(minutes=5)).count()
    participants = room.participants.select_related("user")[:25]
    pinned = room.messages.filter(is_pinned=True, is_deleted=False).select_related("user").order_by("-created_at")[:20]
    return render(request, "chat/room.html", {
        "course": course,
        "room": room,
        "messages": messages,
        "participants": participants,
        "online_count": online_count,
        "pinned_messages": pinned,
        "state": state,
        "is_moderator": can_moderate_chat(request.user),
    })


@login_required(login_url='accounts:login')
@require_POST
def upload_attachment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if not _is_enrolled(request.user, course):
        return JsonResponse({"status": "forbidden"}, status=403)
    room = _ensure_room(course)
    uploaded = request.FILES.get("file")
    content = (request.POST.get("content") or "").strip()
    reply_to = request.POST.get("reply_to")
    if not uploaded:
        return JsonResponse({"status": "error", "message": "No file uploaded"}, status=400)
    ext = os.path.splitext(uploaded.name)[1].lower()
    if ext not in ALLOWED_UPLOAD_EXTENSIONS:
        return JsonResponse({"status": "error", "message": "Unsupported file type"}, status=400)
    if uploaded.size > MAX_UPLOAD_BYTES:
        return JsonResponse({"status": "error", "message": "File too large"}, status=400)
    state, _ = ChatParticipantState.objects.get_or_create(room=room, user=request.user)
    if state.is_banned or state.is_muted or room.read_only:
        return JsonResponse({"status": "forbidden"}, status=403)
    reply_obj = room.messages.filter(id=reply_to).first() if reply_to else None
    msg = ChatMessage.objects.create(
        room=room,
        user=request.user,
        content=content,
        attachment=uploaded,
        attachment_name=uploaded.name,
        reply_to=reply_obj,
    )
    return JsonResponse({"status": "success", "message_id": msg.id})


@login_required(login_url='accounts:login')
@require_POST
def report_message(request, message_id):
    msg = get_object_or_404(ChatMessage, id=message_id, is_deleted=False)
    if not _is_enrolled(request.user, msg.room.course):
        return JsonResponse({"status": "forbidden"}, status=403)
    reason = (request.POST.get("reason") or "").strip()[:300]
    if not reason:
        return JsonResponse({"status": "error", "message": "Reason required"}, status=400)
    ChatReport.objects.get_or_create(message=msg, reporter=request.user, defaults={"reason": reason})
    return JsonResponse({"status": "success"})

# Create your views here.
