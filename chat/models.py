from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from courses.models import Course, Enrollment, UniqueUploadPath, FileSizeValidator, SAFE_DOC_EXTENSIONS



class CourseChatRoom(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='chat_room')
    title = models.CharField(max_length=200, blank=True)
    is_locked = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    read_only = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"{self.course.title} Chat"

    def can_access(self, user):
        if not user.is_authenticated:
            return False
        if user.is_staff or user.is_superuser:
            return True
        return Enrollment.objects.filter(user=user, course=self.course, is_active=True).exists()


class ChatParticipantState(models.Model):
    room = models.ForeignKey(CourseChatRoom, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_states')
    unread_count = models.PositiveIntegerField(default=0)
    last_read_at = models.DateTimeField(null=True, blank=True)
    muted_until = models.DateTimeField(null=True, blank=True)
    is_banned = models.BooleanField(default=False)
    sound_enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('room', 'user')

    @property
    def is_muted(self):
        return bool(self.muted_until and self.muted_until > timezone.now())


class ChatMessage(models.Model):
    room = models.ForeignKey(CourseChatRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    content = models.TextField(blank=True)
    attachment = models.FileField(
        upload_to=UniqueUploadPath('chat_attachments/'), 
        blank=True, 
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=SAFE_DOC_EXTENSIONS),
            FileSizeValidator(12)
        ]
    )
    attachment_name = models.CharField(max_length=255, blank=True)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    is_announcement = models.BooleanField(default=False)
    mentions = models.ManyToManyField(User, blank=True, related_name='mentioned_in_chat')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username}: {self.content[:40]}"


class ChatReaction(models.Model):
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_reactions')
    emoji = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user', 'emoji')


class ChatReport(models.Model):
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_reports')
    reason = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)


class ChatModerationLog(models.Model):
    room = models.ForeignKey(CourseChatRoom, on_delete=models.CASCADE, related_name='moderation_logs')
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_actions_taken')
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_actions_received')
    message = models.ForeignKey(ChatMessage, on_delete=models.SET_NULL, null=True, blank=True, related_name='mod_logs')
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

# Create your models here.
