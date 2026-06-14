from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from urllib.parse import parse_qs, urlparse
import logging
import re
import uuid
import os

User = get_user_model()
logger = logging.getLogger(__name__)

from django.utils.deconstruct import deconstructible

@deconstructible
class UniqueUploadPath:
    """Generates a secure UUID-based filename path to prevent path traversal & script-execution.
    Decorated with @deconstructible to allow Django migrations serialization."""
    def __init__(self, prefix):
        self.prefix = prefix

    def __call__(self, instance, filename):
        ext = os.path.splitext(filename)[1].lower()
        return os.path.join(self.prefix, f"{uuid.uuid4()}{ext}")


@deconstructible
class FileSizeValidator:
    """Enforces maximum file size limit in megabytes.
    Decorated with @deconstructible to allow Django migrations serialization."""
    def __init__(self, max_size_mb):
        self.max_size_mb = max_size_mb

    def __call__(self, file):
        if file.size > self.max_size_mb * 1024 * 1024:
            raise ValidationError(f"File size cannot exceed {self.max_size_mb}MB.")


# Safe extensions to mitigate script injection/execution (RCE)
SAFE_DOC_EXTENSIONS = [
    'pdf', 'zip', 'rar', 'doc', 'docx', 'xls', 'xlsx', 
    'ppt', 'pptx', 'txt', 'png', 'jpg', 'jpeg', 'webp', 'mp4', 'avi', 'mov'
]
IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'webp', 'gif']


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name_plural = "Categories"

class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    instructor = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    discount_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    description = models.TextField()
    learning_outcomes = models.TextField(blank=True, help_text="Enter learning outcomes separated by new lines.")
    prerequisites = models.TextField(blank=True)
    thumbnail = models.ImageField(
        upload_to=UniqueUploadPath('course_thumbnails/'), 
        blank=True, 
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=IMAGE_EXTENSIONS),
            FileSizeValidator(5)
        ]
    )
    banner = models.ImageField(
        upload_to=UniqueUploadPath('course_banners/'), 
        blank=True, 
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=IMAGE_EXTENSIONS),
            FileSizeValidator(5)
        ]
    )
    is_featured = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False, help_text="Check this to make the course free. Users won't need to pay.")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

    @property
    def total_lessons(self):
        return Lesson.objects.filter(module__course=self).count()

    @property
    def total_duration_hours(self):
        lessons = Lesson.objects.filter(module__course=self)
        total_mins = 0
        for l in lessons:
            try:
                parts = [int(p) for p in l.duration.split(':')]
                if len(parts) == 2:
                    total_mins += parts[0] + parts[1]/60.0
                elif len(parts) == 3:
                    total_mins += parts[0]*60 + parts[1] + parts[2]/60.0
            except:
                pass
        val = round(total_mins / 60.0, 1)
        return val if val > 0 else 0.0


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    video_url = models.URLField(help_text="Paste YouTube URL: watch, youtu.be, or embed.")
    youtube_video_id = models.CharField(max_length=20, blank=True, editable=False)
    duration = models.CharField(max_length=20, help_text="e.g., '10:30'")
    order = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True, help_text="Internal lesson notes or student-facing notes.")
    resource_file = models.FileField(
        upload_to=UniqueUploadPath('lesson_resources/'), 
        blank=True, 
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=SAFE_DOC_EXTENSIONS),
            FileSizeValidator(25)
        ]
    )
    is_preview = models.BooleanField(default=False, help_text="Preview lessons are visible without enrollment.")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

    def get_duration_in_minutes(self):
        try:
            parts = [int(p) for p in self.duration.split(':')]
            if len(parts) == 2:
                return parts[0] + parts[1]/60.0
            elif len(parts) == 3:
                return parts[0]*60 + parts[1] + parts[2]/60.0
        except:
            return 0
        return 0

    @property
    def embed_url(self):
        video_id = self.youtube_video_id
        if not video_id and self.video_url:
            video_id = self.extract_youtube_id(self.video_url)
        if video_id and re.match(r"^[a-zA-Z0-9_-]{11}$", video_id):
            return f"https://www.youtube-nocookie.com/embed/{video_id}"
        return ""

    @property
    def youtube_watch_url(self):
        video_id = self.youtube_video_id
        if not video_id and self.video_url:
            video_id = self.extract_youtube_id(self.video_url)
        if video_id and re.match(r"^[a-zA-Z0-9_-]{11}$", video_id):
            return f"https://www.youtube.com/watch?v={video_id}"
        return ""

    @staticmethod
    def extract_youtube_id(url):
        if not url:
            return ""
        raw = url.strip()

        # Direct ID support (11 chars) for admin convenience.
        if re.match(r"^[a-zA-Z0-9_-]{11}$", raw):
            return raw

        parsed = urlparse(raw)
        host = parsed.netloc.lower().replace("www.", "")
        path = parsed.path.strip("/")
        query = parse_qs(parsed.query)

        video_id = ""
        if host in {"youtube.com", "m.youtube.com", "music.youtube.com"}:
            if path == "watch":
                video_id = query.get("v", [""])[0]
            elif path.startswith("embed/"):
                video_id = path.split("/", 1)[1].split("/")[0]
            elif path.startswith("shorts/"):
                video_id = path.split("/", 1)[1].split("/")[0]
            elif path.startswith("live/"):
                video_id = path.split("/", 1)[1].split("/")[0]
        elif host == "youtu.be":
            video_id = path.split("/")[0]

        # Strip accidental query fragments that might survive edge cases.
        video_id = video_id.split("?")[0].split("&")[0].strip()
        if re.match(r"^[a-zA-Z0-9_-]{11}$", video_id):
            return video_id
        return ""

    def clean(self):
        super().clean()
        original_url = self.video_url or ""
        video_id = self.extract_youtube_id(self.video_url)
        if not video_id:
            logger.warning("Invalid YouTube URL for lesson '%s': %s", self.title, self.video_url)
            raise ValidationError({"video_url": "Invalid YouTube URL. Use watch, youtu.be, or embed URL."})
        if "shorts/" in original_url.lower():
            logger.info("Detected YouTube Shorts URL for lesson '%s'. Converting to standard embed video ID.", self.title)
        self.youtube_video_id = video_id
        # Normalize stored URL to a safe canonical watch format.
        self.video_url = f"https://www.youtube.com/watch?v={video_id}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class LessonResource(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    file = models.FileField(
        upload_to=UniqueUploadPath('lesson_resources/'), 
        blank=True, 
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=SAFE_DOC_EXTENSIONS),
            FileSizeValidator(25)
        ]
    )
    external_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if not self.file and not self.external_url:
            raise ValidationError("Add a file or external URL for the resource.")

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    last_accessed_lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True)
    last_accessed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"

class UserLessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progresses')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='user_progresses')
    is_completed = models.BooleanField(default=False)
    watched_seconds = models.PositiveIntegerField(default=0)
    last_watched = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} - {self.is_completed}"

class CourseAccess(models.Model):
    email = models.EmailField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('email', 'course')

    def __str__(self):
        return f"{self.email} -> {self.course.title}"
