from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import get_user_model
from .models import UserProfile
User = get_user_model()
import uuid

class AccountAdapter(DefaultAccountAdapter):
    def populate_username(self, request, user):
        # Generate a unique username based on the email address
        # This is necessary when ACCOUNT_USERNAME_REQUIRED = False
        # and ACCOUNT_AUTHENTICATION_METHOD = 'email'
        username = user.email.split('@')[0]
        original_username = username
        i = 0
        while User.objects.filter(username=username).exists():
            i += 1
            username = original_username + str(i)
        user.username = username
    
    def save_user(self, request, user, form, commit=True):
        """Override save_user to avoid duplicate profile creation"""
        user = super().save_user(request, user, form, commit)
        if commit:
            # Only create profile if it doesn't exist (signal will handle creation)
            UserProfile.objects.get_or_create(user=user)
        return user