from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:id>/', views.event_detail, name='event_detail'),
]
