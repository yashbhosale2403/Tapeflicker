from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Prefetch
from .models import Course, Category, Lesson, Enrollment, UserLessonProgress
import json

def course_list(request):
    category_slug = request.GET.get('category')
    if category_slug:
        courses = Course.objects.filter(category__slug=category_slug, is_locked=False).order_by('-created_at')
    else:
        courses = Course.objects.filter(is_locked=False).order_by('-created_at')
        
    categories = Category.objects.all()
    return render(request, 'courses/list.html', {'courses': courses, 'categories': categories, 'current_category': category_slug})

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_locked=False)
    modules = course.modules.all().prefetch_related(
        Prefetch('lessons', queryset=Lesson.objects.filter(is_published=True).order_by('order'))
    )
    
    # Check if user is already enrolled
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
        
    first_published_lesson = Lesson.objects.filter(module__course=course, is_published=True).order_by('module__order', 'order', 'id').first()

    return render(request, 'courses/detail.html', {
        'course': course,
        'modules': modules,
        'is_enrolled': is_enrolled,
        'locked_attempt': request.GET.get('locked') == '1',
        'first_published_lesson': first_published_lesson,
    })

@login_required(login_url='accounts:login')
def enroll_free_course(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id, is_free=True, is_locked=False)
        Enrollment.objects.get_or_create(user=request.user, course=course)
        return redirect('dashboard:home')
    return redirect('courses:detail', course_id=course_id)

def lesson_player(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, is_published=True)
    course = lesson.module.course
    
    # Verify enrollment
    enrollment = None
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(user=request.user, course=course, is_active=True).first()
    has_access = bool(enrollment) or lesson.is_preview or course.is_free
    if not has_access:
        return redirect(f"/courses/{course.id}/?locked=1")
    
    # Update last accessed
    if enrollment:
        enrollment.last_accessed_lesson = lesson
        enrollment.last_accessed_at = timezone.now()
        enrollment.save()
        
    # Get all lessons for sidebar
    modules = course.modules.all().prefetch_related(
        Prefetch('lessons', queryset=Lesson.objects.filter(is_published=True).order_by('order'))
    )
    
    # Get completed lessons for this user
    if request.user.is_authenticated:
        completed_lesson_ids = set(
            UserLessonProgress.objects.filter(user=request.user, is_completed=True).values_list('lesson_id', flat=True)
        )
        user_progress = UserLessonProgress.objects.filter(user=request.user, lesson=lesson).first()
    else:
        completed_lesson_ids = set()
        user_progress = None

    all_lessons = list(
        Lesson.objects.filter(module__course=course, is_published=True).order_by('module__order', 'order', 'id')
    )
    current_index = next((idx for idx, item in enumerate(all_lessons) if item.id == lesson.id), None)
    next_lesson = all_lessons[current_index + 1] if current_index is not None and current_index + 1 < len(all_lessons) else None
    prev_lesson = all_lessons[current_index - 1] if current_index not in (None, 0) else None

    total_lessons = len(all_lessons)
    completed_count = len([x for x in all_lessons if x.id in completed_lesson_ids])
    progress_percent = int((completed_count / total_lessons) * 100) if total_lessons else 0

    return render(request, 'courses/lesson_player.html', {
        'lesson': lesson,
        'course': course,
        'modules': modules,
        'completed_lesson_ids': completed_lesson_ids,
        'enrollment': enrollment
        ,'user_progress': user_progress,
        'next_lesson': next_lesson,
        'prev_lesson': prev_lesson,
        'total_lessons': total_lessons,
        'completed_count': completed_count,
        'progress_percent': progress_percent,
    })

def _can_access_lesson(user, lesson):
    if lesson.is_preview:
        return True
    return Enrollment.objects.filter(user=user, course=lesson.module.course, is_active=True).exists()

def _update_enrollment_progress(user, course):
    enrollment = Enrollment.objects.filter(user=user, course=course, is_active=True).first()
    if not enrollment:
        return None
    total_lessons = Lesson.objects.filter(module__course=course, is_published=True).count()
    completed_lessons = UserLessonProgress.objects.filter(
        user=user,
        lesson__module__course=course,
        lesson__is_published=True,
        is_completed=True,
    ).count()
    enrollment.progress = int((completed_lessons / total_lessons) * 100) if total_lessons else 0
    enrollment.save(update_fields=['progress'])
    return enrollment

@login_required(login_url='accounts:login')
@require_POST
def mark_lesson_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, is_published=True)
    if not _can_access_lesson(request.user, lesson):
        return JsonResponse({'status': 'forbidden'}, status=403)

    progress, _ = UserLessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
    )
    progress.is_completed = True
    if not progress.completed_at:
        progress.completed_at = timezone.now()
    progress.last_watched = timezone.now()
    progress.save(update_fields=['is_completed', 'completed_at', 'last_watched'])

    enrollment = _update_enrollment_progress(request.user, lesson.module.course)
    return JsonResponse({'status': 'success', 'progress': enrollment.progress if enrollment else 0})

@login_required(login_url='accounts:login')
@require_POST
def track_lesson_progress(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, is_published=True)
    if not _can_access_lesson(request.user, lesson):
        return JsonResponse({'status': 'forbidden'}, status=403)

    payload = json.loads(request.body or '{}')
    watched_seconds = max(0, int(payload.get('watched_seconds', 0)))
    mark_completed = bool(payload.get('completed', False))

    progress, _ = UserLessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
    if watched_seconds > progress.watched_seconds:
        progress.watched_seconds = watched_seconds
    progress.last_watched = timezone.now()
    if mark_completed:
        progress.is_completed = True
        if not progress.completed_at:
            progress.completed_at = timezone.now()
    progress.save(update_fields=['watched_seconds', 'last_watched', 'is_completed', 'completed_at'])

    enrollment = Enrollment.objects.filter(user=request.user, course=lesson.module.course, is_active=True).first()
    if enrollment:
        enrollment.last_accessed_lesson = lesson
        enrollment.last_accessed_at = timezone.now()
        enrollment.save(update_fields=['last_accessed_lesson', 'last_accessed_at'])
    enrollment = _update_enrollment_progress(request.user, lesson.module.course)

    return JsonResponse({
        'status': 'success',
        'progress': enrollment.progress if enrollment else 0,
        'watched_seconds': progress.watched_seconds,
        'completed': progress.is_completed,
    })
