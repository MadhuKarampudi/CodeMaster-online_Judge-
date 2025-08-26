# Online Judge API Documentation

This document provides comprehensive API documentation for the Online Judge system, including REST endpoints, authentication, request/response formats, and usage examples.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URLs and Versioning](#base-urls-and-versioning)
- [Response Formats](#response-formats)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [API Endpoints](#api-endpoints)
- [WebSocket APIs](#websocket-apis)
- [SDK and Client Libraries](#sdk-and-client-libraries)
- [Examples](#examples)

## Overview

The Online Judge API provides programmatic access to the platform's core functionality, including problem management, code submission, and result retrieval. The API follows RESTful principles and returns JSON responses.

### API Features

- **Problem Management**: Retrieve problem lists, details, and test cases
- **Code Submission**: Submit solutions and track execution status
- **User Management**: User registration, authentication, and profile management
- **Statistics**: Access submission statistics and leaderboards
- **Real-time Updates**: WebSocket support for live submission status updates

### Supported Operations

| Operation | Description | Authentication Required |
|-----------|-------------|------------------------|
| GET | Retrieve resources | Optional (depends on resource) |
| POST | Create new resources | Required |
| PUT | Update existing resources | Required |
| DELETE | Remove resources | Required (admin only) |

## Authentication

The Online Judge API supports multiple authentication methods:

### Session Authentication (Web Interface)

Used by the web interface for browser-based interactions:

```python
# Login via web form
POST /accounts/login/
{
    "username": "your_username",
    "password": "your_password"
}

# Session cookie is automatically set
# Subsequent requests include session authentication
```

### Token Authentication (API Access)

For programmatic access, use token-based authentication:

```python
# Obtain token
POST /api/auth/token/
{
    "username": "your_username",
    "password": "your_password"
}

# Response
{
    "token": "your_api_token_here",
    "expires_at": "2024-01-01T12:00:00Z"
}

# Use token in subsequent requests
Authorization: Token your_api_token_here
```

### API Key Authentication (Future Enhancement)

For third-party integrations:

```python
# Include API key in headers
X-API-Key: your_api_key_here
```

## Base URLs and Versioning

### Base URL Structure

```
Production: https://your-domain.com/api/v1/
Development: http://localhost:8000/api/v1/
```

### API Versioning

The API uses URL-based versioning:

- **v1**: Current stable version
- **v2**: Future version (when available)

### Content Types

All API endpoints accept and return JSON:

```
Content-Type: application/json
Accept: application/json
```

## Response Formats

### Standard Response Structure

All API responses follow a consistent structure:

```json
{
    "success": true,
    "data": {
        // Response data
    },
    "message": "Operation completed successfully",
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "req_123456789"
}
```

### Error Response Structure

```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": {
            "field_name": ["This field is required"]
        }
    },
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "req_123456789"
}
```

### Pagination

List endpoints support pagination:

```json
{
    "success": true,
    "data": {
        "results": [
            // Array of items
        ],
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total_pages": 5,
            "total_items": 100,
            "has_next": true,
            "has_previous": false,
            "next_url": "/api/v1/problems/?page=2",
            "previous_url": null
        }
    }
}
```

## Error Handling

### HTTP Status Codes

| Status Code | Description | Usage |
|-------------|-------------|-------|
| 200 | OK | Successful GET, PUT requests |
| 201 | Created | Successful POST requests |
| 204 | No Content | Successful DELETE requests |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Error Codes

| Error Code | Description |
|------------|-------------|
| `VALIDATION_ERROR` | Request data validation failed |
| `AUTHENTICATION_REQUIRED` | User must be authenticated |
| `PERMISSION_DENIED` | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | Requested resource not found |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `SUBMISSION_FAILED` | Code submission processing failed |
| `COMPILATION_ERROR` | Code compilation failed |
| `EXECUTION_ERROR` | Code execution failed |

## Rate Limiting

### Default Limits

| Endpoint Category | Limit | Window |
|------------------|-------|--------|
| Authentication | 5 requests | 1 minute |
| Problem Retrieval | 100 requests | 1 minute |
| Code Submission | 10 requests | 1 minute |
| General API | 1000 requests | 1 hour |

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Rate Limit Exceeded Response

```json
{
    "success": false,
    "error": {
        "code": "RATE_LIMIT_EXCEEDED",
        "message": "Rate limit exceeded. Try again in 60 seconds.",
        "retry_after": 60
    }
}
```

## API Endpoints

### Authentication Endpoints

#### POST /api/v1/auth/login/

Authenticate user and obtain session/token.

**Request:**
```json
{
    "username": "testuser",
    "password": "password123"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "user": {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User"
        },
        "token": "auth_token_here",
        "expires_at": "2024-01-01T12:00:00Z"
    }
}
```

#### POST /api/v1/auth/logout/

Logout user and invalidate session/token.

**Response:**
```json
{
    "success": true,
    "message": "Successfully logged out"
}
```

#### POST /api/v1/auth/register/

Register new user account.

**Request:**
```json
{
    "username": "newuser",
    "email": "new@example.com",
    "password": "securepassword123",
    "first_name": "New",
    "last_name": "User"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "user": {
            "id": 2,
            "username": "newuser",
            "email": "new@example.com"
        },
        "message": "Account created successfully"
    }
}
```

### Problem Endpoints

#### GET /api/v1/problems/

Retrieve list of problems with pagination.

**Query Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)
- `difficulty`: Filter by difficulty (easy, medium, hard)
- `search`: Search in problem titles and descriptions

**Response:**
```json
{
    "success": true,
    "data": {
        "results": [
            {
                "id": 1,
                "title": "Two Sum",
                "difficulty": "easy",
                "time_limit": 1.0,
                "memory_limit": 128,
                "solved_count": 150,
                "total_submissions": 300,
                "acceptance_rate": 50.0,
                "tags": ["array", "hash-table"]
            }
        ],
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total_pages": 1,
            "total_items": 3
        }
    }
}
```

#### GET /api/v1/problems/{id}/

Retrieve detailed problem information.

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "title": "Two Sum",
        "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        "difficulty": "easy",
        "time_limit": 1.0,
        "memory_limit": 128,
        "input_format": "First line contains array, second line contains target",
        "output_format": "Array of two indices",
        "constraints": "2 <= nums.length <= 10^4",
        "sample_test_cases": [
            {
                "input": "[2,7,11,15]\n9",
                "output": "[0,1]",
                "explanation": "nums[0] + nums[1] = 2 + 7 = 9"
            }
        ],
        "tags": ["array", "hash-table"],
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z"
    }
}
```

#### POST /api/v1/problems/ (Admin Only)

Create new problem.

**Request:**
```json
{
    "title": "New Problem",
    "description": "Problem description here",
    "difficulty": "medium",
    "time_limit": 2.0,
    "memory_limit": 256,
    "input_format": "Input format description",
    "output_format": "Output format description",
    "constraints": "Problem constraints",
    "tags": ["dynamic-programming", "graph"]
}
```

### Submission Endpoints

#### POST /api/v1/submissions/

Submit code solution for a problem.

**Request:**
```json
{
    "problem_id": 1,
    "language": "python",
    "code": "def two_sum(nums, target):\n    # Solution code here\n    pass"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "submission_id": 123,
        "status": "pending",
        "message": "Code submitted successfully. Judging in progress.",
        "estimated_time": 5
    }
}
```

#### GET /api/v1/submissions/{id}/

Retrieve submission details and results.

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 123,
        "problem": {
            "id": 1,
            "title": "Two Sum"
        },
        "user": {
            "id": 1,
            "username": "testuser"
        },
        "language": "python",
        "status": "accepted",
        "execution_time": 0.045,
        "memory_used": 1024,
        "code": "def two_sum(nums, target):\n    # Solution code",
        "output": "[0, 1]",
        "error": null,
        "submitted_at": "2024-01-01T12:00:00Z",
        "judged_at": "2024-01-01T12:00:05Z",
        "test_cases_passed": 10,
        "test_cases_total": 10
    }
}
```

#### GET /api/v1/submissions/

Retrieve user's submission history.

**Query Parameters:**
- `page`: Page number
- `problem_id`: Filter by problem
- `status`: Filter by status
- `language`: Filter by language

**Response:**
```json
{
    "success": true,
    "data": {
        "results": [
            {
                "id": 123,
                "problem_title": "Two Sum",
                "language": "python",
                "status": "accepted",
                "execution_time": 0.045,
                "submitted_at": "2024-01-01T12:00:00Z"
            }
        ],
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total_items": 50
        }
    }
}
```

#### GET /api/v1/submissions/{id}/status/

Get real-time submission status (used for polling).

**Response:**
```json
{
    "success": true,
    "data": {
        "status": "judging",
        "progress": 60,
        "message": "Running test case 6 of 10",
        "estimated_remaining": 2
    }
}
```

### User Endpoints

#### GET /api/v1/users/profile/

Get current user's profile information.

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "date_joined": "2024-01-01T10:00:00Z",
        "statistics": {
            "problems_solved": 25,
            "total_submissions": 100,
            "acceptance_rate": 75.0,
            "rank": 150,
            "points": 1250
        },
        "solved_problems": [1, 2, 3, 5, 8]
    }
}
```

#### PUT /api/v1/users/profile/

Update user profile information.

**Request:**
```json
{
    "first_name": "Updated",
    "last_name": "Name",
    "email": "updated@example.com"
}
```

### Statistics Endpoints

#### GET /api/v1/statistics/leaderboard/

Get user leaderboard.

**Query Parameters:**
- `limit`: Number of users to return (default: 50)
- `period`: Time period (all, month, week)

**Response:**
```json
{
    "success": true,
    "data": {
        "leaderboard": [
            {
                "rank": 1,
                "username": "topuser",
                "problems_solved": 100,
                "points": 5000,
                "acceptance_rate": 85.5
            }
        ],
        "user_rank": {
            "rank": 150,
            "username": "testuser",
            "problems_solved": 25,
            "points": 1250
        }
    }
}
```

#### GET /api/v1/statistics/problems/{id}/

Get problem statistics.

**Response:**
```json
{
    "success": true,
    "data": {
        "problem_id": 1,
        "total_submissions": 1000,
        "accepted_submissions": 600,
        "acceptance_rate": 60.0,
        "average_execution_time": 0.125,
        "language_distribution": {
            "python": 45.0,
            "cpp": 30.0,
            "java": 20.0,
            "c": 5.0
        },
        "difficulty_rating": 4.2,
        "tags": ["array", "hash-table"]
    }
}
```

## WebSocket APIs

### Real-time Submission Updates

Connect to WebSocket for real-time submission status updates:

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/submissions/');

ws.onopen = function(event) {
    console.log('Connected to submission updates');
    
    // Subscribe to specific submission
    ws.send(JSON.stringify({
        'action': 'subscribe',
        'submission_id': 123
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Submission update:', data);
    
    // Handle status updates
    if (data.type === 'status_update') {
        updateSubmissionStatus(data.submission_id, data.status);
    }
};
```

