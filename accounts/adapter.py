# accounts/adapter.py

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        # login বা signup successful হলে হোমে redirect হবে
        return resolve_url("home")

    
class CustomSocialAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to connect social accounts to existing users
    with the same email to prevent UNIQUE constraint errors.
    """

    def pre_social_login(self, request, sociallogin):
        """
        This method is called before social login is processed.
        If a user with the same email exists, connect the social account
        to the existing user instead of creating a new one.
        """
        email = sociallogin.account.extra_data.get('email')
        if not email:
            return

        try:
            existing_user = User.objects.get(email=email)
        except User.DoesNotExist:
            existing_user = None

        if existing_user:
            # Connect this social account to existing user
            sociallogin.connect(request, existing_user)
            # Mark the process as connecting instead of signup
            sociallogin.state['process'] = 'connect'

    def save_user(self, request, sociallogin, form=None):
        """
        Override save_user to prevent creating duplicates
        if the user already exists.
        """
        user = sociallogin.user
        if User.objects.filter(email=user.email).exists():
            # Return existing user
            user = User.objects.get(email=user.email)
            sociallogin.user = user
            return user
        else:
            # Call default save_user method
            return super().save_user(request, sociallogin, form)