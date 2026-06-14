from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.urls import reverse
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from courses.models import Course, Enrollment, Module, Lesson, LessonResource
from core.models import Event, ContactMessage
from chat.models import CourseChatRoom, ChatMessage, ChatParticipantState, ChatReport, ChatModerationLog
from django.contrib.auth import get_user_model
from .forms import CourseForm, EventForm, ModuleForm, LessonForm, LessonResourceForm

User = get_user_model()
from .models import AuditLog, AffiliateRecord, SupportTicket


@staff_member_required
def dashboard(request):
    total_courses = Course.objects.count()
    total_students = User.objects.filter(is_staff=False, is_superuser=False).count()
    total_enrollments = Enrollment.objects.count()
    pending_enrollments = Enrollment.objects.filter(is_active=False).count()
    recent_courses = Course.objects.order_by('-created_at')[:5]
    upcoming_events = Event.objects.filter(is_active=True).order_by('date')[:4]
    featured_courses = Course.objects.filter(is_featured=True).count()
    locked_courses = Course.objects.filter(is_locked=True).count()

    # Calculate actual revenue from active enrollments
    enrollments = Enrollment.objects.all().select_related('course')
    revenue = sum(e.course.price for e in enrollments if e.is_active)

    # Fetch recent logs and tickets
    recent_logs = AuditLog.objects.all().select_related('actor').order_by('-timestamp')[:5]
    recent_tickets = SupportTicket.objects.all().select_related('user').order_by('-created_at')[:5]

    context = {
        'total_courses': total_courses,
        'total_students': total_students,
        'total_enrollments': total_enrollments,
        'pending_enrollments': pending_enrollments,
        'revenue': revenue,
        'recent_courses': recent_courses,
        'upcoming_events': upcoming_events,
        'featured_courses': featured_courses,
        'locked_courses': locked_courses,
        'recent_logs': recent_logs,
        'recent_tickets': recent_tickets,
    }
    return render(request, 'manager/dashboard.html', context)

# ================= COURSES MODULE =================

@staff_member_required
def course_list(request):
    courses = Course.objects.all().order_by('-created_at')
    return render(request, 'manager/courses_list.html', {'courses': courses})

@staff_member_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course created successfully.')
            return redirect('manager:course_list')
    else:
        form = CourseForm()
    return render(request, 'manager/course_form.html', {'form': form, 'title': 'Create Course'})

