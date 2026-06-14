from django.shortcuts import render, get_object_or_404
from courses.models import Course, Category
from .models import Event, Testimonial, HeroSection, Stat, AboutPage, ContactMessage

def home(request):
    featured_courses = Course.objects.filter(is_featured=True, is_locked=False)[:3]
    categories = Category.objects.all()
    upcoming_events = Event.objects.filter(is_active=True).order_by('date')[:3]
    testimonials = Testimonial.objects.all()
    hero = HeroSection.objects.filter(is_active=True).first()
    stats = Stat.objects.all()
    
    # Query active enrollments for terminal showcase if logged in
    user_enrollments_list = []
    if request.user.is_authenticated:
        enrollments = request.user.enrollments.filter(is_active=True).select_related('course')[:3]
        for e in enrollments:
            user_enrollments_list.append({
                'title': e.course.title,
                'progress': e.progress
            })
            
    context = {
        'featured_courses': featured_courses,
        'categories': categories,
        'upcoming_events': upcoming_events,
        'testimonials': testimonials,
        'hero': hero,
        'stats': stats,
        'user_enrollments': user_enrollments_list,
    }
    return render(request, 'core/home.html', context)

def about(request):
    about_content = AboutPage.objects.filter(is_active=True).first()
    return render(request, 'core/about.html', {'about': about_content})

from tapeflicker_proj.decorators import ratelimit

@ratelimit('contact', limit=3, period=60)
def contact(request):
    if request.method == 'POST':
        from django.http import JsonResponse
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'All fields are required.'}, status=400)
    return render(request, 'core/contact.html')

def event_list(request):
    event_type = request.GET.get('type', 'all')
    events = Event.objects.filter(is_active=True).order_by('date')
    
    if event_type and event_type != 'all':
        events = events.filter(event_type=event_type)
        
    return render(request, 'core/event_list.html', {'events': events})

def event_detail(request, id):
    event = get_object_or_404(Event, id=id, is_active=True)
    return render(request, 'core/event_detail.html', {'event': event})
