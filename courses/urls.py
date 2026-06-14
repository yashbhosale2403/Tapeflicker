from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='list'),
    path('<int:course_id>/', views.course_detail, name='detail'),
    path('<int:course_id>/enroll/free/', views.enroll_free_course, name='enroll_free'),
    path('lesson/<int:lesson_id>/', views.lesson_player, name='lesson_player'),
    path('api/complete-lesson/<int:lesson_id>/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('api/track-lesson/<int:lesson_id>/', views.track_lesson_progress, name='track_lesson_progress'),
]
