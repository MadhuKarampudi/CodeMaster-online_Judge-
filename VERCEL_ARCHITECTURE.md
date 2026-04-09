# CodeMaster Online Judge - Vercel Deployment Architecture

## Overview

Your Django Online Judge application has been configured to deploy on **Vercel** using **Judge0 API** for code execution instead of Docker.

## Why Judge0 API?

**Problem:** Vercel is serverless with strict timeouts (10-60 seconds)
**Solution:** Delegate code execution to Judge0 API (external service)

| Feature | Vercel | Judge0 |
|---------|--------|--------|
| Code Execution | ❌ Timeout limits | ✅ Unlimited |
| Docker Support | ❌ No | ✅ Full |
| Code Languages | - | ✅ 90+ languages |
| Scalability | ✅ Auto-scale | ✅ Fast responses |
| Cost | ✅ Free tier | ✅ Free tier available |

## Architecture Diagram

```
┌─────────────────┐
│  User Browser   │
└────────┬────────┘
         │ HTTP Request
         ▼
┌─────────────────────────────────────┐
│  Vercel (Django Application)        │
│  ┌─────────────────────────────────┐│
│  │ API Endpoints                   ││
│  │ - User Auth (JWT)               ││
│  │ - Problem Management            ││
│  │ - Submission Handling           ││
│  └────────┬────────────────────────┘│
│           │ POST /submit            │
│           ▼                          │
│  ┌─────────────────────────────────┐│
│  │ Judge0 Executor                 ││
│  │ (submissions/judge0_executor.py)││
│  └────────┬────────────────────────┘│
└────────────┼──────────────────────────┘
             │ HTTP Request (Judge0 API)
             ▼
    ┌──────────────────┐
    │  Judge0 API      │  ← Executes code
    │ (RapidAPI)       │  ← Returns results
    │ judge0-ce.com    │
    └─────────────────┘
             │ Response
             ▼
        Vercel saves
        results to
        database (Neon)

┌─────────────────────────────────────┐
│  Neon PostgreSQL Database           │
│  - Users                            │
│  - Problems                         │
│  - Submissions & Results            │
│  - Test Cases                       │
└─────────────────────────────────────┘
```

## Execution Flow

### Submission Process

1. **User submits code** → Browser sends POST request to Vercel
2. **Vercel receives submission** → Validates input, saves to database
3. **Create Submission object** → Status = "Judging"
4. **Judge0Executor.judge()** → Loops through test cases
5. **For each test case:**
   - Encodes code in Base64
   - Sends to Judge0 API
   - Polls for result (max 10 sec)
   - Decodes response
6. **Save results** → Update Submission status, time, memory, output
7. **Update user stats** → Increment problems solved
8. **Return response** → User sees results

### Code Flow

**File:** `submissions/judge0_executor.py`

```python
class Judge0Executor:
    def judge(self):
        """Main judging function"""
        for test_case in test_cases:
            result = self._execute_test_case(test_case)
            if result['status'] != 'Accepted':
                return  # Stop on first failure
        # All passed!
    
    def _execute_test_case(self, test_case):
        """Execute single test case via Judge0"""
        # 1. Send code to Judge0
        response = requests.post(
            "judge0-ce.p.rapidapi.com/submissions",
            json=payload,  # Base64 encoded code
            headers=headers  # Include API key
        )
        
        # 2. Poll for result
        for attempt in range(20):  # 10 seconds max
            result = requests.get(
                f"judge0-ce.p.rapidapi.com/submissions/{id}"
            )
            if result is final:
                return self._parse_judge0_result(result)
        
        return timeout_error()
```

**File:** `submissions/judge.py` (Updated)

```python
def judge_submission(submission):
    """Auto-select judge based on environment"""
    if os.environ.get('JUDGE0_API_KEY'):
        # Vercel deployment
        judge = Judge0Executor(submission)
    else:
        # Railway deployment (Docker)
        judge = SecureCodeJudge(submission)
    
    judge.judge()
```

## Files Modified/Created

### ✅ Created Files

1. **`vercel.json`** - Vercel configuration
   - Build command: Runs migrations & collectstatic
   - Routes: API routing
   - Functions: Max duration 60 seconds

2. **`api/wsgi.py`** - Entry point for Vercel
   - Sets up Django
   - Exports WSGI application

3. **`submissions/judge0_executor.py`** - Judge0 integration
   - Executes code via Judge0 API
   - Handles test cases
   - Parses results

4. **`.vercelignore`** - Files to exclude from Vercel
   - Database files
   - Docker files
   - Node modules

5. **`setup_vercel.py`** - Setup helper script
   - Generates Django secret key
   - Creates `.env.vercel` template

6. **`VERCEL_DEPLOYMENT_GUIDE.md`** - Detailed guide
7. **`VERCEL_QUICK_START.md`** - Quick reference

### ✏️ Modified Files

