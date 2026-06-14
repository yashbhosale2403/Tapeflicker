from django.contrib import admin
from .models import Category, Course, Module, Lesson, LessonResource, Enrollment, UserLessonProgress, CourseAccess

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'price', 'is_free', 'difficulty')
    list_filter = ('category', 'difficulty', 'is_free')
    search_fields = ('title', 'instructor')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'instructor', 'difficulty')
        }),
        ('Pricing & Access (FREE COURSE BUTTON)', {
            'fields': ('price', 'discount_price', 'is_free', 'is_locked'),
            'description': 'Check "Is free" to allow users to enroll directly without paying.'
        }),
        ('Details & Media', {
            'fields': ('description', 'learning_outcomes', 'prerequisites', 'thumbnail', 'banner', 'is_featured')
        }),
    )

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    ordering = ('course', 'order')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'duration', 'order', 'is_preview', 'is_published')
    list_filter = ('module__course', 'is_preview', 'is_published')
    ordering = ('module__course', 'module', 'order')
    search_fields = ('title', 'module__title', 'module__course__title', 'youtube_video_id')
    fields = (
        'module',
        'title',
        'video_url',
        'duration',
        'order',
        'description',
        'notes',
        'resource_file',
        'is_preview',
        'is_published',
    )

@admin.register(LessonResource)
class LessonResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'created_at')
    search_fields = ('title', 'lesson__title', 'lesson__module__course__title')
    list_filter = ('lesson__module__course',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'progress', 'is_active', 'enrolled_at')
    list_filter = ('is_active', 'course')
    search_fields = ('user__username', 'user__email', 'course__title')

@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'is_completed', 'watched_seconds', 'last_watched', 'completed_at')
    list_filter = ('is_completed', 'lesson__module__course')
    search_fields = ('user__username', 'lesson__title')

@admin.register(CourseAccess)
class CourseAccessAdmin(admin.ModelAdmin):
    list_display = ('email', 'course', 'granted_at')
    search_fields = ('email', 'course__title')
