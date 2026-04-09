# ========================================
# VERCEL DEPLOYMENT - QUICK START GUIDE
# ========================================

## 1. GENERATE DJANGO SECRET KEY

Run this command in your terminal to generate a secure key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Save this value - you'll need it for Vercel.

## 2. SET UP EXTERNAL DATABASE (Neon.tech)

1. Visit: https://neon.tech
2. Create free account
3. Create new project (PostgreSQL 15)
4. Copy connection string: postgresql://user:password@host/dbname
5. Save this - you'll need it for `DATABASE_URL`

## 3. GET JUDGE0 API KEY

1. Visit: https://rapidapi.com/judge0-api/api/judge0-ce
2. Click "Subscribe to Test" (free tier)
3. Go to Dashboard
4. Copy "X-RapidAPI-Key"
5. Save this - you'll need it for `JUDGE0_API_KEY`

## 4. PUSH CODE TO GITHUB

```bash
cd CodeMaster-online_Judge-

# Stage all files
git add .

# Commit changes
git commit -m "Add Vercel deployment configuration with Judge0"

# Push to GitHub
git push origin main
```

## 5. DEPLOY TO VERCEL

### Method A: Vercel Dashboard (Easiest)

1. Go to https://vercel.com/dashboard
2. Click "Add New" → "Project"
3. Select "Import Git Repository"
4. Find "CodeMaster-online_Judge-" repository
5. Click "Import"
6. In "Configure Project":
   - **Framework Preset:** Choose "Other" (Django is not listed)
   - Click "Continue"

7. Configure Environment Variables (Settings → Environment Variables):
   ```
   DJANGO_SECRET_KEY = <your-generated-secret-key>
   DEBUG = False
   DATABASE_URL = <your-neon-connection-string>
   JUDGE0_API_KEY = <your-rapidapi-key>
   ALLOWED_HOSTS = <project-name>.vercel.app,localhost
   USE_DOCKER = False
   ```

8. Click "Deploy"

### Method B: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
cd CodeMaster-online_Judge-
vercel deploy --prod

# When prompted, add environment variables
```

## 6. RUN INITIAL MIGRATIONS

After deployment succeeds:

```bash
# Option 1: Using Vercel env
vercel env pull .env.production.local
export $(cat .env.production.local)

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Option 2: Using exported DATABASE_URL
export DATABASE_URL="postgresql://..."
python manage.py migrate
python manage.py createsuperuser
```

## 7. VERIFY DEPLOYMENT

1. Visit your Vercel app: https://<project-name>.vercel.app
2. Try logging in
3. Try creating a submission to test code execution

## ENVIRONMENT VARIABLES REFERENCE

| Variable | Required | Where to Get | Example |
|----------|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | ✅ | `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` | `django-insecure-abc123...` |
| `DEBUG` | ✅ | Set this | `False` |
| `DATABASE_URL` | ✅ | Neon.tech dashboard | `postgresql://user:pass@host/db` |
| `JUDGE0_API_KEY` | ✅ | RapidAPI dashboard | `xxxx-xxxx-xxxx-xxxx` |
| `ALLOWED_HOSTS` | ✅ | Your Vercel domain | `myproject.vercel.app` |
| `USE_DOCKER` | ❌ | Leave as | `False` |

## EXPECTED FILE STRUCTURE

After deployment, Vercel should find:
```
CodeMaster-online_Judge-/
├── vercel.json          ✅ (Vercel config)
├── api/
│   ├── wsgi.py         ✅ (Entry point)
│   └── __init__.py
├── manage.py
├── online_judge_project/
├── submissions/
│   ├── judge.py        ✅ (Updated)
│   └── judge0_executor.py ✅ (Judge0 integration)
├── problems/
├── users/
└── requirements.txt    ✅ (Dependencies)
```

## TROUBLESHOOTING

### Build Fails with "ModuleNotFoundError"
- Check requirements.txt is in root directory
- Ensure all dependencies are listed
- Try: `pip freeze > requirements.txt`

### Database Connection Error
- Verify DATABASE_URL format: `postgresql://user:password@host:5432/dbname`
- Test locally: `psql $DATABASE_URL`
- Check Neon dashboard for active connections

### Judge0 Errors
- Verify JUDGE0_API_KEY is correct (copy exactly from RapidAPI)
- Check RapidAPI quota hasn't been exceeded
- Test with simple Python code first

### Static Files Not Loading
- Run: `python manage.py collectstatic --noinput`
- WhiteNoise should handle this automatically
- Check STATIC_URL and STATIC_ROOT in settings.py

### 500 Error on Deployment
- Check Vercel logs:  `vercel logs` in terminal
- Run migrations: `python manage.py migrate`
- Check SECRET_KEY is set correctly

## ROLLBACK TO RAILWAY

If Vercel isn't working:
1. Your Railway deployment is still active
2. No need to redeploy - just use Railway URL
3. Update DNS/bookmarks to use Railway
4. Railway URL: https://codemaster-onlinejudge-production.up.railway.app

## NEXT STEPS

- 📊 Set up monitoring (Sentry, LogRocket)
- 🔐 Enable custom domain via Vercel
- 📱 Test on mobile devices
- ⚡ Monitor API execution times
- 🚀 Optimize database queries

---

**Need Help?**
- Vercel Docs: https://vercel.com/docs
- Django Docs: https://docs.djangoproject.com
- Judge0 API: https://rapidapi.com/judge0-api/api/judge0-ce
- Neon Docs: https://neon.tech/docs