**Message Format:**
```json
{
    "type": "status_update",
    "submission_id": 123,
    "status": "judging",
    "progress": 60,
    "message": "Running test case 6 of 10",
    "timestamp": "2024-01-01T12:00:30Z"
}
```

### Live Contest Updates

For contest mode (future enhancement):

```javascript
const contestWs = new WebSocket('ws://localhost:8000/ws/contest/1/');

contestWs.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'leaderboard_update') {
        updateLeaderboard(data.leaderboard);
    }
};
```

## SDK and Client Libraries

### Python SDK

```python
import requests
from typing import Dict, List, Optional

class OnlineJudgeAPI:
    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if token:
            self.session.headers.update({'Authorization': f'Token {token}'})
    
    def login(self, username: str, password: str) -> Dict:
        """Authenticate and get token"""
        response = self.session.post(
            f'{self.base_url}/api/v1/auth/login/',
            json={'username': username, 'password': password}
        )
        response.raise_for_status()
        data = response.json()
        
        if data['success']:
            token = data['data']['token']
            self.session.headers.update({'Authorization': f'Token {token}'})
        
        return data
    
    def get_problems(self, page: int = 1, difficulty: Optional[str] = None) -> Dict:
        """Get list of problems"""
        params = {'page': page}
        if difficulty:
            params['difficulty'] = difficulty
        
        response = self.session.get(
            f'{self.base_url}/api/v1/problems/',
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_problem(self, problem_id: int) -> Dict:
        """Get problem details"""
        response = self.session.get(
            f'{self.base_url}/api/v1/problems/{problem_id}/'
        )
        response.raise_for_status()
        return response.json()
    
    def submit_code(self, problem_id: int, language: str, code: str) -> Dict:
        """Submit code solution"""
        response = self.session.post(
            f'{self.base_url}/api/v1/submissions/',
            json={
                'problem_id': problem_id,
                'language': language,
                'code': code
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_submission(self, submission_id: int) -> Dict:
        """Get submission details"""
        response = self.session.get(
            f'{self.base_url}/api/v1/submissions/{submission_id}/'
        )
        response.raise_for_status()
        return response.json()

# Usage example
api = OnlineJudgeAPI('http://localhost:8000')
api.login('testuser', 'password123')

problems = api.get_problems(difficulty='easy')
problem = api.get_problem(1)

submission = api.submit_code(
    problem_id=1,
    language='python',
    code='def solution(): pass'
)
```

