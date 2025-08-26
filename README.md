# Online Judge System

A comprehensive Django-based Online Judge platform for programming contests and practice. This system allows users to submit code solutions in multiple programming languages and provides automated judging with real-time feedback.

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

## Features

### Core Functionality
- **User Management**: Secure user registration, authentication, and profile management
- **Problem Management**: Create, edit, and organize programming problems with test cases
- **Multi-language Support**: Support for Python, C++, Java, and C programming languages
- **Automated Judging**: Real-time code execution and evaluation against test cases
- **Submission History**: Track and review all user submissions with detailed results
- **Admin Interface**: Comprehensive admin panel for managing problems and users

### User Experience
- **Responsive Design**: Mobile-friendly interface using Bootstrap 5
- **Real-time Updates**: AJAX-powered status updates for pending submissions
- **Intuitive Navigation**: Clean and professional user interface
- **Sample Test Cases**: Display sample inputs and outputs for each problem
- **Submission Statistics**: Track solved problems and completion rates

### Judging System
- **Multiple Verdicts**: Support for Accepted, Wrong Answer, Time Limit Exceeded, Runtime Error, and Compilation Error
- **Secure Execution**: Sandboxed code execution with timeout and resource limits
- **Performance Metrics**: Track execution time and memory usage
- **Detailed Feedback**: Comprehensive error messages and debugging information

## Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Backend Framework | Django | 5.2.4 | Web application framework |
| Database | SQLite3 | Default | Development database |
| Frontend | HTML/CSS/JavaScript | - | User interface |
| CSS Framework | Bootstrap | 5.3.0 | Responsive design |
| Icons | Font Awesome | 6.0.0 | UI icons |
| Code Execution | Python subprocess | - | Code judging engine |
| Authentication | Django Auth | Built-in | User management |

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

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- Git (for version control)

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd online_judge_project
   ```

2. **Create Virtual Environment**
   ```bash
   python3.11 -m venv online_judge_env
   source online_judge_env/bin/activate  # On Windows: online_judge_env\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install django
   ```

4. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Load Sample Data** (Optional)
   ```bash
   python manage.py shell
   # Run the sample data creation script from the documentation
   ```

7. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

The application will be available at `http://localhost:8000`.

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

## API Documentation

### Submission Status API

**Endpoint**: `/submissions/api/status/<int:submission_id>/`
**Method**: GET
**Authentication**: Required (user must own the submission)

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

## Deployment

### Production Deployment

For production deployment, consider the following steps:

1. **Environment Configuration**
   ```bash
   # Set environment variables
   export DEBUG=False
   export SECRET_KEY='your-secret-key'
   export ALLOWED_HOSTS='your-domain.com'
   ```

2. **Database Migration**
   ```bash
   # Use PostgreSQL or MySQL for production
   pip install psycopg2-binary  # For PostgreSQL
   python manage.py migrate
   ```

3. **Static Files Collection**
   ```bash
   python manage.py collectstatic
   ```

4. **Web Server Configuration**
   - Use Gunicorn or uWSGI as WSGI server
   - Configure Nginx as reverse proxy
   - Set up SSL certificates for HTTPS

5. **Security Hardening**
   - Configure firewall rules
   - Set up proper file permissions
   - Enable security headers
   - Configure CSRF and XSS protection

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

**Built with ❤️ using Django and Python**

