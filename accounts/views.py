from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from tapeflicker_proj.decorators import ratelimit
import json
import firebase_admin
from firebase_admin import auth
from django.contrib.auth.models import User
from .models import UserProfile
import os

# Ensure Firebase is initialized
import config.firebase

@ensure_csrf_cookie
@ratelimit('login', limit=5, period=60)
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid username or password'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return render(request, 'accounts/login.html')

@ensure_csrf_cookie
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return render(request, 'accounts/signup.html')

def logout_view(request):
    logout(request)
    return redirect('core:home')

@ratelimit('login', limit=5, period=60)
def verify_firebase_token(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id_token = data.get('idToken')
            
            if not id_token:
                return JsonResponse({'status': 'error', 'message': 'No token provided'}, status=400)
            
            # Verify token with Firebase Admin
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            email = decoded_token.get('email', '')
            name = decoded_token.get('name', email.split('@')[0])
            picture = decoded_token.get('picture', '')

            # Create or get user
            try:
                user_profile = UserProfile.objects.get(firebase_uid=uid)
                user = user_profile.user
            except UserProfile.DoesNotExist:
                # User doesn't exist, create Django user
                first_name = name.split(' ')[0] if ' ' in name else name
                last_name = name.split(' ', 1)[1] if ' ' in name else ''
                user, created = User.objects.get_or_create(username=uid, defaults={'email': email, 'first_name': first_name, 'last_name': last_name})
                user_profile = UserProfile.objects.create(user=user, firebase_uid=uid, avatar_url=picture)
            
            # Update streak and last active date
            from datetime import date, timedelta
            today = date.today()
            if user_profile.last_active_date != today:
                if user_profile.last_active_date == today - timedelta(days=1):
                    user_profile.current_streak += 1
                else:
                    user_profile.current_streak = 1
                user_profile.last_active_date = today
                user_profile.save()

            # Log the user in to Django session
            login(request, user)
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=401)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
