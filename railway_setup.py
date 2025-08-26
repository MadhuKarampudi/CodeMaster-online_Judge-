#!/usr/bin/env python
"""
Railway deployment setup script
Run this to initialize the database and create superuser
"""
import os
import django
import sys

# Add the project directory to Python path
sys.path.append('/app')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_judge_project.settings')

# Setup Django
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model

def setup_database():
    """Run migrations and create superuser"""
    print("Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("Creating superuser...")
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print("Superuser created: admin/admin123")
    else:
        print("Superuser already exists")

if __name__ == '__main__':
    setup_database()
