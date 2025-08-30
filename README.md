# 🏆 CodeMaster - Online Judge Platform

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Railway-brightgreen)](https://codemaster-onlinejudge-production.up.railway.app/)
[![Django](https://img.shields.io/badge/Django-5.2.4-green)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**🌐 Live Production App**: [https://codemaster-onlinejudge-production.up.railway.app/](https://codemaster-onlinejudge-production.up.railway.app/)

A comprehensive Django-based Online Judge platform for programming contests and practice. This system allows users to submit code solutions in multiple programming languages and provides automated judging with real-time feedback.

## 🎯 Live Demo

**Try it now**: [CodeMaster Online Judge](https://codemaster-onlinejudge-production.up.railway.app/)

**Test Credentials:**
- Email: `admin@example.com`
- Password: `admin123`

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Security Considerations](#security-considerations)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### 🔐 Authentication & User Management
- **JWT Authentication**: Secure token-based authentication system
- **User Profiles**: Comprehensive user profiles with statistics tracking
- **Registration/Login**: Seamless signup and login experience
- **Admin Interface**: Powerful Django admin panel for user management

### 💻 Problem Solving Platform
- **Multi-language Support**: Python, C++, Java, and C programming languages
- **Problem Library**: Diverse collection of coding challenges
- **Difficulty Levels**: Problems categorized by complexity
- **Sample Test Cases**: Clear examples for each problem

### ⚡ Real-time Code Judging
- **Instant Feedback**: Automated judging with immediate results
- **Multiple Verdicts**: Accepted, Wrong Answer, TLE, Runtime Error, Compilation Error
- **Performance Metrics**: Execution time and memory usage tracking
- **Detailed Output**: Comprehensive error messages and debugging info

### 🎨 Modern User Experience
- **Responsive Design**: Mobile-friendly Bootstrap 5 interface
- **Real-time Updates**: AJAX-powered submission status updates
- **Professional UI**: Clean and intuitive navigation
- **Progress Tracking**: Monitor solved problems and completion rates

## Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Backend** | Django | 5.2.4 | Web application framework |
| **Database** | PostgreSQL/SQLite | - | Production/Development database |
| **Authentication** | JWT + Django Auth | - | Secure user authentication |
| **API** | Django REST Framework | - | RESTful API endpoints |
| **Frontend** | Bootstrap 5 + JavaScript | 5.3.0 | Responsive user interface |
| **Code Execution** | Python subprocess | - | Multi-language code judging |
| **Deployment** | Railway + Docker | - | Cloud hosting platform |
| **Static Files** | WhiteNoise | - | Static file serving |

## System Architecture

The Online Judge follows a monolithic Django architecture with clear separation of concerns:

```
online_judge_project/
├── online_judge_project/     # Main project configuration
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL routing
│   └── wsgi.py              # WSGI configuration
├── users/                   # User management app
│   ├── models.py            # User profile models
│   ├── views.py             # Authentication views
│   ├── forms.py             # User forms
│   └── admin.py             # Admin configuration
├── problems/                # Problem management app
│   ├── models.py            # Problem and TestCase models
│   ├── views.py             # Problem display views
│   └── admin.py             # Problem admin interface
├── submissions/             # Submission handling app
│   ├── models.py            # Submission model
│   ├── views.py             # Submission views
│   ├── forms.py             # Submission forms
│   ├── judge.py             # Judging engine
│   └── admin.py             # Submission admin
├── templates/               # HTML templates
│   ├── base.html            # Base template
│   ├── home.html            # Homepage
│   ├── users/               # User templates
│   ├── problems/            # Problem templates
│   └── submissions/         # Submission templates
├── static/                  # Static files (CSS, JS, images)
└── media/                   # User-uploaded files
```

### Database Schema

The system uses four main models:

1. **User** (Django built-in): Handles authentication and basic user information
2. **UserProfile**: Extended user information including statistics
3. **Problem**: Programming problems with metadata and constraints
4. **TestCase**: Input/output pairs for problem validation
5. **Submission**: User code submissions with results and metadata

## 🛠️ Installation

### Prerequisites

- **Python 3.11+** 
- **pip** (Python package installer)
- **Git** (for version control)

### Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/MadhuKarampudi/CodeMaster-online_Judge-.git
   cd CodeMaster-online_Judge-
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

**🌐 Local Access**: `http://localhost:8000`

## Configuration

### Django Settings

Key configuration options in `settings.py`:

```python
# Security Settings
DEBUG = True  # Set to False in production
ALLOWED_HOSTS = ['*']  # Configure for production

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Authentication Settings
LOGIN_REDIRECT_URL = '/problems/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'

# Static Files
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Judging Engine Configuration

The judging engine supports multiple programming languages with configurable settings:

```python
LANGUAGE_CONFIGS = {
    'python': {
        'extension': '.py',
        'compile_cmd': None,
        'run_cmd': ['python3', '{filename}'],
        'timeout_multiplier': 1.0
    },
    'cpp': {
        'extension': '.cpp',
        'compile_cmd': ['g++', '-o', '{executable}', '{filename}', '-std=c++17'],
        'run_cmd': ['./{executable}'],
        'timeout_multiplier': 1.0
    },
    # Additional language configurations...
}
```

## Usage

### For Users

1. **Registration and Login**
   - Visit the homepage and click "Get Started" to register
   - Fill in the registration form with username, email, and password
   - Login with your credentials to access the platform

2. **Browsing Problems**
   - Navigate to the Problems page to view available challenges
   - Problems are categorized by difficulty (Easy, Medium, Hard)
   - Click on any problem to view detailed description and sample test cases

3. **Submitting Solutions**
   - Click "Submit Solution" on any problem page
   - Select your preferred programming language
   - Write your code in the provided editor
   - Submit and wait for automated judging results

4. **Tracking Progress**
   - View your submission history in "My Submissions"
   - Monitor your solved problems count and completion rate
   - Review detailed feedback for each submission

### For Administrators

1. **Managing Problems**
   - Access the Django admin panel at `/admin/`
   - Create new problems with descriptions and constraints
   - Add test cases (both sample and hidden)
   - Set time and memory limits

2. **User Management**
   - View and manage user accounts
   - Monitor user statistics and activity
   - Handle user-related issues

3. **System Monitoring**
   - Review submission logs and error reports
   - Monitor system performance and resource usage
   - Manage database and file storage

## 📚 API Documentation

### 🔐 JWT Authentication API

**Base URL**: `https://codemaster-onlinejudge-production.up.railway.app/api/auth/`

#### Login Endpoint
```http
POST /api/auth/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password123"
}
```

**Response**:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
}
```

#### Signup Endpoint
```http
POST /api/auth/signup/
Content-Type: application/json

{
    "email": "newuser@example.com",
    "password": "password123",
    "first_name": "Jane",
    "last_name": "Smith"
}
```

### 📊 Submission Status API

**Endpoint**: `/submissions/api/status/<int:submission_id>/`
**Method**: GET
**Authentication**: Required (JWT token or session)

**Response Format**:
```json
{
    "status": "Accepted",
    "execution_time": 0.045,
    "memory_used": 1024,
    "output": "Program output",
    "error": "Error messages (if any)"
}
```

**Status Values**:
- `Pending`: Submission is being processed
- `Accepted`: Solution is correct
- `Wrong Answer`: Output doesn't match expected result
- `Time Limit Exceeded`: Execution took too long
- `Runtime Error`: Program crashed during execution
- `Compilation Error`: Code failed to compile
- `Memory Limit Exceeded`: Program used too much memory

### URL Patterns

| URL Pattern | View | Description |
|-------------|------|-------------|
| `/` | Home | Landing page |
| `/accounts/register/` | RegisterView | User registration |
| `/accounts/login/` | LoginView | User login |
| `/accounts/logout/` | LogoutView | User logout |
| `/problems/` | ProblemListView | List all problems |
| `/problems/<int:pk>/` | ProblemDetailView | Problem details |
| `/submissions/` | SubmissionHistoryView | User's submissions |
| `/submissions/<int:pk>/` | SubmissionDetailView | Submission details |
| `/submissions/submit/<int:problem_id>/` | SubmitCodeView | Submit solution |
| `/admin/` | Django Admin | Administrative interface |

## 🚀 Deployment

### 🌐 Live Production Deployment

**✅ Currently Deployed**: [https://codemaster-onlinejudge-production.up.railway.app/](https://codemaster-onlinejudge-production.up.railway.app/)

### Railway Deployment (Recommended)

This project is optimized for Railway deployment with automatic CI/CD:

1. **One-Click Deploy**
   ```bash
   # Fork this repository and connect to Railway
   # Railway will automatically deploy from your GitHub repo
   ```

2. **Environment Variables**
   Set these in Railway dashboard:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   DATABASE_URL=postgresql://... (Railway provides this automatically)
   ALLOWED_HOSTS=your-domain.railway.app
   ```

3. **Automatic Features**
   - ✅ **Auto-deployment** on every GitHub push
   - ✅ **Database migrations** run automatically
   - ✅ **Static files** collected and served
   - ✅ **SSL certificate** provided by Railway
   - ✅ **Custom domain** support available

### Production Deployment

For other production deployments:

1. **Environment Configuration**
   ```bash
   # Set environment variables
   export DEBUG=False
   export SECRET_KEY='your-secret-key'
   export ALLOWED_HOSTS='your-domain.com'
   ```

2. **Database Migration**
   ```bash
   # Use PostgreSQL for production (Railway provides this)
   python manage.py migrate
   ```

3. **Static Files Collection**
   ```bash
   python manage.py collectstatic
   ```

### Docker Deployment

Create a `Dockerfile` for containerized deployment:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "online_judge_project.wsgi:application"]
```

### Cloud Deployment

The application can be deployed on various cloud platforms:

- **Heroku**: Use the provided `Procfile` and configure environment variables
- **AWS**: Deploy using Elastic Beanstalk or EC2 instances
- **Google Cloud**: Use App Engine or Compute Engine
- **DigitalOcean**: Deploy on Droplets with proper configuration

## Security Considerations

### Current Implementation

The current implementation includes basic security measures suitable for development and educational purposes:

1. **Django Security Features**
   - CSRF protection enabled by default
   - XSS protection through template auto-escaping
   - SQL injection prevention via ORM
   - Secure password hashing

2. **Code Execution Security**
   - Temporary file isolation
   - Process timeout limits
   - Basic resource constraints

### Production Security Requirements

**⚠️ IMPORTANT**: The current judging system uses Python's `subprocess` module, which is **NOT SECURE** for production use. For production deployment, implement proper sandboxing:

1. **Docker Containerization**
   ```bash
   # Example Docker command for secure execution
   docker run --rm --memory=128m --cpus=1 --network=none \
     --read-only --tmpfs /tmp:exec \
     python:3.11-alpine python /tmp/solution.py
   ```

2. **System-level Isolation**
   - Use chroot jails or similar isolation mechanisms
   - Implement proper user permissions and access controls
   - Set up resource limits (CPU, memory, disk I/O)

3. **Additional Security Measures**
   - Input validation and sanitization
   - Rate limiting for submissions
   - Monitoring and logging of all activities
   - Regular security audits and updates

### Recommended Security Enhancements

1. **Authentication Security**
   - Implement two-factor authentication
   - Add password strength requirements
   - Set up account lockout policies

2. **Data Protection**
   - Encrypt sensitive data at rest
   - Use HTTPS for all communications
   - Implement proper backup and recovery procedures

3. **Monitoring and Logging**
   - Set up comprehensive logging
   - Implement intrusion detection
   - Monitor system resources and performance

## Contributing

We welcome contributions to improve the Online Judge system. Please follow these guidelines:

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper testing
4. Submit a pull request with detailed description

### Code Standards

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Include unit tests for new features

### Testing

Run the test suite before submitting changes:

```bash
python manage.py test
```

### Documentation

Update documentation for any new features or changes:
- Update README.md for significant changes
- Add docstrings to new functions
- Update API documentation if applicable

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support and Contact

For questions, issues, or contributions:
- Create an issue on the project repository
- Contact the development team
- Check the documentation for common solutions

---

## 🌟 Project Status

**🚀 Production Ready**: Fully deployed and operational on Railway  
**🔗 Live URL**: [https://codemaster-onlinejudge-production.up.railway.app/](https://codemaster-onlinejudge-production.up.railway.app/)  
**📈 Status**: Active and maintained  
**🔄 CI/CD**: Automatic deployment from GitHub  

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Madhu Karampudi**
- GitHub: [@MadhuKarampudi](https://github.com/MadhuKarampudi)
- Project: [CodeMaster Online Judge](https://github.com/MadhuKarampudi/CodeMaster-online_Judge-)

## 🙏 Acknowledgments

- Django community for the excellent framework
- Railway for seamless deployment platform
- Bootstrap team for the responsive UI framework
- All contributors and users of this platform

---

**⭐ If you find this project helpful, please give it a star!**

**Built with ❤️ using Django and Python**

