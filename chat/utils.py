from accounts.models import UserProfile


def user_chat_role(user):
    if not user.is_authenticated:
        return "guest"
    if user.is_superuser or user.is_staff:
        return "admin"
    profile = getattr(user, 'profile', None)
    if not profile:
        return "student"
    role = (profile.role or "Student").lower()
    if role == "admin":
        return "admin"
    if role == "instructor":
        return "instructor"
    if role == "moderator":
        return "moderator"
    return "student"


def can_moderate_chat(user):
    return user_chat_role(user) in {"admin", "instructor", "moderator"}
