from django.urls import path
from . import views

app_name = 'manager'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Courses
    path('courses/', views.course_list, name='course_list'),
    path('courses/new/', views.course_create, name='course_create'),
    path('courses/<int:pk>/edit/', views.course_update, name='course_update'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course_delete'),
    path('courses/<int:course_id>/content/', views.course_content, name='course_content'),
    path('courses/<int:course_id>/modules/new/', views.module_create, name='module_create'),
    path('modules/<int:pk>/edit/', views.module_update, name='module_update'),
    path('modules/<int:pk>/delete/', views.module_delete, name='module_delete'),
    path('courses/<int:course_id>/lessons/new/', views.lesson_create, name='lesson_create'),
    path('lessons/<int:pk>/edit/', views.lesson_update, name='lesson_update'),
    path('lessons/<int:pk>/delete/', views.lesson_delete, name='lesson_delete'),
    path('lessons/<int:lesson_id>/resources/new/', views.resource_create, name='resource_create'),
    path('resources/<int:pk>/edit/', views.resource_update, name='resource_update'),
    path('resources/<int:pk>/delete/', views.resource_delete, name='resource_delete'),
    
    # Events
    path('events/', views.event_list, name='event_list'),
    path('events/new/', views.event_create, name='event_create'),
    path('events/<int:pk>/edit/', views.event_update, name='event_update'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),
    
    # Students
    path('students/', views.student_list, name='student_list'),
    
    # Enrollments
    path('enrollments/', views.enrollment_list, name='enrollment_list'),
    
    # Payments
    path('payments/', views.payment_list, name='payment_list'),
    
    # Settings
    path('settings/', views.settings_view, name='settings_view'),
    path('audit-trail/', views.audit_trail, name='audit_trail'),
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/<int:ticket_id>/status/', views.ticket_status_update, name='ticket_status_update'),

    # Contact Messages
    path('messages/', views.contact_messages, name='contact_messages'),

    # Chat management
    path('chat/', views.chat_management, name='chat_management'),
    path('chat/room/<int:room_id>/', views.chat_room_management, name='chat_room_management'),
    path('chat/message/<int:message_id>/delete/', views.chat_delete_message, name='chat_delete_message'),
    path('chat/message/<int:message_id>/pin/', views.chat_toggle_pin_message, name='chat_toggle_pin_message'),
    path('chat/message/<int:message_id>/announce/', views.chat_toggle_announcement, name='chat_toggle_announcement'),
    path('chat/participant/<int:state_id>/mute/', views.chat_mute_user, name='chat_mute_user'),
    path('chat/participant/<int:state_id>/ban/', views.chat_ban_user, name='chat_ban_user'),
    path('chat/room/<int:room_id>/toggle-lock/', views.chat_toggle_lock, name='chat_toggle_lock'),
    path('chat/room/<int:room_id>/toggle-readonly/', views.chat_toggle_readonly, name='chat_toggle_readonly'),
    path('chat/room/<int:room_id>/toggle-archive/', views.chat_toggle_archive, name='chat_toggle_archive'),
    path('chat/reports/', views.chat_reports, name='chat_reports'),
]
