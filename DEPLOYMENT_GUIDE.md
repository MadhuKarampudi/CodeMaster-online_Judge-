# Online Judge Deployment Guide

This comprehensive guide covers deploying the Online Judge system in various environments, from development to production-ready deployments.

## Table of Contents

- [Development Deployment](#development-deployment)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Platform Deployment](#cloud-platform-deployment)
- [Security Configuration](#security-configuration)
- [Performance Optimization](#performance-optimization)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Troubleshooting](#troubleshooting)

## Development Deployment

### Local Development Setup

The development setup is designed for quick iteration and testing:

```bash
# 1. Clone and setup virtual environment
git clone <repository-url>
cd online_judge_project
python3.11 -m venv online_judge_env
source online_judge_env/bin/activate

# 2. Install dependencies
pip install django

# 3. Database setup
python manage.py makemigrations
python manage.py migrate

# 4. Create admin user
python manage.py createsuperuser

# 5. Load sample data (optional)
python manage.py shell
exec(open('load_sample_data.py').read())

# 6. Start development server
python manage.py runserver 0.0.0.0:8000
```

### Development Configuration

Key settings for development in `settings.py`:

```python
DEBUG = True
ALLOWED_HOSTS = ['*']

# Use SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Simple email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

## Production Deployment

### Prerequisites

Before deploying to production, ensure you have:

- A server with Python 3.11+ installed
- A production database (PostgreSQL recommended)
- A web server (Nginx recommended)
- SSL certificates for HTTPS
- Domain name configured

### Step 1: Server Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3.11 python3.11-venv python3-pip nginx postgresql postgresql-contrib

# Create application user
sudo useradd --system --shell /bin/bash --home /opt/onlinejudge onlinejudge
sudo mkdir -p /opt/onlinejudge
sudo chown onlinejudge:onlinejudge /opt/onlinejudge
```

### Step 2: Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE onlinejudge_db;
CREATE USER onlinejudge_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE onlinejudge_db TO onlinejudge_user;
\q
```

### Step 3: Application Deployment

```bash
# Switch to application user
sudo -u onlinejudge -i

# Clone and setup application
cd /opt/onlinejudge
git clone <repository-url> .
python3.11 -m venv venv
source venv/bin/activate

# Install production dependencies
pip install django psycopg2-binary gunicorn

# Configure environment variables
cat > .env << EOF
DEBUG=False
SECRET_KEY=your-very-secure-secret-key-here
DATABASE_URL=postgresql://onlinejudge_user:secure_password@localhost/onlinejudge_db
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
EOF

# Database migration
python manage.py migrate
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

### Step 4: Production Settings

Create `settings_production.py`:

```python
from .settings import *
import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = False
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'onlinejudge_db',
        'USER': 'onlinejudge_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static files
STATIC_ROOT = '/opt/onlinejudge/staticfiles'
MEDIA_ROOT = '/opt/onlinejudge/media'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.your-provider.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@domain.com'
EMAIL_HOST_PASSWORD = 'your-email-password'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/opt/onlinejudge/logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Step 5: Gunicorn Configuration

Create `/opt/onlinejudge/gunicorn.conf.py`:

```python
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
daemon = False
user = "onlinejudge"
group = "onlinejudge"
tmp_upload_dir = None
errorlog = "/opt/onlinejudge/logs/gunicorn_error.log"
accesslog = "/opt/onlinejudge/logs/gunicorn_access.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
```

### Step 6: Systemd Service

Create `/etc/systemd/system/onlinejudge.service`:

```ini
[Unit]
Description=Online Judge Gunicorn daemon
After=network.target

[Service]
User=onlinejudge
Group=onlinejudge
WorkingDirectory=/opt/onlinejudge
Environment="PATH=/opt/onlinejudge/venv/bin"
ExecStart=/opt/onlinejudge/venv/bin/gunicorn --config gunicorn.conf.py online_judge_project.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable onlinejudge
sudo systemctl start onlinejudge
sudo systemctl status onlinejudge
```

### Step 7: Nginx Configuration

Create `/etc/nginx/sites-available/onlinejudge`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias /opt/onlinejudge/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /opt/onlinejudge/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/onlinejudge /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Docker Deployment

### Dockerfile

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
        g++ \
        default-jdk \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create logs directory
RUN mkdir -p /app/logs

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "online_judge_project.wsgi:application"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      POSTGRES_DB: onlinejudge_db
      POSTGRES_USER: onlinejudge_user
      POSTGRES_PASSWORD: secure_password
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  web:
    build: .
    command: gunicorn --bind 0.0.0.0:8000 --workers 3 online_judge_project.wsgi:application
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://onlinejudge_user:secure_password@db:5432/onlinejudge_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### Requirements File

Create `requirements.txt`:

```
Django==5.2.4
psycopg2-binary==2.9.7
gunicorn==21.2.0
redis==4.6.0
celery==5.3.1
python-dotenv==1.0.0
```

### Docker Deployment Commands

```bash
# Build and start services
docker-compose up -d --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# View logs
docker-compose logs -f web
```

## Cloud Platform Deployment

### Heroku Deployment

1. **Prepare for Heroku**

Create `Procfile`:
```
web: gunicorn online_judge_project.wsgi:application --log-file -
```

Create `runtime.txt`:
```
python-3.11.5
```

Update `requirements.txt`:
```
Django==5.2.4
gunicorn==21.2.0
psycopg2-binary==2.9.7
dj-database-url==2.1.0
whitenoise==6.5.0
```

2. **Deploy to Heroku**

```bash
# Install Heroku CLI and login
heroku login

# Create Heroku app
heroku create your-onlinejudge-app

# Set environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ALLOWED_HOSTS=your-app.herokuapp.com

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

### AWS Deployment

1. **EC2 Instance Setup**

```bash
# Launch EC2 instance with Ubuntu 22.04
# Connect via SSH and follow production deployment steps

# Configure security groups:
# - HTTP (80) from anywhere
# - HTTPS (443) from anywhere
# - SSH (22) from your IP
```

2. **RDS Database Setup**

```bash
# Create RDS PostgreSQL instance
# Update Django settings with RDS endpoint
# Configure security groups for database access
```

3. **S3 for Static Files**

```python
# Install django-storages
pip install django-storages boto3

# Update settings.py
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
AWS_S3_REGION_NAME = 'us-east-1'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.StaticS3Boto3Storage'
```

### Google Cloud Platform

1. **App Engine Deployment**

Create `app.yaml`:
```yaml
runtime: python311

env_variables:
  DEBUG: "False"
  SECRET_KEY: "your-secret-key"
  DATABASE_URL: "postgresql://user:pass@/dbname?host=/cloudsql/project:region:instance"

automatic_scaling:
  min_instances: 1
  max_instances: 10
```

Deploy:
```bash
gcloud app deploy
```

2. **Cloud SQL Setup**

```bash
# Create Cloud SQL PostgreSQL instance
gcloud sql instances create onlinejudge-db --database-version=POSTGRES_15

# Create database and user
gcloud sql databases create onlinejudge_db --instance=onlinejudge-db
gcloud sql users create onlinejudge_user --instance=onlinejudge-db --password=secure_password
```

## Security Configuration

### Secure Code Execution

**⚠️ CRITICAL**: The current implementation uses basic subprocess execution, which is NOT secure for production. Implement proper sandboxing:

1. **Docker-based Sandboxing**

```python
import docker

class DockerJudge:
    def __init__(self):
        self.client = docker.from_env()
    
    def execute_code(self, code, language, input_data, time_limit=1.0, memory_limit=128):
        # Create temporary container
        container = self.client.containers.run(
            image=f'judge-{language}:latest',
            command=['python', '/tmp/solution.py'],
            stdin_open=True,
            detach=True,
            mem_limit=f'{memory_limit}m',
            cpu_period=100000,
            cpu_quota=int(100000 * time_limit),
            network_disabled=True,
            read_only=True,
            tmpfs={'/tmp': 'exec,size=10m'},
            volumes={
                '/tmp/solution.py': {'bind': '/tmp/solution.py', 'mode': 'ro'}
            }
        )
        
        # Execute and get results
        try:
            result = container.wait(timeout=time_limit + 1)
            output = container.logs().decode('utf-8')
            return {
                'status': 'Accepted' if result['StatusCode'] == 0 else 'Runtime Error',
                'output': output,
                'execution_time': time_limit  # Measure actual time
            }
        except docker.errors.ContainerError as e:
            return {'status': 'Runtime Error', 'error': str(e)}
        finally:
            container.remove(force=True)
```

2. **System-level Security**

```bash
# Create restricted user for code execution
sudo useradd --system --shell /bin/false --home /nonexistent judge

# Set up chroot environment
sudo mkdir -p /var/chroot/judge/{bin,lib,lib64,usr,tmp}
sudo cp /bin/python3 /var/chroot/judge/bin/
sudo cp -r /lib/x86_64-linux-gnu /var/chroot/judge/lib/
sudo cp -r /usr/lib/python3.11 /var/chroot/judge/usr/lib/

# Configure resource limits in /etc/security/limits.conf
judge soft nproc 10
judge hard nproc 20
judge soft cpu 5
judge hard cpu 10
judge soft as 134217728  # 128MB
judge hard as 268435456  # 256MB
```

### Application Security

1. **Environment Variables**

```bash
# Use environment variables for sensitive data
export SECRET_KEY='your-very-secure-secret-key'
export DATABASE_PASSWORD='secure-database-password'
export EMAIL_PASSWORD='email-password'
```

2. **Security Headers**

```python
# Add to settings.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
```

3. **Rate Limiting**

```python
# Install django-ratelimit
pip install django-ratelimit

# Add to views
from django_ratelimit.decorators import ratelimit

@ratelimit(key='user', rate='10/m', method='POST')
def submit_code(request, problem_id):
    # Submission logic
    pass
```

## Performance Optimization

### Database Optimization

1. **Database Indexing**

```python
# Add to models.py
class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, db_index=True)
    status = models.CharField(max_length=20, db_index=True)
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['problem', 'status']),
            models.Index(fields=['-submitted_at']),
        ]
```

2. **Query Optimization**

```python
# Use select_related and prefetch_related
def get_submissions(request):
    submissions = Submission.objects.select_related(
        'user', 'problem'
    ).filter(
        user=request.user
    ).order_by('-submitted_at')
    return submissions
```

### Caching

1. **Redis Caching**

```python
# Install redis
pip install redis django-redis

# Add to settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Use caching in views
from django.core.cache import cache

def get_problem_list(request):
    problems = cache.get('problem_list')
    if not problems:
        problems = Problem.objects.all()
        cache.set('problem_list', problems, 300)  # 5 minutes
    return problems
```

2. **Template Caching**

```html
{% load cache %}
{% cache 300 problem_detail problem.id %}
    <!-- Problem content -->
{% endcache %}
```

### Static File Optimization

1. **CDN Configuration**

```python
# Use AWS CloudFront or similar CDN
AWS_S3_CUSTOM_DOMAIN = 'your-cdn-domain.cloudfront.net'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
```

2. **Compression**

```python
# Install whitenoise for static file compression
pip install whitenoise[brotli]

# Add to settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... other middleware
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

## Monitoring and Maintenance

### Logging Configuration

```python
# Comprehensive logging setup
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/opt/onlinejudge/logs/django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/opt/onlinejudge/logs/django_error.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'submissions': {
            'handlers': ['file', 'error_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Health Monitoring

1. **Health Check Endpoint**

```python
# Add to urls.py
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)
```

2. **System Monitoring**

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Monitor system resources
htop  # CPU and memory usage
iotop  # Disk I/O
nethogs  # Network usage

# Monitor application logs
tail -f /opt/onlinejudge/logs/django.log
tail -f /opt/onlinejudge/logs/gunicorn_error.log
```

### Backup Strategy

1. **Database Backup**

```bash
#!/bin/bash
# backup_db.sh
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/onlinejudge_backup_$DATE.sql"

mkdir -p $BACKUP_DIR
pg_dump -h localhost -U onlinejudge_user onlinejudge_db > $BACKUP_FILE
gzip $BACKUP_FILE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "onlinejudge_backup_*.sql.gz" -mtime +7 -delete
```

2. **Media Files Backup**

```bash
#!/bin/bash
# backup_media.sh
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
MEDIA_DIR="/opt/onlinejudge/media"

tar -czf "$BACKUP_DIR/media_backup_$DATE.tar.gz" -C "$MEDIA_DIR" .

# Keep only last 30 days of media backups
find $BACKUP_DIR -name "media_backup_*.tar.gz" -mtime +30 -delete
```

3. **Automated Backup with Cron**

```bash
# Add to crontab
crontab -e

# Daily database backup at 2 AM
0 2 * * * /opt/onlinejudge/scripts/backup_db.sh

# Weekly media backup on Sundays at 3 AM
0 3 * * 0 /opt/onlinejudge/scripts/backup_media.sh
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database connectivity
sudo -u postgres psql -c "SELECT version();"

# Verify database credentials
sudo -u postgres psql -d onlinejudge_db -c "\dt"
```

2. **Static Files Not Loading**

```bash
# Collect static files
python manage.py collectstatic --noinput

# Check Nginx configuration
sudo nginx -t

# Verify file permissions
ls -la /opt/onlinejudge/staticfiles/
```

3. **Code Execution Timeouts**

```python
# Increase timeout in judge.py
def execute_code(self, code, language, input_data, time_limit=5.0):
    # Increased from 1.0 to 5.0 seconds
    pass
```

4. **Memory Issues**

```bash
# Check system memory
free -h

# Monitor application memory usage
ps aux | grep gunicorn

# Adjust Gunicorn worker count
# In gunicorn.conf.py
workers = 2  # Reduce if memory constrained
```

### Log Analysis

1. **Application Logs**

```bash
# View recent errors
tail -n 100 /opt/onlinejudge/logs/django_error.log

# Search for specific errors
grep "ERROR" /opt/onlinejudge/logs/django.log | tail -20

# Monitor real-time logs
tail -f /opt/onlinejudge/logs/django.log
```

2. **Web Server Logs**

```bash
# Nginx access logs
tail -f /var/log/nginx/access.log

# Nginx error logs
tail -f /var/log/nginx/error.log

# Gunicorn logs
tail -f /opt/onlinejudge/logs/gunicorn_error.log
```

### Performance Issues

1. **Database Query Optimization**

```python
# Enable query logging in development
LOGGING['loggers']['django.db.backends'] = {
    'level': 'DEBUG',
    'handlers': ['console'],
}

# Use Django Debug Toolbar
pip install django-debug-toolbar
```

2. **Memory Profiling**

```python
# Install memory profiler
pip install memory-profiler

# Profile memory usage
@profile
def memory_intensive_function():
    # Function code
    pass

# Run with profiler
python -m memory_profiler your_script.py
```

### Recovery Procedures

1. **Database Recovery**

```bash
# Restore from backup
gunzip onlinejudge_backup_20240101_020000.sql.gz
sudo -u postgres psql onlinejudge_db < onlinejudge_backup_20240101_020000.sql
```

2. **Application Recovery**

```bash
# Restart services
sudo systemctl restart onlinejudge
sudo systemctl restart nginx

# Check service status
sudo systemctl status onlinejudge
sudo systemctl status nginx
```

3. **Emergency Procedures**

```bash
# Quick rollback to previous version
cd /opt/onlinejudge
git log --oneline -10  # Find previous commit
git checkout <previous-commit-hash>
sudo systemctl restart onlinejudge
```

This deployment guide provides comprehensive instructions for deploying the Online Judge system in various environments. Always test deployments in a staging environment before applying to production, and maintain regular backups of both data and configuration files.

