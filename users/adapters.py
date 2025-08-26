from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth.models import User
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