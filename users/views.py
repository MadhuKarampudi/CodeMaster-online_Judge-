from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.generic import CreateView, DetailView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm
from .models import UserProfile
from django.contrib.auth.mixins import LoginRequiredMixin

def login_view(request):
    """Custom login view"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user:
                login(request, user)
                return redirect('/problems/')
            else:
                messages.error(request, 'Invalid email or password.')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'users/login.html')

def signup_view(request):
    """Custom signup view"""
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation
        if not all([first_name, last_name, email, password, confirm_password]):
            messages.error(request, 'All fields are required.')
            return render(request, 'users/signup.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'users/signup.html')
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'users/signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'users/signup.html')
        
        # Create user
        username = email.split('@')[0]  # Use email prefix as username
        counter = 1
        original_username = username
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        messages.success(request, 'Account created successfully! Please log in.')
        return redirect('/auth/login/')
    
    return render(request, 'users/signup.html')

def logout_view(request):
    """Custom logout view"""
    logout(request)
    return redirect('/')

@login_required
def profile(request):
    """User profile view"""
    return render(request, 'users/profile.html', {
        'user': request.user
    })

def leaderboard(request):
    """Leaderboard view showing top users by solved problems"""
    users = User.objects.all()[:10]
    return render(request, 'users/leaderboard.html', {
        'users': users
    })

class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    
    def form_valid(self, form):
        messages.success(self.request, 'Registration successful! Please log in.')
        return super().form_valid(form)
    
    def dispatch(self, request, *args, **kwargs):
        # Redirect authenticated users to problems page
        if request.user.is_authenticated:
            return redirect('problems:list')
        return super().dispatch(request, *args, **kwargs)

class ProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'users/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        print(f"Attempting to retrieve profile for user: {self.request.user.username}")
        return self.request.user.userprofile

