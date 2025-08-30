// JWT Authentication JavaScript
class AuthManager {
    constructor() {
        this.baseURL = '/api/auth';
        this.accessToken = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
    }

    // Store tokens in localStorage
    storeTokens(accessToken, refreshToken) {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
        this.accessToken = accessToken;
        this.refreshToken = refreshToken;
    }

    // Clear tokens from localStorage
    clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_data');
        this.accessToken = null;
        this.refreshToken = null;
    }

    // Check if user is authenticated
    isAuthenticated() {
        return !!this.accessToken;
    }

    // Get stored user data
    getUserData() {
        const userData = localStorage.getItem('user_data');
        return userData ? JSON.parse(userData) : null;
    }

    // Store user data
    storeUserData(userData) {
        localStorage.setItem('user_data', JSON.stringify(userData));
    }

    // Login function
    async login(email, password) {
        try {
            const response = await fetch(`${this.baseURL}/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.storeTokens(data.access, data.refresh);
                this.storeUserData(data.user);
                return { success: true, user: data.user };
            } else {
                return { success: false, error: data.error || 'Login failed' };
            }
        } catch (error) {
            return { success: false, error: 'Network error occurred' };
        }
    }

    // Signup function
    async signup(email, password, firstName, lastName) {
        try {
            const response = await fetch(`${this.baseURL}/signup/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    first_name: firstName,
                    last_name: lastName
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.storeTokens(data.access, data.refresh);
                this.storeUserData(data.user);
                return { success: true, user: data.user };
            } else {
                return { success: false, error: data.error || 'Signup failed' };
            }
        } catch (error) {
            return { success: false, error: 'Network error occurred' };
        }
    }

    // Logout function
    logout() {
        this.clearTokens();
        window.location.href = '/';
    }

    // Refresh access token
    async refreshAccessToken() {
        if (!this.refreshToken) {
            this.logout();
            return false;
        }

        try {
            const response = await fetch(`${this.baseURL}/refresh-token/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.accessToken}`
                },
                body: JSON.stringify({
                    refresh: this.refreshToken
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.storeTokens(data.access, this.refreshToken);
                return true;
            } else {
                this.logout();
                return false;
            }
        } catch (error) {
            this.logout();
            return false;
        }
    }

    // Make authenticated API request
    async apiRequest(url, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.accessToken) {
            headers['Authorization'] = `Bearer ${this.accessToken}`;
        }

        let response = await fetch(url, {
            ...options,
            headers
        });

        // If token expired, try to refresh
        if (response.status === 401 && this.refreshToken) {
            const refreshed = await this.refreshAccessToken();
            if (refreshed) {
                headers['Authorization'] = `Bearer ${this.accessToken}`;
                response = await fetch(url, {
                    ...options,
                    headers
                });
            }
        }

        return response;
    }

    // Get CSRF token
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }

    // Initialize auth state on page load
    init() {
        if (this.isAuthenticated()) {
            this.updateUIForAuthenticatedUser();
        } else {
            this.updateUIForAnonymousUser();
        }
    }

    // Update UI for authenticated user
    updateUIForAuthenticatedUser() {
        const userData = this.getUserData();
        if (userData) {
            // Update navigation
            const authLinks = document.querySelector('.auth-links');
            if (authLinks) {
                authLinks.innerHTML = `
                    <span class="navbar-text me-3">Welcome, ${userData.first_name || userData.email}!</span>
                    <a href="/auth/profile/" class="btn btn-outline-primary me-2">Profile</a>
                    <button onclick="authManager.logout()" class="btn btn-outline-danger">Logout</button>
                `;
            }
        }
    }

    // Update UI for anonymous user
    updateUIForAnonymousUser() {
        const authLinks = document.querySelector('.auth-links');
        if (authLinks) {
            authLinks.innerHTML = `
                <a href="/accounts/login/" class="btn btn-outline-primary me-2">Login</a>
                <a href="/accounts/signup/" class="btn btn-primary">Sign Up</a>
            `;
        }
    }
}

// Initialize auth manager
const authManager = new AuthManager();

// Initialize on DOM content loaded
document.addEventListener('DOMContentLoaded', function() {
    authManager.init();
});

// Login form handler
function handleLogin(event) {
    event.preventDefault();
    
    const form = event.target;
    const email = form.querySelector('input[name="login"]').value;
    const password = form.querySelector('input[name="password"]').value;
    const submitBtn = form.querySelector('button[type="submit"]');
    const errorDiv = form.querySelector('.error-message');
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.textContent = 'Logging in...';
    
    authManager.login(email, password).then(result => {
        if (result.success) {
            // Redirect to problems page
            window.location.href = '/problems/';
        } else {
            // Show error message
            if (errorDiv) {
                errorDiv.textContent = result.error;
                errorDiv.style.display = 'block';
            } else {
                alert(result.error);
            }
        }
    }).finally(() => {
        // Reset button state
        submitBtn.disabled = false;
        submitBtn.textContent = 'Sign In';
    });
}

// Signup form handler
function handleSignup(event) {
    event.preventDefault();
    
    const form = event.target;
    const email = form.querySelector('input[name="email"]').value;
    const password1 = form.querySelector('input[name="password1"]').value;
    const password2 = form.querySelector('input[name="password2"]').value;
    const firstName = form.querySelector('input[name="first_name"]').value;
    const lastName = form.querySelector('input[name="last_name"]').value;
    const submitBtn = form.querySelector('button[type="submit"]');
    const errorDiv = form.querySelector('.error-message');
    
    // Validate passwords match
    if (password1 !== password2) {
        if (errorDiv) {
            errorDiv.textContent = 'Passwords do not match';
            errorDiv.style.display = 'block';
        } else {
            alert('Passwords do not match');
        }
        return;
    }
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating Account...';
    
    authManager.signup(email, password1, firstName, lastName).then(result => {
        if (result.success) {
            // Redirect to problems page
            window.location.href = '/problems/';
        } else {
            // Show error message
            if (errorDiv) {
                errorDiv.textContent = result.error;
                errorDiv.style.display = 'block';
            } else {
                alert(result.error);
            }
        }
    }).finally(() => {
        // Reset button state
        submitBtn.disabled = false;
        submitBtn.textContent = 'Sign Up';
    });
}
