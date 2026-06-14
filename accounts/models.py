from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    firebase_uid = models.CharField(max_length=128, unique=True)
    role = models.CharField(max_length=20, choices=[('Student', 'Student'), ('Instructor', 'Instructor'), ('Moderator', 'Moderator'), ('Admin', 'Admin')], default='Student')
    avatar_url = models.URLField(blank=True, null=True)
    
    last_active_date = models.DateField(blank=True, null=True)
    current_streak = models.IntegerField(default=0)
    
    # Gamification Fields
    xp = models.IntegerField(default=150) # Starting XP
    level = models.IntegerField(default=1)
    learning_rank = models.CharField(max_length=50, default='Novice')
    current_goal = models.CharField(max_length=100, default='Daily Cybersecurity Lesson')

    def get_xp_percentage(self):
        # Assumes 1000 XP per level
        return int((self.xp % 1000) / 10)

    def get_xp_progress(self):
        return self.xp % 1000

    def get_recent_badges(self):
        badges = []
        if self.user.enrollments.exists():
            badges.append({
                'name': 'First Step',
                'description': 'Enrolled in first course',
                'icon': '🚀',
                'color': 'text-blue-400 bg-blue-500/10'
            })
        if self.current_streak >= 3:
            badges.append({
                'name': 'Streak Starter',
                'description': 'Maintained a 3-day streak',
                'icon': '🔥',
                'color': 'text-orange-400 bg-orange-500/10'
            })
        if self.user.enrollments.filter(progress=100).exists():
            badges.append({
                'name': 'Graduate',
                'description': 'Completed at least one course',
                'icon': '🎓',
                'color': 'text-green-400 bg-green-500/10'
            })
        if self.xp >= 500:
            badges.append({
                'name': 'Elite Scout',
                'description': 'Reached 500+ XP',
                'icon': '🛡️',
                'color': 'text-purple-400 bg-purple-500/10'
            })
        # Default fallback
        if not badges:
            badges.append({
                'name': 'Scout Init',
                'description': 'Joined Tapeflicker community',
                'icon': '👶',
                'color': 'text-maindim bg-white/5'
            })
        return badges

    def get_initials(self):
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name[0]}{self.user.last_name[0]}".upper()
        elif self.user.first_name:
            return self.user.first_name[0].upper()
        elif self.user.username:
            return self.user.username[0].upper()
        return "U"

    def __str__(self):
        return f"{self.user.username} ({self.role})"
