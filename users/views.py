from django.shortcuts import render, redirect
from django.views.generic import CreateView, DetailView
from django.contrib.auth import get_user_model
User = get_user_model()
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import UserProfile
from django.contrib.auth.mixins import LoginRequiredMixin

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
        from .models import UserProfile
        
        # Use get_or_create to handle profile creation safely
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                'bio': '',
                'location': '',
                'birth_date': None,
                'avatar': None
            }
        )
        return profile

