from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from courses.models import Enrollment, UserLessonProgress

@login_required(login_url='accounts:login')
def dashboard_home(request):
    enrollments = Enrollment.objects.filter(user=request.user, is_active=True).select_related('course')
    
    # Compute Stats
    completed_courses = enrollments.filter(progress=100).count()
    in_progress_courses = enrollments.filter(progress__lt=100)
    
    # Continue Learning (Last accessed active course)
    continue_learning = enrollments.order_by('-last_accessed_at').first()
    
    return render(request, 'dashboard/index.html', {
        'enrollments': enrollments,
        'in_progress_courses': in_progress_courses,
        'completed_courses_list': enrollments.filter(progress=100),
        'completed_courses': completed_courses,
        'continue_learning': continue_learning,
    })

@login_required(login_url='accounts:login')
def certificates_view(request):
    completed_enrollments = Enrollment.objects.filter(user=request.user, is_active=True, progress=100).select_related('course')
    return render(request, 'dashboard/certificates.html', {
        'completed_enrollments': completed_enrollments,
        'title': 'Certificates'
    })

@login_required(login_url='accounts:login')
def settings_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        avatar_url = request.POST.get('avatar_url')
        
        user = request.user
        if first_name: user.first_name = first_name
        if last_name: user.last_name = last_name
        user.save()
        
        profile = user.profile
        if avatar_url: profile.avatar_url = avatar_url
        profile.save()
        
        return redirect('dashboard:settings')
        
    return render(request, 'dashboard/settings.html')

@login_required(login_url='accounts:login')
def empty_state_view(request, title):
    return render(request, 'dashboard/empty_state.html', {'title': title})

@login_required(login_url='accounts:login')
def delete_enrollment(request, enrollment_id):
    if request.method == 'POST':
        two_factor_code = request.POST.get('two_factor_code', '').strip()
        expected_code = request.POST.get('expected_code', '').strip()
        
        if not two_factor_code or two_factor_code != expected_code:
            from django.contrib import messages
            messages.error(request, "2FA Security Verification Failed: Invalid 2FA code provided.")
            return redirect('dashboard:home')

        enrollment = get_object_or_404(Enrollment, id=enrollment_id, user=request.user)
        course_title = enrollment.course.title
        UserLessonProgress.objects.filter(user=request.user, lesson__module__course=enrollment.course).delete()
        enrollment.delete()
        
        from django.contrib import messages
        messages.success(request, f"2FA Verified: Successfully unenrolled from '{course_title}'.")
    return redirect('dashboard:home')

