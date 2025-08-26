# Security Guidelines for Online Judge

This document outlines security considerations, best practices, and implementation guidelines for the Online Judge system.

## Table of Contents

- [Security Overview](#security-overview)
- [Code Execution Security](#code-execution-security)
- [Authentication and Authorization](#authentication-and-authorization)
- [Input Validation and Sanitization](#input-validation-and-sanitization)
- [Data Protection](#data-protection)
- [Network Security](#network-security)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security Checklist](#security-checklist)
- [Incident Response](#incident-response)

## Security Overview

The Online Judge system handles user-submitted code execution, which presents unique security challenges. This document provides comprehensive security guidelines for safe deployment and operation.

### Security Principles

1. **Defense in Depth**: Multiple layers of security controls
2. **Least Privilege**: Minimal necessary permissions
3. **Fail Secure**: Secure defaults and error handling
4. **Security by Design**: Built-in security from the ground up

### Threat Model

| Threat | Impact | Likelihood | Mitigation |
|--------|--------|------------|------------|
| Malicious Code Execution | High | High | Sandboxing, Resource Limits |
| Data Breach | High | Medium | Encryption, Access Controls |
| DoS Attacks | Medium | High | Rate Limiting, Resource Monitoring |
| Privilege Escalation | High | Low | Proper Authentication, Authorization |
| SQL Injection | Medium | Low | ORM Usage, Input Validation |

## Code Execution Security

### Current Implementation Limitations

⚠️ **CRITICAL SECURITY WARNING**: The current implementation uses Python's `subprocess` module for code execution, which is **NOT SECURE** for production use. This approach is suitable only for development and educational purposes.

### Production-Ready Sandboxing

#### Docker-based Isolation

Implement Docker containers for secure code execution:

```python
import docker
import tempfile
import os
from pathlib import Path

class SecureJudge:
    def __init__(self):
        self.client = docker.from_env()
        self.base_images = {
            'python': 'python:3.11-alpine',
            'cpp': 'gcc:11-alpine',
            'java': 'openjdk:17-alpine'
        }
    
    def execute_code(self, code, language, input_data, time_limit=1.0, memory_limit=128):
        """Execute code in secure Docker container"""
        
        # Create temporary directory for code
        with tempfile.TemporaryDirectory() as temp_dir:
            code_file = Path(temp_dir) / f"solution.{self.get_extension(language)}"
            input_file = Path(temp_dir) / "input.txt"
            
            # Write code and input files
            code_file.write_text(code)
            input_file.write_text(input_data)
            
            # Configure container security
            container_config = {
                'image': self.base_images[language],
                'command': self.get_run_command(language),
                'volumes': {
                    temp_dir: {'bind': '/workspace', 'mode': 'ro'}
                },
                'working_dir': '/workspace',
                'mem_limit': f'{memory_limit}m',
                'memswap_limit': f'{memory_limit}m',
                'cpu_period': 100000,
                'cpu_quota': int(100000 * time_limit),
                'network_disabled': True,
                'read_only': True,
                'tmpfs': {'/tmp': 'exec,size=10m'},
                'security_opt': ['no-new-privileges:true'],
                'cap_drop': ['ALL'],
                'user': '65534:65534',  # nobody user
                'ulimits': [
                    docker.types.Ulimit(name='nproc', soft=10, hard=10),
                    docker.types.Ulimit(name='nofile', soft=64, hard=64)
                ]
            }
            
            try:
                # Run container with timeout
                container = self.client.containers.run(
                    detach=True,
                    stdin_open=True,
                    **container_config
                )
                
                # Send input and wait for completion
                container.exec_run(f'cat /workspace/input.txt', stdin=True)
                result = container.wait(timeout=time_limit + 2)
                
                # Get output and logs
                output = container.logs().decode('utf-8', errors='ignore')
                
                return {
                    'status': 'Accepted' if result['StatusCode'] == 0 else 'Runtime Error',
                    'output': output,
                    'execution_time': self.measure_execution_time(container),
                    'memory_used': self.measure_memory_usage(container)
                }
                
            except docker.errors.ContainerError as e:
                return {'status': 'Runtime Error', 'error': str(e)}
            except Exception as e:
                return {'status': 'System Error', 'error': str(e)}
            finally:
                try:
                    container.remove(force=True)
                except:
                    pass
```

#### System-level Isolation

For environments where Docker is not available:

```bash
#!/bin/bash
# secure_execute.sh - System-level sandboxing script

# Create chroot environment
CHROOT_DIR="/var/chroot/judge"
USER_ID="judge"
GROUP_ID="judge"

# Setup chroot jail
setup_chroot() {
    mkdir -p "$CHROOT_DIR"/{bin,lib,lib64,usr,tmp,dev}
    
    # Copy essential binaries
    cp /bin/python3 "$CHROOT_DIR/bin/"
    cp /bin/sh "$CHROOT_DIR/bin/"
    
    # Copy required libraries
    ldd /bin/python3 | grep -o '/lib[^ ]*' | xargs -I {} cp {} "$CHROOT_DIR/lib/"
    
    # Create device files
    mknod "$CHROOT_DIR/dev/null" c 1 3
    mknod "$CHROOT_DIR/dev/zero" c 1 5
    mknod "$CHROOT_DIR/dev/urandom" c 1 9
    
    # Set permissions
    chown -R "$USER_ID:$GROUP_ID" "$CHROOT_DIR"
    chmod 755 "$CHROOT_DIR"
}

# Execute code with restrictions
execute_code() {
    local code_file="$1"
    local input_file="$2"
    local time_limit="$3"
    local memory_limit="$4"
    
    # Copy files to chroot
    cp "$code_file" "$CHROOT_DIR/tmp/solution.py"
    cp "$input_file" "$CHROOT_DIR/tmp/input.txt"
    
    # Execute with restrictions
    timeout "$time_limit" \
    chroot "$CHROOT_DIR" \
    sudo -u "$USER_ID" \
    ulimit -v "$((memory_limit * 1024))" \
    ulimit -t "$time_limit" \
    ulimit -f 1024 \
    ulimit -n 64 \
    python3 /tmp/solution.py < /tmp/input.txt
}
```

### Resource Limits

Implement comprehensive resource limiting:

```python
import resource
import signal
import subprocess
import psutil

class ResourceLimiter:
    def __init__(self, time_limit=1.0, memory_limit=128, file_size_limit=1):
        self.time_limit = time_limit
        self.memory_limit = memory_limit * 1024 * 1024  # Convert to bytes
        self.file_size_limit = file_size_limit * 1024 * 1024  # Convert to bytes
    
    def set_limits(self):
        """Set resource limits for child process"""
        # CPU time limit
        resource.setrlimit(resource.RLIMIT_CPU, (int(self.time_limit), int(self.time_limit) + 1))
        
        # Memory limit
        resource.setrlimit(resource.RLIMIT_AS, (self.memory_limit, self.memory_limit))
        
        # File size limit
        resource.setrlimit(resource.RLIMIT_FSIZE, (self.file_size_limit, self.file_size_limit))
        
        # Number of processes
        resource.setrlimit(resource.RLIMIT_NPROC, (1, 1))
        
        # Number of file descriptors
        resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    
    def execute_with_limits(self, command, input_data):
        """Execute command with resource limits"""
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=self.set_limits,
                text=True
            )
            
            # Monitor process
            psutil_process = psutil.Process(process.pid)
            start_time = time.time()
            
            try:
                stdout, stderr = process.communicate(
                    input=input_data,
                    timeout=self.time_limit + 1
                )
                
                execution_time = time.time() - start_time
                memory_info = psutil_process.memory_info()
                
                return {
                    'returncode': process.returncode,
                    'stdout': stdout,
                    'stderr': stderr,
                    'execution_time': execution_time,
                    'memory_used': memory_info.rss
                }
                
            except subprocess.TimeoutExpired:
                process.kill()
                return {'status': 'Time Limit Exceeded'}
                
        except Exception as e:
            return {'status': 'System Error', 'error': str(e)}
```

## Authentication and Authorization

### Secure Authentication

#### Password Security

```python
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password, check_password
import secrets
import string

class SecureAuthManager:
    @staticmethod
    def generate_secure_password(length=12):
        """Generate cryptographically secure password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password
    
    @staticmethod
    def validate_password_strength(password):
        """Validate password meets security requirements"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")
        
        return errors
    
    @staticmethod
    def hash_password(password):
        """Securely hash password"""
        return make_password(password)
```

#### Session Security

```python
# settings.py
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection
SESSION_COOKIE_AGE = 3600  # 1 hour timeout
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Custom session middleware
class SecureSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check session validity
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            if last_activity:
                inactive_time = time.time() - last_activity
                if inactive_time > 3600:  # 1 hour
                    request.session.flush()
                    return redirect('login')
            
            request.session['last_activity'] = time.time()
        
        response = self.get_response(request)
        return response
```

#### Two-Factor Authentication

```python
import pyotp
import qrcode
from io import BytesIO
import base64

class TwoFactorAuth:
    @staticmethod
    def generate_secret():
        """Generate TOTP secret"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(user, secret):
        """Generate QR code for TOTP setup"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name="Online Judge"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    @staticmethod
    def verify_token(secret, token):
        """Verify TOTP token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
```

### Authorization Controls

```python
from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

def admin_required(view_func):
    """Decorator for admin-only views"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden("Admin access required")
        return view_func(request, *args, **kwargs)
    return wrapper

def problem_owner_required(view_func):
    """Decorator for problem owner access"""
    @wraps(view_func)
    @login_required
    def wrapper(request, problem_id, *args, **kwargs):
        problem = get_object_or_404(Problem, id=problem_id)
        if problem.created_by != request.user and not request.user.is_staff:
            return HttpResponseForbidden("Access denied")
        return view_func(request, problem_id, *args, **kwargs)
    return wrapper
```

## Input Validation and Sanitization

### Code Input Validation

```python
import re
import ast
from django.core.exceptions import ValidationError

class CodeValidator:
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r'import\s+os',
        r'import\s+sys',
        r'import\s+subprocess',
        r'import\s+socket',
        r'import\s+urllib',
        r'import\s+requests',
        r'__import__',
        r'eval\s*\(',
        r'exec\s*\(',
        r'compile\s*\(',
        r'open\s*\(',
        r'file\s*\(',
        r'input\s*\(',  # Allow only in specific contexts
        r'raw_input\s*\(',
    ]
    
    # Allowed imports
    ALLOWED_IMPORTS = {
        'python': ['math', 'random', 'collections', 'itertools', 'functools', 'operator'],
        'java': ['java.util.*', 'java.lang.*', 'java.math.*'],
        'cpp': ['iostream', 'vector', 'algorithm', 'string', 'map', 'set']
    }
    
    @classmethod
    def validate_code(cls, code, language):
        """Validate submitted code for security"""
        errors = []
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                errors.append(f"Dangerous pattern detected: {pattern}")
        
        # Language-specific validation
        if language == 'python':
            errors.extend(cls.validate_python_code(code))
        elif language == 'java':
            errors.extend(cls.validate_java_code(code))
        elif language == 'cpp':
            errors.extend(cls.validate_cpp_code(code))
        
        return errors
    
    @classmethod
    def validate_python_code(cls, code):
        """Python-specific validation"""
        errors = []
        
        try:
            # Parse AST to check for dangerous constructs
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Check for dangerous function calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['eval', 'exec', 'compile', '__import__']:
                            errors.append(f"Dangerous function call: {node.func.id}")
                
                # Check for dangerous imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name not in cls.ALLOWED_IMPORTS['python']:
                            errors.append(f"Disallowed import: {alias.name}")
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module not in cls.ALLOWED_IMPORTS['python']:
                        errors.append(f"Disallowed import: {node.module}")
        
        except SyntaxError as e:
            errors.append(f"Syntax error: {e}")
        
        return errors
    
    @classmethod
    def sanitize_input(cls, input_data):
        """Sanitize input data"""
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', input_data)
        
        # Limit input size
        if len(sanitized) > 10000:  # 10KB limit
            raise ValidationError("Input data too large")
        
        return sanitized
```

### SQL Injection Prevention

```python
from django.db import models
from django.core.exceptions import ValidationError

class SecureQueryManager:
    @staticmethod
    def safe_filter(queryset, **filters):
        """Safely filter queryset with validation"""
        allowed_fields = ['id', 'title', 'difficulty', 'status', 'user_id']
        
        for field, value in filters.items():
            if field not in allowed_fields:
                raise ValidationError(f"Invalid filter field: {field}")
            
            # Validate field values
            if isinstance(value, str):
                if len(value) > 100:
                    raise ValidationError(f"Filter value too long: {field}")
                if re.search(r'[<>\'";]', value):
                    raise ValidationError(f"Invalid characters in filter: {field}")
        
        return queryset.filter(**filters)
```

## Data Protection

### Encryption at Rest

```python
from cryptography.fernet import Fernet
from django.conf import settings
import base64

class DataEncryption:
    def __init__(self):
        self.key = settings.ENCRYPTION_KEY.encode()
        self.cipher = Fernet(self.key)
    
    def encrypt_data(self, data):
        """Encrypt sensitive data"""
        if isinstance(data, str):
            data = data.encode()
        
        encrypted = self.cipher.encrypt(data)
        return base64.b64encode(encrypted).decode()
    
    def decrypt_data(self, encrypted_data):
        """Decrypt sensitive data"""
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return decrypted.decode()

# Model with encrypted fields
class EncryptedSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    encrypted_code = models.TextField()
    
    def set_code(self, code):
        encryptor = DataEncryption()
        self.encrypted_code = encryptor.encrypt_data(code)
    
    def get_code(self):
        encryptor = DataEncryption()
        return encryptor.decrypt_data(self.encrypted_code)
```

### Secure File Handling

```python
import os
import tempfile
import hashlib
from pathlib import Path

class SecureFileHandler:
    ALLOWED_EXTENSIONS = {'.py', '.cpp', '.java', '.c'}
    MAX_FILE_SIZE = 1024 * 1024  # 1MB
    
    @classmethod
    def validate_file(cls, file):
        """Validate uploaded file"""
        # Check file size
        if file.size > cls.MAX_FILE_SIZE:
            raise ValidationError("File too large")
        
        # Check file extension
        ext = Path(file.name).suffix.lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise ValidationError("Invalid file type")
        
        # Check file content
        content = file.read().decode('utf-8', errors='ignore')
        file.seek(0)  # Reset file pointer
        
        # Validate content
        if len(content) > 50000:  # 50KB code limit
            raise ValidationError("Code too long")
        
        return True
    
    @classmethod
    def secure_save(cls, file, directory):
        """Securely save file with validation"""
        cls.validate_file(file)
        
        # Generate secure filename
        file_hash = hashlib.sha256(file.read()).hexdigest()[:16]
        file.seek(0)
        
        ext = Path(file.name).suffix.lower()
        secure_filename = f"{file_hash}{ext}"
        
        # Ensure directory exists and is secure
        os.makedirs(directory, mode=0o755, exist_ok=True)
        
        file_path = Path(directory) / secure_filename
        
        with open(file_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
        
        # Set secure permissions
        os.chmod(file_path, 0o644)
        
        return file_path
```

## Network Security

### HTTPS Configuration

```nginx
# Nginx SSL configuration
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL certificates
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # SSL security settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
    
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:8000;
    }
    
    location /accounts/login/ {
        limit_req zone=login burst=5 nodelay;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

### Firewall Configuration

```bash
#!/bin/bash
# firewall_setup.sh

# Enable UFW
ufw --force enable

# Default policies
ufw default deny incoming
ufw default allow outgoing

# SSH access (change port as needed)
ufw allow 22/tcp

# HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Database (only from application server)
ufw allow from 10.0.0.0/8 to any port 5432

# Rate limiting rules
ufw limit ssh
ufw limit 80/tcp
ufw limit 443/tcp

# Log dropped packets
ufw logging on

echo "Firewall configured successfully"
```

## Monitoring and Logging

### Security Logging

```python
import logging
import json
from datetime import datetime
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed

# Configure security logger
security_logger = logging.getLogger('security')

class SecurityEventLogger:
    @staticmethod
    def log_event(event_type, user=None, ip_address=None, details=None):
        """Log security events"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user': user.username if user else None,
            'ip_address': ip_address,
            'details': details or {}
        }
        
        security_logger.info(json.dumps(event))
    
    @staticmethod
    def log_login_attempt(sender, request, user, **kwargs):
        """Log successful login"""
        SecurityEventLogger.log_event(
            'LOGIN_SUCCESS',
            user=user,
            ip_address=request.META.get('REMOTE_ADDR'),
            details={'user_agent': request.META.get('HTTP_USER_AGENT')}
        )
    
    @staticmethod
    def log_login_failure(sender, credentials, request, **kwargs):
        """Log failed login"""
        SecurityEventLogger.log_event(
            'LOGIN_FAILURE',
            ip_address=request.META.get('REMOTE_ADDR'),
            details={
                'username': credentials.get('username'),
                'user_agent': request.META.get('HTTP_USER_AGENT')
            }
        )
    
    @staticmethod
    def log_code_submission(user, problem_id, language, ip_address):
        """Log code submission"""
        SecurityEventLogger.log_event(
            'CODE_SUBMISSION',
            user=user,
            ip_address=ip_address,
            details={
                'problem_id': problem_id,
                'language': language
            }
        )

# Connect signals
user_logged_in.connect(SecurityEventLogger.log_login_attempt)
user_login_failed.connect(SecurityEventLogger.log_login_failure)
```

### Intrusion Detection

```python
from collections import defaultdict
from datetime import datetime, timedelta
from django.core.cache import cache

class IntrusionDetector:
    def __init__(self):
        self.failed_attempts = defaultdict(list)
        self.suspicious_patterns = [
            r'union\s+select',
            r'<script',
            r'javascript:',
            r'eval\s*\(',
            r'exec\s*\('
        ]
    
    def check_failed_logins(self, ip_address):
        """Check for brute force attacks"""
        now = datetime.now()
        cutoff = now - timedelta(minutes=15)
        
        # Get recent failed attempts
        attempts = cache.get(f'failed_login_{ip_address}', [])
        recent_attempts = [a for a in attempts if a > cutoff]
        
        if len(recent_attempts) >= 5:
            self.trigger_alert('BRUTE_FORCE_ATTACK', {
                'ip_address': ip_address,
                'attempts': len(recent_attempts)
            })
            return True
        
        return False
    
    def check_suspicious_input(self, input_data, user, ip_address):
        """Check for malicious input patterns"""
        for pattern in self.suspicious_patterns:
            if re.search(pattern, input_data, re.IGNORECASE):
                self.trigger_alert('SUSPICIOUS_INPUT', {
                    'user': user.username if user else None,
                    'ip_address': ip_address,
                    'pattern': pattern,
                    'input_sample': input_data[:100]
                })
                return True
        
        return False
    
    def trigger_alert(self, alert_type, details):
        """Trigger security alert"""
        alert = {
            'timestamp': datetime.utcnow().isoformat(),
            'alert_type': alert_type,
            'severity': 'HIGH',
            'details': details
        }
        
        # Log alert
        security_logger.critical(json.dumps(alert))
        
        # Send notification (implement as needed)
        self.send_security_notification(alert)
    
    def send_security_notification(self, alert):
        """Send security notification to administrators"""
        # Implement email/SMS/Slack notification
        pass
```

## Security Checklist

### Pre-deployment Checklist

- [ ] **Code Execution Security**
  - [ ] Docker-based sandboxing implemented
  - [ ] Resource limits configured
  - [ ] Network isolation enabled
  - [ ] File system restrictions in place

- [ ] **Authentication & Authorization**
  - [ ] Strong password requirements enforced
  - [ ] Session security configured
  - [ ] Two-factor authentication available
  - [ ] Role-based access controls implemented

- [ ] **Input Validation**
  - [ ] Code validation rules implemented
  - [ ] SQL injection prevention verified
  - [ ] XSS protection enabled
  - [ ] File upload restrictions configured

- [ ] **Data Protection**
  - [ ] Sensitive data encrypted at rest
  - [ ] HTTPS enforced for all connections
  - [ ] Database credentials secured
  - [ ] Backup encryption enabled

- [ ] **Network Security**
  - [ ] Firewall rules configured
  - [ ] Rate limiting implemented
  - [ ] DDoS protection enabled
  - [ ] Security headers configured

- [ ] **Monitoring & Logging**
  - [ ] Security event logging enabled
  - [ ] Intrusion detection configured
  - [ ] Log rotation and retention set
  - [ ] Alert notifications configured

### Runtime Security Monitoring

```bash
#!/bin/bash
# security_monitor.sh - Runtime security monitoring script

# Check for suspicious processes
check_processes() {
    echo "Checking for suspicious processes..."
    ps aux | grep -E "(nc|netcat|telnet|wget|curl)" | grep -v grep
}

# Monitor failed login attempts
check_failed_logins() {
    echo "Checking failed login attempts..."
    grep "authentication failure" /var/log/auth.log | tail -10
}

# Check disk usage
check_disk_usage() {
    echo "Checking disk usage..."
    df -h | awk '$5 > 80 {print $0}'
}

# Monitor network connections
check_network() {
    echo "Checking network connections..."
    netstat -tuln | grep LISTEN
}

# Check for rootkits
check_rootkits() {
    echo "Checking for rootkits..."
    if command -v rkhunter &> /dev/null; then
        rkhunter --check --skip-keypress
    fi
}

# Run all checks
echo "=== Security Monitor Report $(date) ==="
check_processes
check_failed_logins
check_disk_usage
check_network
check_rootkits
echo "=== End Report ==="
```

## Incident Response

### Incident Response Plan

1. **Detection and Analysis**
   - Monitor security logs and alerts
   - Analyze suspicious activities
   - Determine incident severity

2. **Containment**
   - Isolate affected systems
   - Block malicious IP addresses
   - Disable compromised accounts

3. **Eradication**
   - Remove malicious code or files
   - Patch vulnerabilities
   - Update security configurations

4. **Recovery**
   - Restore systems from clean backups
   - Verify system integrity
   - Resume normal operations

5. **Post-Incident Activities**
   - Document lessons learned
   - Update security procedures
   - Conduct security training

### Emergency Response Scripts

```bash
#!/bin/bash
# emergency_response.sh

# Block suspicious IP address
block_ip() {
    local ip=$1
    echo "Blocking IP: $ip"
    ufw insert 1 deny from $ip
    iptables -I INPUT -s $ip -j DROP
}

# Disable user account
disable_user() {
    local username=$1
    echo "Disabling user: $username"
    usermod -L $username
    pkill -u $username
}

# Stop application services
stop_services() {
    echo "Stopping application services..."
    systemctl stop onlinejudge
    systemctl stop nginx
}

# Create system snapshot
create_snapshot() {
    echo "Creating system snapshot..."
    tar -czf "/backup/emergency_snapshot_$(date +%Y%m%d_%H%M%S).tar.gz" \
        /opt/onlinejudge \
        /etc/nginx \
        /var/log
}

# Usage examples:
# ./emergency_response.sh block_ip 192.168.1.100
# ./emergency_response.sh disable_user suspicious_user
# ./emergency_response.sh stop_services
# ./emergency_response.sh create_snapshot

case "$1" in
    block_ip)
        block_ip "$2"
        ;;
    disable_user)
        disable_user "$2"
        ;;
    stop_services)
        stop_services
        ;;
    create_snapshot)
        create_snapshot
        ;;
    *)
        echo "Usage: $0 {block_ip|disable_user|stop_services|create_snapshot} [parameter]"
        exit 1
        ;;
esac
```

This security documentation provides comprehensive guidelines for securing the Online Judge system. Regular security audits, penetration testing, and staying updated with the latest security best practices are essential for maintaining a secure platform.