1. **`online_judge_project/settings.py`**
   - Dynamic ALLOWED_HOSTS for Vercel domains
   - Dynamic CORS configuration
   - Support for .vercel.app domains

2. **`submissions/judge.py`**
   - Added automatic judge selection
   - Falls back to Docker if no Judge0 key
   - Better error handling

3. **`.env.example`**
   - Added JUDGE0_API_KEY variable
   - Organized by platform (Railway vs Vercel)

## Environment Variables

### Required for Vercel

```bash
DJANGO_SECRET_KEY        # Generated secret key
DEBUG=False              # Never True in production
DATABASE_URL             # From Neon.tech
JUDGE0_API_KEY          # From RapidAPI
ALLOWED_HOSTS           # Your Vercel domain
USE_DOCKER=False        # Disable Docker execution
```

### Optional

```bash
EMAIL_HOST              # For email notifications
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER
EMAIL_HOST_PASSWORD
CUSTOM_DOMAIN           # Your custom domain
```

## Judge0 Language Mapping

The `Judge0Executor` supports these languages:

```python
LANGUAGE_MAP = {
    'python': 71,      # Python 3.8.1
    'cpp': 54,         # C++ 17
    'c': 50,           # C 10
    'java': 62,        # Java 14
}
```

Judge0 supports 90+ additional languages if needed!

## Deployment Checklist

- [ ] Push code to GitHub
- [ ] Create Neon.tech account and database
- [ ] Get RapidAPI/Judge0 API key
- [ ] Go to vercel.com and import repository
- [ ] Add environment variables to Vercel
- [ ] Deploy
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Test submission (code should execute via Judge0)
- [ ] Verify results appear correctly

## Testing Judge0 Locally

To test Judge0 locally before Vercel deployment:

```bash
# Set environment variables
export JUDGE0_API_KEY="your-rapidapi-key"
export DEBUG=False

# Test with local database
python manage.py migrate

# Create a test submission (via Django shell)
python manage.py shell
>>> from submissions.models import Submission
>>> from submissions.judge0_executor import Judge0Executor
>>> submission = Submission.objects.first()
>>> judge = Judge0Executor(submission)
>>> judge.judge()
>>> submission.refresh_from_db()
>>> print(submission.status)  # Should show 'Accepted' or 'Wrong Answer'
```

## Limitations & Workarounds

### Issue: Judge0 Free Tier Rate Limiting
- **Limit:** 50 requests per day
- **Workaround:** Upgrade RapidAPI plan (pay-as-you-go)
- **Alternative:** Self-host Judge0 on your own server

### Issue: 10-second Vercel timeout for code execution
- **Solution:** Judge0 handles timing independently
- **Note:** Only request itself must complete in 10 sec
- **Best Practice:** Complex code should still finish quickly

### Issue: Code output very large (>1MB)
- **Limit:** Database storage limits
- **Workaround:** Truncate output in database
- **Solution:** Implemented in `judge0_executor.py`

## Performance Optimization

### Database Queries
```python
# Good: Prefetch related objects
Submission.objects.select_related('user', 'problem')

# Bad: N+1 queries
for submission in Submission.objects.all():
    print(submission.user.username)
```

### API Calls
```python
# Cache Judge0 results for 1 hour
from rest_framework.decorators import cache_page

@cache_page(60 * 60)
def get_problem(request, problem_id):
    ...
```

## Monitoring & Debugging

### Check Vercel Logs
```bash
vercel logs <project-name>
vercel logs <project-name> --follow
```

### Monitor Judge0 Usage
- Dashboard: https://rapidapi.com/dashboard
- Check remaining API calls

### Database Monitoring
- Neon console: https://neon.tech/console
- Query performance stats

## Comparison: Vercel vs Railway

| Feature | Vercel | Railway |
|---------|--------|---------|
| **Setup Time** | 5 minutes | 10 minutes |
| **Cost** | Free tier available | Free tier available |
| **Docker Support** | ❌ No | ✅ Yes |
| **Max Duration** | 60 sec (Pro) | 30 minutes |
| **Database** | External only | Included / External |
| **Scaling** | Auto | Manual |
| **Learning Curve** | Easy | Medium |
| **Recommended for** | APIs, Static sites | Full-stack Django apps |

## Next Steps

1. ✅ Configure all files (DONE)
2. ⏭️ Deploy to Vercel (push to GitHub)
3. ⏭️ Get Judge0 API key
4. ⏭️ Set up Neon database
5. ⏭️ Add environment variables to Vercel
6. ⏭️ Run migrations
7. ⏭️ Test code submissions

## Support & Resources

- **Vercel Docs:** https://vercel.com/docs
- **Django Docs:** https://docs.djangoproject.com/
- **Judge0 API:** https://rapidapi.com/judge0-api/api/judge0-ce
- **Neon DB:** https://neon.tech/docs/
- **Our Guides:** See `VERCEL_QUICK_START.md` and `VERCEL_DEPLOYMENT_GUIDE.md`

---

**Your app is ready for Vercel deployment!** 🚀
