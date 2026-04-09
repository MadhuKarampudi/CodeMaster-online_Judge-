# 🚀 Vercel Deployment Guide - CodeMaster Online Judge

## Prerequisites

1. **Vercel Account** - Sign up at https://vercel.com
2. **Judge0 API Key** - Get from https://rapidapi.com/judge0-api/api/judge0-ce
3. **PostgreSQL Database** - Use Neon (https://neon.tech) or similar
4. **GitHub Repository** - Push your code to GitHub

## Step 1: Set Up External Database (Neon)

1. Go to https://neon.tech and create an account
2. Create a new project:
   - Region: Choose closest to you
   - PostgreSQL version: 15
3. Copy the connection string (will look like: `postgresql://user:password@host/dbname`)

## Step 2: Get Judge0 API Key

1. Go to https://rapidapi.com/judge0-api/api/judge0-ce
2. Click "Subscribe to Test"
3. Copy your "X-RapidAPI-Key" from the dashboard
4. Keep this secret - don't commit it to GitHub!

## Step 3: Push Code to GitHub

```bash
cd CodeMaster-online_Judge-

# Add Vercel files to git
git add vercel.json api/ .vercelignore submissions/judge0_executor.py
git commit -m "Add Vercel deployment configuration"
git push origin main
```

## Step 4: Deploy to Vercel

### Option A: Using Vercel Dashboard (Easiest)

1. Go to https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Select your CodeMaster project
5. Click "Import"
6. Configure environment variables in Project Settings → Environment Variables:

```
DJANGO_SECRET_KEY = <your-secret-key>
DEBUG = False
DATABASE_URL = postgresql://user:password@host/dbname
JUDGE0_API_KEY = <your-judge0-api-key>
ALLOWED_HOSTS = your-domain.vercel.app,localhost
USE_DOCKER = False
```

7. Click "Deploy"

### Option B: Using Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
cd CodeMaster-online_Judge-
vercel env add DJANGO_SECRET_KEY
vercel env add DATABASE_URL
vercel env add JUDGE0_API_KEY
vercel env add DEBUG

vercel deploy --prod
```

## Step 5: Configure Environment Variables in Vercel

In your Vercel dashboard, go to Settings → Environment Variables and add:

| Variable | Value | Example |
|----------|-------|---------|
| `DJANGO_SECRET_KEY` | Generate secure key | `django-insecure-a1b2c3d4...` |
| `DEBUG` | False | `False` |
| `DATABASE_URL` | Your Neon DB URL | `postgresql://user:pass@host/db` |
| `JUDGE0_API_KEY` | Your RapidAPI key | `xxxx-xxxx-xxxx-xxxx` |
| `ALLOWED_HOSTS` | Your Vercel domain | `codemaster.vercel.app,localhost` |
| `USE_DOCKER` | False | `False` |

## Step 6: Run Initial Migrations

After deployment, run migrations on your database:

```bash
# Option A: Using Vercel CLI
vercel env pull .env.production.local
export $(cat .env.production.local | xargs) && python manage.py migrate

# Option B: Manual
export DATABASE_URL="your-neon-connection-string"
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

## Step 7: Test Your Deployment

1. Go to your Vercel deployment URL: `https://your-project.vercel.app`
2. Test user login with credentials you created
3. Try submitting code - it should execute via Judge0 API

## Troubleshooting

### "Database connection failed"
- Check DATABASE_URL in Vercel settings
- Ensure Neon database is running
- Test connection locally: `psql $DATABASE_URL`

### "Judge0 submission failed"
- Verify JUDGE0_API_KEY is correct
- Check RapidAPI quota hasn't been exceeded
- Ensure your code syntax is valid

### "404 Not Found" on main page
- Check ALLOWED_HOSTS includes your Vercel domain
- Run: `python manage.py collectstatic --noinput`

### "Static files not loading"
- Vercel should handle this via WhiteNoise
- If issues persist, check STATIC_ROOT and settings.py

## Performance Notes

⚠️ **Vercel Limitations:**
- Free tier: 10 seconds execution timeout per request
- Pro tier: 60 seconds execution timeout per request
- Code execution delegated to Judge0 API (separate service)
- Database queries should be optimized

## Scaling Options

If you outgrow Vercel:

1. **Railway** (Already configured) - Better for Django apps
2. **Heroku** - Full Docker support
3. **AWS ECS** - Enterprise-grade
4. **Google Cloud Run** - Similar to Vercel, better performance

## Monitoring

- Check Vercel Analytics at: https://vercel.com/dashboard
- Monitor database with Neon console: https://neon.tech
- View Judge0 usage: https://rapidapi.com/user/profile

## Next Steps

1. ✅ Set up Vercel project
2. ✅ Configure database
3. ✅ Get Judge0 API key
4. ✅ Deploy to Vercel
5. ✅ Run migrations
6. 📊 Add monitoring (Sentry, LogRocket)
7. 🔐 Enable SSL/HTTPS (automatic)
8. 📱 Test on mobile devices

## Support

For issues:
- **Vercel Docs**: https://vercel.com/docs
- **Django Docs**: https://djangoproject.com/
- **Judge0 API**: https://rapidapi.com/judge0-api/api/judge0-ce
- **Neon Docs**: https://neon.tech/docs
