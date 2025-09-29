"""
Custom authentication backends for tenant users
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to login with email
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Handle both username and email parameters
        email = kwargs.get('email', username)
        
        try:
            # Try to find user by email or username
            user = User.objects.get(
                Q(email=email) | Q(username=username) | Q(email=username)
            )
            
            # Check password
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
                
        except User.DoesNotExist:
            return None
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
