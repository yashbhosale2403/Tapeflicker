from .models import Announcement, ContactMessage

def active_announcements(request):
    """Context processor to pass active announcements to all templates."""
    announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')
    unread_contact_count = ContactMessage.objects.filter(is_read=False).count()
    return {
        'active_announcements': announcements,
        'unread_contact_count': unread_contact_count,
    }