@staff_member_required
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully.')
            return redirect('manager:course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'manager/course_form.html', {'form': form, 'title': 'Edit Course', 'course': course})

@staff_member_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully.')
        return redirect('manager:course_list')
    return render(request, 'manager/confirm_delete.html', {'object': course, 'cancel_url': 'manager:course_list'})

@staff_member_required
def course_content(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    modules = course.modules.all().prefetch_related('lessons__resources').order_by('order')
    return render(request, 'manager/course_content.html', {
        'course': course,
        'modules': modules,
    })

@staff_member_required
def module_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            messages.success(request, 'Module created.')
            return redirect('manager:course_content', course_id=course.id)
    else:
        form = ModuleForm()
    return render(request, 'manager/module_form.html', {'form': form, 'course': course, 'title': 'Create Module'})

@staff_member_required
def module_update(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, 'Module updated.')
            return redirect('manager:course_content', course_id=module.course_id)
    else:
        form = ModuleForm(instance=module)
    return render(request, 'manager/module_form.html', {'form': form, 'course': module.course, 'title': 'Edit Module'})

@staff_member_required
def module_delete(request, pk):
    module = get_object_or_404(Module, pk=pk)
    course_id = module.course_id
    if request.method == 'POST':
        module.delete()
        messages.success(request, 'Module deleted.')
        return redirect('manager:course_content', course_id=course_id)
    return render(request, 'manager/confirm_delete.html', {'object': module, 'cancel_path': reverse('manager:course_content', kwargs={'course_id': course_id})})

@staff_member_required
def lesson_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        form.fields['module'].queryset = course.modules.all().order_by('order')
        if form.is_valid():
            form.save()
            messages.success(request, 'Lesson created.')
            return redirect('manager:course_content', course_id=course.id)
    else:
        form = LessonForm()
        form.fields['module'].queryset = course.modules.all().order_by('order')
    return render(request, 'manager/lesson_form.html', {'form': form, 'course': course, 'title': 'Create Lesson'})

@staff_member_required
def lesson_update(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    course = lesson.module.course
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        form.fields['module'].queryset = course.modules.all().order_by('order')
        if form.is_valid():
            form.save()
            messages.success(request, 'Lesson updated.')
            return redirect('manager:course_content', course_id=course.id)
    else:
        form = LessonForm(instance=lesson)
        form.fields['module'].queryset = course.modules.all().order_by('order')
    return render(request, 'manager/lesson_form.html', {'form': form, 'course': course, 'title': 'Edit Lesson'})

@staff_member_required
def lesson_delete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    course_id = lesson.module.course_id
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Lesson deleted.')
        return redirect('manager:course_content', course_id=course_id)
    return render(request, 'manager/confirm_delete.html', {'object': lesson, 'cancel_path': reverse('manager:course_content', kwargs={'course_id': course_id})})

@staff_member_required
def resource_create(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    if request.method == 'POST':
        form = LessonResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.lesson = lesson
            resource.save()
            messages.success(request, 'Resource added.')
            return redirect('manager:course_content', course_id=lesson.module.course_id)
    else:
        form = LessonResourceForm()
    return render(request, 'manager/resource_form.html', {'form': form, 'course': lesson.module.course, 'lesson': lesson, 'title': 'Add Resource'})

@staff_member_required
def resource_update(request, pk):
    resource = get_object_or_404(LessonResource, pk=pk)
    lesson = resource.lesson
    if request.method == 'POST':
        form = LessonResourceForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource updated.')
            return redirect('manager:course_content', course_id=lesson.module.course_id)
    else:
        form = LessonResourceForm(instance=resource)
    return render(request, 'manager/resource_form.html', {'form': form, 'course': lesson.module.course, 'lesson': lesson, 'title': 'Edit Resource'})

@staff_member_required
def resource_delete(request, pk):
    resource = get_object_or_404(LessonResource, pk=pk)
    course_id = resource.lesson.module.course_id
    if request.method == 'POST':
        resource.delete()
        messages.success(request, 'Resource deleted.')
        return redirect('manager:course_content', course_id=course_id)
    return render(request, 'manager/confirm_delete.html', {'object': resource, 'cancel_path': reverse('manager:course_content', kwargs={'course_id': course_id})})

# ================= EVENTS MODULE =================

@staff_member_required
def event_list(request):
    events = Event.objects.all().order_by('-date')
    return render(request, 'manager/events_list.html', {'events': events})

@staff_member_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event created successfully.')
            return redirect('manager:event_list')
    else:
        form = EventForm()
    return render(request, 'manager/event_form.html', {'form': form, 'title': 'Create Event'})

@staff_member_required
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully.')
            return redirect('manager:event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'manager/event_form.html', {'form': form, 'title': 'Edit Event', 'event': event})

@staff_member_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully.')
        return redirect('manager:event_list')
    return render(request, 'manager/confirm_delete.html', {'object': event, 'cancel_url': 'manager:event_list'})

# ================= CONTACT MESSAGES =================

@staff_member_required
def contact_messages(request):
    if request.method == 'POST':
        msg_id = request.POST.get('msg_id')
        action = request.POST.get('action')
        if msg_id and action in ('read', 'unread', 'delete'):
            msg = get_object_or_404(ContactMessage, id=msg_id)
            if action == 'delete':
                msg.delete()
                messages.success(request, 'Message deleted.')
            else:
                msg.is_read = (action == 'read')
                msg.save(update_fields=['is_read'])
        return redirect('manager:contact_messages')

    filter_status = request.GET.get('status', 'all')
    qs = ContactMessage.objects.all()
    if filter_status == 'unread':
        qs = qs.filter(is_read=False)
    elif filter_status == 'read':
        qs = qs.filter(is_read=True)

    unread_count = ContactMessage.objects.filter(is_read=False).count()
    return render(request, 'manager/contact_messages.html', {
        'contact_messages': qs,
        'unread_count': unread_count,
        'filter_status': filter_status,
    })

# ================= PLACEHOLDERS =================

@staff_member_required
def student_list(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        student_id = request.POST.get('student_id')
        if action == 'toggle_status' and student_id:
            student = get_object_or_404(User, id=student_id, is_staff=False, is_superuser=False)
            student.is_active = not student.is_active
            student.save()
            AuditLog.objects.create(
                actor=request.user,
                action="BLOCK_USER" if not student.is_active else "UNBLOCK_USER",
                ip_address=request.META.get('REMOTE_ADDR'),
                details=f"Updated status of student @{student.username} to {'Blocked' if not student.is_active else 'Active'}."
            )
            messages.success(request, f"Status of @{student.username} updated successfully.")
            return redirect('manager:student_list')
        elif action == 'delete_student' and student_id:
            student = get_object_or_404(User, id=student_id, is_staff=False, is_superuser=False)
            username = student.username
            student.delete()
            AuditLog.objects.create(
                actor=request.user,
                action="DELETE_USER",
                ip_address=request.META.get('REMOTE_ADDR'),
                details=f"Permanently deleted student account @{username}."
            )
            messages.success(request, f"Student account @{username} has been permanently deleted.")
            return redirect('manager:student_list')
            
    students = User.objects.select_related('profile').prefetch_related('enrollments').order_by('-is_superuser', '-is_staff', '-date_joined')
    
    total_students = sum(1 for s in students if not s.is_staff and not s.is_superuser)
    active_students = sum(1 for s in students if not s.is_staff and not s.is_superuser and s.is_active)
    total_admins = sum(1 for s in students if s.is_staff or s.is_superuser)
    
    context = {
        'students': students,
        'total_students': total_students,
        'active_students': active_students,
        'total_admins': total_admins,
    }
    return render(request, 'manager/students_list.html', context)

@staff_member_required
def enrollment_list(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'toggle_active':
            enrollment_id = request.POST.get('enrollment_id')
            enrollment = get_object_or_404(Enrollment, id=enrollment_id)
            enrollment.is_active = not enrollment.is_active
            enrollment.save()
            messages.success(request, "Enrollment status toggled successfully.")
            return redirect('manager:enrollment_list')
            
        elif action == 'delete_enrollment':
            enrollment_id = request.POST.get('enrollment_id')
            enrollment = get_object_or_404(Enrollment, id=enrollment_id)
            enrollment.delete()
            messages.success(request, "Enrollment deleted successfully.")
            return redirect('manager:enrollment_list')
            
        elif action == 'create_enrollment':
            student_id = request.POST.get('student_id')
            course_id = request.POST.get('course_id')
            student = get_object_or_404(User, id=student_id)
            course = get_object_or_404(Course, id=course_id)
            
            enrollment, created = Enrollment.objects.get_or_create(user=student, course=course)
            if created:
                messages.success(request, f"Enrolled {student.username} in {course.title} successfully.")
            else:
                messages.info(request, f"{student.username} is already enrolled in {course.title}.")
            return redirect('manager:enrollment_list')

    enrollments = Enrollment.objects.all().select_related('user', 'course__category').order_by('-enrolled_at')
    courses = Course.objects.all().order_by('title')
    students = User.objects.filter(is_staff=False, is_superuser=False).order_by('username')
    
    context = {
        'enrollments': enrollments,
        'courses': courses,
        'students': students,
    }
    return render(request, 'manager/enrollment_list.html', context)

@staff_member_required
def payment_list(request):
    enrollments = Enrollment.objects.all().select_related('user', 'course__category').order_by('-enrolled_at')
    total_revenue = sum(e.course.price for e in enrollments if e.is_active)
    total_commissions = AffiliateRecord.objects.filter(payout_status='Paid').aggregate(Sum('commission_earned'))['commission_earned__sum'] or 0
    net_profit = total_revenue - total_commissions
    
    context = {
        'title': 'Payments Ledger',
        'enrollments': enrollments,
        'total_revenue': total_revenue,
        'total_commissions': total_commissions,
        'net_profit': net_profit,
    }
    return render(request, 'manager/payment_list.html', context)

@staff_member_required
def settings_view(request):
    from core.models import SiteSetting
    setting, _ = SiteSetting.objects.get_or_create(id=1)
    if request.method == 'POST':
        setting.site_name = request.POST.get('site_name', 'Tapeflicker')
        setting.contact_email = request.POST.get('contact_email', 'support@tapeflicker.com')
        setting.maintenance_mode = request.POST.get('maintenance_mode') == 'on'
        setting.save()
        messages.success(request, "Global site settings updated successfully.")
        return redirect('manager:settings_view')
    
    context = {
        'title': 'System Settings',
        'setting': setting,
    }
    return render(request, 'manager/settings.html', context)

@staff_member_required
def audit_trail(request):
    logs = AuditLog.objects.all().select_related('actor').order_by('-timestamp')[:100]
    return render(request, 'manager/audit_trail.html', {'logs': logs})

@staff_member_required
def ticket_list(request):
    if request.method == 'POST':
        # Create a mock ticket for testing support centers easily
        from django.contrib.auth.models import User
        import random
        users = User.objects.filter(is_staff=False)
        if users.exists():
            user = random.choice(users)
            SupportTicket.objects.create(
                user=user,
                subject=request.POST.get('subject', 'Need help with labs'),
                category=request.POST.get('category', 'Technical'),
                priority=request.POST.get('priority', 'Medium')
            )
            messages.success(request, "New support ticket created.")
            return redirect('manager:ticket_list')

    tickets = SupportTicket.objects.all().select_related('user').order_by('-created_at')
    return render(request, 'manager/ticket_list.html', {'tickets': tickets})

@staff_member_required
def ticket_status_update(request, ticket_id):
    if request.method == 'POST':
        ticket = get_object_or_404(SupportTicket, id=ticket_id)
        status = request.POST.get('status')
        if status in ['Open', 'In Progress', 'Resolved', 'Closed']:
            ticket.status = status
            if status in ['Resolved', 'Closed']:
                ticket.resolved_at = timezone.now()
            ticket.save()
            messages.success(request, f"Ticket #{ticket.id} status updated to {status}.")
        return redirect('manager:ticket_list')
    return redirect('manager:ticket_list')

@staff_member_required
def chat_management(request):
    rooms = CourseChatRoom.objects.select_related('course').annotate(total_messages=Count('messages'))
    active_rooms = rooms.filter(is_archived=False).count()
    total_messages = ChatMessage.objects.filter(is_deleted=False).count()
    total_reports = ChatReport.objects.filter(resolved=False).count()
    context = {
        'rooms': rooms,
        'active_rooms': active_rooms,
        'total_messages': total_messages,
        'total_reports': total_reports,
    }
    return render(request, 'manager/chat_management.html', context)

@staff_member_required
def chat_room_management(request, room_id):
    room = get_object_or_404(CourseChatRoom, id=room_id)
    q = (request.GET.get('q') or '').strip()
    user_q = (request.GET.get('user') or '').strip()
    messages_qs = room.messages.select_related('user', 'reply_to').order_by('-created_at')
    if q:
        messages_qs = messages_qs.filter(content__icontains=q)
    if user_q:
        messages_qs = messages_qs.filter(user__username__icontains=user_q)
    participants = room.participants.select_related('user').order_by('-updated_at')[:200]
    logs = room.moderation_logs.select_related('actor', 'target_user', 'message').order_by('-created_at')[:100]
    return render(request, 'manager/chat_room_management.html', {
        'room': room,
        'messages': messages_qs[:400],
        'participants': participants,
        'logs': logs,
        'q': q,
        'user_q': user_q,
    })

def _log_mod_action(room, actor, action, target_user=None, message=None, details=''):
    ChatModerationLog.objects.create(
        room=room,
        actor=actor,
        action=action,
        target_user=target_user,
        message=message,
        details=details,
    )

def _broadcast_room_event(room_id, payload):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(f"course_chat_{room_id if isinstance(room_id, int) else room_id}", payload)

@staff_member_required
def chat_delete_message(request, message_id):
    msg = get_object_or_404(ChatMessage, id=message_id)
    msg.is_deleted = True
    msg.content = ''
    msg.attachment = None
    msg.save(update_fields=['is_deleted', 'content', 'attachment', 'updated_at'])
    _log_mod_action(msg.room, request.user, 'delete_message', target_user=msg.user, message=msg)
    _broadcast_room_event(msg.room.course_id, {"type": "message.deleted", "message_id": msg.id})
    messages.success(request, 'Message deleted.')
    return redirect('manager:chat_room_management', room_id=msg.room_id)

@staff_member_required
def chat_toggle_pin_message(request, message_id):
    msg = get_object_or_404(ChatMessage, id=message_id)
    msg.is_pinned = not msg.is_pinned
    msg.save(update_fields=['is_pinned', 'updated_at'])
    _log_mod_action(msg.room, request.user, 'toggle_pin', target_user=msg.user, message=msg, details=f'pinned={msg.is_pinned}')
    _broadcast_room_event(msg.room.course_id, {"type": "message.updated", "message": {
        "id": msg.id, "content": msg.content, "is_pinned": msg.is_pinned, "is_announcement": msg.is_announcement,
        "is_edited": msg.is_edited, "is_deleted": msg.is_deleted, "reply_to": msg.reply_to_id,
        "user_id": msg.user_id, "username": msg.user.username, "avatar": getattr(getattr(msg.user, "profile", None), "avatar_url", ""),
        "created_at": msg.created_at.isoformat(), "updated_at": msg.updated_at.isoformat()
    }})
    return redirect('manager:chat_room_management', room_id=msg.room_id)

@staff_member_required
def chat_toggle_announcement(request, message_id):
    msg = get_object_or_404(ChatMessage, id=message_id)
    msg.is_announcement = not msg.is_announcement
    msg.save(update_fields=['is_announcement', 'updated_at'])
    _log_mod_action(msg.room, request.user, 'toggle_announcement', target_user=msg.user, message=msg, details=f'announcement={msg.is_announcement}')
    _broadcast_room_event(msg.room.course_id, {"type": "message.updated", "message": {
        "id": msg.id, "content": msg.content, "is_pinned": msg.is_pinned, "is_announcement": msg.is_announcement,
        "is_edited": msg.is_edited, "is_deleted": msg.is_deleted, "reply_to": msg.reply_to_id,
        "user_id": msg.user_id, "username": msg.user.username, "avatar": getattr(getattr(msg.user, "profile", None), "avatar_url", ""),
        "created_at": msg.created_at.isoformat(), "updated_at": msg.updated_at.isoformat()
    }})
    return redirect('manager:chat_room_management', room_id=msg.room_id)

@staff_member_required
def chat_mute_user(request, state_id):
    st = get_object_or_404(ChatParticipantState, id=state_id)
    if st.muted_until and st.muted_until > timezone.now():
        st.muted_until = None
    else:
        st.muted_until = timezone.now() + timezone.timedelta(hours=12)
    st.save(update_fields=['muted_until', 'updated_at'])
    _log_mod_action(st.room, request.user, 'mute_toggle', target_user=st.user, details=str(st.muted_until))
    return redirect('manager:chat_room_management', room_id=st.room_id)

@staff_member_required
def chat_ban_user(request, state_id):
    st = get_object_or_404(ChatParticipantState, id=state_id)
    st.is_banned = not st.is_banned
    st.save(update_fields=['is_banned', 'updated_at'])
    _log_mod_action(st.room, request.user, 'ban_toggle', target_user=st.user, details=f'banned={st.is_banned}')
    return redirect('manager:chat_room_management', room_id=st.room_id)

@staff_member_required
def chat_toggle_lock(request, room_id):
    room = get_object_or_404(CourseChatRoom, id=room_id)
    room.is_locked = not room.is_locked
    room.save(update_fields=['is_locked'])
    _log_mod_action(room, request.user, 'room_lock_toggle', details=f'locked={room.is_locked}')
    return redirect('manager:chat_room_management', room_id=room.id)

@staff_member_required
def chat_toggle_readonly(request, room_id):
    room = get_object_or_404(CourseChatRoom, id=room_id)
    room.read_only = not room.read_only
    room.save(update_fields=['read_only'])
    _log_mod_action(room, request.user, 'room_readonly_toggle', details=f'read_only={room.read_only}')
    return redirect('manager:chat_room_management', room_id=room.id)

@staff_member_required
def chat_toggle_archive(request, room_id):
    room = get_object_or_404(CourseChatRoom, id=room_id)
    room.is_archived = not room.is_archived
    room.save(update_fields=['is_archived'])
    _log_mod_action(room, request.user, 'room_archive_toggle', details=f'archived={room.is_archived}')
    return redirect('manager:chat_management')

@staff_member_required
def chat_reports(request):
    reports = ChatReport.objects.select_related('message', 'reporter', 'message__room', 'message__user').order_by('-created_at')
    return render(request, 'manager/chat_reports.html', {'reports': reports})
