import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tapeflicker_proj.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model

# 1. Run Migrations
print("Running database migrations...")
call_command('migrate', interactive=False)

# 2. Create Superuser if needed
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@tapeflicker.com')

if not password:
    print("DJANGO_SUPERUSER_PASSWORD environment variable not set. Skipping superuser creation.")
else:
    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser '{username}'...")
        User.objects.create_superuser(username, email, password)
        print("Superuser created successfully.")
    else:
        print(f"Superuser '{username}' already exists.")
