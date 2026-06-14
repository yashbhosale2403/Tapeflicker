from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from courses.models import Enrollment, UserLessonProgress

@login_required(login_url='accounts:login')
def dashboard_home(request):
    enrollments = Enrollment.objects.filter(user=request.user, is_active=True).select_related('course')
    
    # Compute Stats
    completed_courses = enrollments.filter(progress=100).count()
    
    # Compute Hours Learned
    progresses = UserLessonProgress.objects.filter(user=request.user, is_completed=True).select_related('lesson')
    total_minutes = sum(p.lesson.get_duration_in_minutes() for p in progresses)
    hours_learned = int(total_minutes // 60)
    
    # Continue Learning
    continue_learning = enrollments.order_by('-last_accessed_at').first()
    
    return render(request, 'dashboard/index.html', {
        'enrollments': enrollments,
        'completed_courses': completed_courses,
        'hours_learned': hours_learned,
        'continue_learning': continue_learning,
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