### JavaScript SDK

```javascript
class OnlineJudgeAPI {
    constructor(baseUrl, token = null) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.token = token;
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}/api/v1${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        if (this.token) {
            headers['Authorization'] = `Token ${this.token}`;
        }
        
        const response = await fetch(url, {
            ...options,
            headers
        });
        
        if (!response.ok) {
            throw new Error(`API request failed: ${response.statusText}`);
        }
        
        return response.json();
    }
    
    async login(username, password) {
        const data = await this.request('/auth/login/', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        
        if (data.success) {
            this.token = data.data.token;
        }
        
        return data;
    }
    
    async getProblems(page = 1, difficulty = null) {
        const params = new URLSearchParams({ page });
        if (difficulty) params.append('difficulty', difficulty);
        
        return this.request(`/problems/?${params}`);
    }
    
    async submitCode(problemId, language, code) {
        return this.request('/submissions/', {
            method: 'POST',
            body: JSON.stringify({
                problem_id: problemId,
                language,
                code
            })
        });
    }
}

// Usage
const api = new OnlineJudgeAPI('http://localhost:8000');
await api.login('testuser', 'password123');

const problems = await api.getProblems();
const submission = await api.submitCode(1, 'python', 'def solution(): pass');
```

## Examples

### Complete Submission Workflow

