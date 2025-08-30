from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import get_user_model
User = get_user_model()
import uuid

class AccountAdapter(DefaultAccountAdapter):
    def populate_username(self, request, user):
        # Generate a unique username based on email or a UUID
        # This is a fallback if allauth's default unique username generation fails
        if not user.username:
            email_prefix = user.email.split('@')[0]
            username = email_prefix
            # Ensure uniqueness by appending a UUID if necessary
            while User.objects.filter(username=username).exists():
                username = f"{email_prefix}-{str(uuid.uuid4())[:8]}"
            user.username = username