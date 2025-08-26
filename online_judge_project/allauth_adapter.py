from allauth.account.adapter import DefaultAccountAdapter
import uuid

class CustomAccountAdapter(DefaultAccountAdapter):
    def populate_username(self, request, user):
        # Generate a unique username using UUID
        user.username = str(uuid.uuid4())