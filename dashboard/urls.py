from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('settings/', views.settings_view, name='settings'),
    path('certificates/', views.empty_state_view, {'title': 'Certificates'}, name='certificates'),
    path('analytics/', views.empty_state_view, {'title': 'Analytics'}, name='analytics'),
]