```python
import time
from online_judge_api import OnlineJudgeAPI

# Initialize API client
api = OnlineJudgeAPI('http://localhost:8000')

# Login
login_result = api.login('testuser', 'password123')
print(f"Login successful: {login_result['success']}")

# Get problem list
problems = api.get_problems(difficulty='easy')
print(f"Found {len(problems['data']['results'])} easy problems")

# Get specific problem
problem = api.get_problem(1)
print(f"Problem: {problem['data']['title']}")
print(f"Description: {problem['data']['description'][:100]}...")

# Submit solution
code = """
def two_sum(nums, target):
    num_map = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], i]
        num_map[num] = i
    return []

# Read input
import ast
nums = ast.literal_eval(input().strip())
target = int(input().strip())

# Solve and print result
result = two_sum(nums, target)
print(result)
"""

submission = api.submit_code(
    problem_id=1,
    language='python',
    code=code
)

submission_id = submission['data']['submission_id']
print(f"Submitted code, submission ID: {submission_id}")

# Poll for results
while True:
    result = api.get_submission(submission_id)
    status = result['data']['status']
    
    print(f"Status: {status}")
    
    if status != 'pending':
        print(f"Final result: {status}")
        if status == 'accepted':
            print(f"Execution time: {result['data']['execution_time']}s")
            print(f"Memory used: {result['data']['memory_used']} KB")
        elif result['data']['error']:
            print(f"Error: {result['data']['error']}")
        break
    
    time.sleep(2)  # Wait 2 seconds before checking again
```

