from django.db import models

class Event(models.Model):
    EVENT_TYPES = [
        ('Webinar', 'Webinar'),
        ('Workshop', 'Live Workshop'),
        ('Bootcamp', 'Bootcamp'),
        ('Hackathon', 'Hackathon'),
        ('AMA Session', 'AMA Session'),
        ('AI Session', 'AI Session'),
        ('Cybersecurity Lab', 'Cybersecurity Live Lab')
    ]
    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, default='Webinar')
    instructor = models.CharField(max_length=150, default="Tapeflicker Expert")
    description = models.TextField()
    highlights = models.TextField(blank=True, null=True, help_text="One per line")
    requirements = models.TextField(blank=True, null=True, help_text="One per line")
    date = models.DateTimeField()
    registration_link = models.URLField(blank=True, null=True, help_text="Optional: If blank, falls back to WhatsApp")
    banner = models.ImageField(upload_to='event_banners/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Testimonial(models.Model):
    student_name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    content = models.TextField()
    avatar = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.role}"

class SiteSetting(models.Model):
    site_name = models.CharField(max_length=100, default="Tapeflicker")
    contact_email = models.EmailField(default="support@tapeflicker.com")
    maintenance_mode = models.BooleanField(default=False)
    
    def __str__(self):
        return "Global Site Settings"

class HeroSection(models.Model):
    badge_text = models.CharField(max_length=100, default="Welcome to the Future of Learning")
    title_line_1 = models.CharField(max_length=100, default="Master Future")
    title_line_2_gradient = models.CharField(max_length=100, default="Tech Skills")
    subtitle = models.TextField(default="Affordable, premium-quality courses in cybersecurity, AI, development, and modern technology. Built for the ambitious.")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "Hero Section Config"

class Stat(models.Model):
    number = models.IntegerField(default=0)
    suffix = models.CharField(max_length=10, blank=True)
    label = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    color_class = models.CharField(max_length=50, default="text-accent-neon", help_text="e.g. text-accent-neon, text-accent-purple, text-accent-cyan")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.label

class AboutPage(models.Model):
    title = models.CharField(max_length=200, default="About Tapeflicker")
    description = models.TextField(default="We believe that high-quality tech education shouldn't cost a fortune. Tapeflicker is built by developers, for future developers and cybersecurity experts.")
    mission_title = models.CharField(max_length=100, default="Our Mission")
    mission_text = models.TextField(default="To democratize access to premium tech education through affordable, high-quality courses.")
    vision_title = models.CharField(max_length=100, default="Our Vision")
    vision_text = models.TextField(default="A world where anyone with ambition can learn the skills needed to build the future.")
    values_title = models.CharField(max_length=100, default="Our Values")
    values_text = models.TextField(default="Quality over quantity. Student success above all. Continuous innovation in learning.")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "About Page Content"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{'READ' if self.is_read else 'NEW'}] {self.subject} — {self.name}"

    class Meta:
        ordering = ['-submitted_at']
