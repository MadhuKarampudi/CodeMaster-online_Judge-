#!/usr/bin/env python
"""
Vercel Deployment Helper Script
Generates configuration values needed for Vercel deployment
"""

import os
import sys
from pathlib import Path

def generate_secret_key():
    """Generate a secure Django secret key"""
    try:
        from django.core.management.utils import get_random_secret_key
        return get_random_secret_key()
    except ImportError:
        # Fallback if Django not yet installed
        import secrets
        import string
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(chars) for _ in range(50))

def create_env_template():
    """Create a .env.vercel template with instructions"""
    secret_key = generate_secret_key()
    
    template = f"""# ================================================
# VERCEL DEPLOYMENT ENVIRONMENT VARIABLES
# ================================================
# Copy these values to Vercel Dashboard:
# Settings → Environment Variables → Add

# 1. SECRET KEY (generated)
DJANGO_SECRET_KEY={secret_key}

# 2. DEBUG MODE (set to False for production)
DEBUG=False

# 3. DATABASE URL (from Neon.tech)
# Get from: https://neon.tech → Project → Connection String
# Format: postgresql://user:password@host:5432/dbname
DATABASE_URL=postgresql://user:password@host:5432/dbname

# 4. JUDGE0 API KEY (from RapidAPI)
# Get from: https://rapidapi.com/judge0-api/api/judge0-ce
# Dashboard → X-RapidAPI-Key
JUDGE0_API_KEY=your-judge0-api-key-here

# 5. ALLOWED HOSTS (your Vercel domain)
# Replace 'myproject' with your actual Vercel project name
ALLOWED_HOSTS=myproject.vercel.app,localhost

# 6. DOCKER EXECUTION (disabled for Vercel)
USE_DOCKER=False

# ================================================
# INSTRUCTIONS FOR GETTING EACH VALUE:
# ================================================

# DJANGO_SECRET_KEY: ✅ Already generated above!

# DATABASE_URL:
#   1. Go to https://neon.tech
#   2. Create account → Create Project
#   3. Choose PostgreSQL 13 or higher
#   4. Copy Connection String (includes password)
#   5. Paste here as DATABASE_URL

# JUDGE0_API_KEY:
#   1. Go to https://rapidapi.com/judge0-api/api/judge0-ce
#   2. Click "Subscribe to Test" (free tier)
#   3. Go to Dashboard
#   4. Copy "X-RapidAPI-Key"
#   5. Paste here

# ALLOWED_HOSTS:
#   - After Vercel deployment, you'll see your domain
#   - It will be: https://YOUR-PROJECT-NAME.vercel.app
#   - Use format: myproject.vercel.app (without https://)

# ================================================
"""
    
    return template

def main():
    print("=" * 60)
    print("CODEMASTER ONLINE JUDGE - VERCEL DEPLOYMENT SETUP")
    print("=" * 60)
    print()
    
    # Generate environment template
    env_template = create_env_template()
    
    # Save to file
    env_file = Path(__file__).parent / '.env.vercel'
    with open(env_file, 'w') as f:
        f.write(env_template)
    
    print(f"✅ Created {env_file}")
    print()
    print("DJANGO_SECRET_KEY generated! Copy from .env.vercel file")
    print()
    print("=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print()
    print("1. Get DATABASE_URL from Neon.tech:")
    print("   → https://neon.tech")
    print("   → Create Project → Copy Connection String")
    print()
    print("2. Get JUDGE0_API_KEY from RapidAPI:")
    print("   → https://rapidapi.com/judge0-api/api/judge0-ce")
    print("   → Subscribe → Copy X-RapidAPI-Key")
    print()
    print("3. Update .env.vercel with your values:")
    print(f"   See: {env_file}")
    print()
    print("4. Push to GitHub:")
    print("   git add .")
    print("   git commit -m 'Add Vercel deployment configuration'")
    print("   git push origin main")
    print()
    print("5. Deploy to Vercel:")
    print("   → https://vercel.com/dashboard")
    print("   → Import Git Repository → Select your repo")
    print("   → Add Environment Variables from .env.vercel")
    print("   → Deploy!")
    print()
    print("=" * 60)
    print(f"Configuration saved to: {env_file}")
    print("=" * 60)

if __name__ == '__main__':
    main()