### Batch Problem Analysis

```python
def analyze_problems(api, difficulty='easy'):
    """Analyze problems by difficulty"""
    problems = api.get_problems(difficulty=difficulty)
    
    analysis = {
        'total_problems': 0,
        'avg_acceptance_rate': 0,
        'common_tags': {},
        'time_limits': []
    }
    
    for problem_summary in problems['data']['results']:
        problem = api.get_problem(problem_summary['id'])
        problem_data = problem['data']
        
        analysis['total_problems'] += 1
        analysis['avg_acceptance_rate'] += problem_summary['acceptance_rate']
        analysis['time_limits'].append(problem_data['time_limit'])
        
        # Count tags
        for tag in problem_data.get('tags', []):
            analysis['common_tags'][tag] = analysis['common_tags'].get(tag, 0) + 1
    
    # Calculate averages
    if analysis['total_problems'] > 0:
        analysis['avg_acceptance_rate'] /= analysis['total_problems']
        analysis['avg_time_limit'] = sum(analysis['time_limits']) / len(analysis['time_limits'])
    
    return analysis

# Usage
api = OnlineJudgeAPI('http://localhost:8000')
api.login('testuser', 'password123')

easy_analysis = analyze_problems(api, 'easy')
print(f"Easy problems analysis: {easy_analysis}")
```

### Real-time Submission Monitoring

```javascript
class SubmissionMonitor {
    constructor(apiUrl, token) {
        this.api = new OnlineJudgeAPI(apiUrl, token);
        this.ws = null;
        this.callbacks = {};
    }
    
    connect() {
        const wsUrl = this.api.baseUrl.replace('http', 'ws') + '/ws/submissions/';
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('Connected to submission updates');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleUpdate(data);
        };
        
        this.ws.onclose = () => {
            console.log('Disconnected from submission updates');
            // Reconnect after 5 seconds
            setTimeout(() => this.connect(), 5000);
        };
    }
    
    subscribe(submissionId, callback) {
        this.callbacks[submissionId] = callback;
        
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                action: 'subscribe',
                submission_id: submissionId
            }));
        }
    }
    
    handleUpdate(data) {
        const submissionId = data.submission_id;
        const callback = this.callbacks[submissionId];
        
        if (callback) {
            callback(data);
            
            // Remove callback if submission is complete
            if (['accepted', 'wrong_answer', 'time_limit_exceeded', 
                 'runtime_error', 'compilation_error'].includes(data.status)) {
                delete this.callbacks[submissionId];
            }
        }
    }
}

// Usage
const monitor = new SubmissionMonitor('http://localhost:8000', 'your_token');
monitor.connect();

// Submit code and monitor
const api = new OnlineJudgeAPI('http://localhost:8000', 'your_token');
const submission = await api.submitCode(1, 'python', 'your_code');

monitor.subscribe(submission.data.submission_id, (update) => {
    console.log(`Submission ${update.submission_id}: ${update.status}`);
    
    if (update.status === 'accepted') {
        console.log('🎉 Solution accepted!');
    } else if (update.status !== 'pending') {
        console.log('❌ Solution failed:', update.message);
    }
});
```

This API documentation provides comprehensive information for integrating with the Online Judge system. The API is designed to be RESTful, well-documented, and easy to use for both web applications and programmatic access.

