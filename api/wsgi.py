"""
Vercel WSGI handler - entry point for Vercel deployment
"""
import os
import sys
from pathlib import Path

# Add project directory to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_judge_project.settings')

# Configure Django
import django
django.setup()

# Import WSGI application
from online_judge_project.wsgi import application

# Vercel expects 'app' as the WSGI application
app = application
