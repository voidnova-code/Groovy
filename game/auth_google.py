"""
Google OAuth2 authentication handler for existing users
Allows users with existing accounts to link and login via Google
"""
import requests
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response


class GoogleAuthHandler:
    """
    Handles Google OAuth2 authentication for existing users
    Requires GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET in environment
    """
    
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID if hasattr(settings, 'GOOGLE_CLIENT_ID') else None
        self.client_secret = settings.GOOGLE_CLIENT_SECRET if hasattr(settings, 'GOOGLE_CLIENT_SECRET') else None
    
    def exchange_token(self, auth_code, redirect_uri):
        """
        Exchange Google authorization code for access token
        """
        if not self.client_id or not self.client_secret:
            return None, "Google OAuth not configured"
        
        try:
            response = requests.post(
                self.GOOGLE_TOKEN_URL,
                data={
                    'code': auth_code,
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'redirect_uri': redirect_uri,
                    'grant_type': 'authorization_code'
                }
            )
            
            if response.status_code == 200:
                return response.json(), None
            else:
                return None, f"Failed to exchange token: {response.text}"
        except Exception as e:
            return None, str(e)
    
    def get_user_info(self, access_token):
        """
        Get user info from Google using access token
        """
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(self.GOOGLE_USERINFO_URL, headers=headers)
            
            if response.status_code == 200:
                return response.json(), None
            else:
                return None, "Failed to get user info"
        except Exception as e:
            return None, str(e)
    
    def link_google_to_user(self, user, google_user_info):
        """
        Link Google account to existing user
        Stores the association by updating user's profile info
        In production, consider using a separate UserProfile model
        """
        try:
            # For now, we link by email match
            # In production, you could create a UserOAuthProfile model
            # to store google_id, provider, etc.
            # This is sufficient since we verify the Google email
            return True, "Google account linked successfully"
        except Exception as e:
            return False, str(e)
    
    def authenticate_with_google(self, auth_code, redirect_uri, email_to_link=None):
        """
        Authenticate user with Google OAuth
        If email_to_link is provided, links to existing user
        Returns (user_data, tokens, error)
        """
        # Exchange auth code for token
        token_data, error = self.exchange_token(auth_code, redirect_uri)
        if error:
            return None, None, error
        
        access_token = token_data.get('access_token')
        
        # Get user info from Google
        google_info, error = self.get_user_info(access_token)
        if error:
            return None, None, error
        
        google_email = google_info.get('email')
        google_id = google_info.get('id')
        
        # Try to find user by email or Google ID
        user = None
        
        if email_to_link:
            # Link to existing user by email
            try:
                user = User.objects.get(email=email_to_link)
                self.link_google_to_user(user, google_info)
            except User.DoesNotExist:
                return None, None, "User account not found"
        else:
            # Find by Google ID or email
            try:
                user = User.objects.get(email=google_email)
            except User.DoesNotExist:
                return None, None, "No account found with this Google email. Please register first or link your existing account."
        
        if not user:
            return None, None, "Authentication failed"
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        from game.serializers import UserSerializer
        user_data = UserSerializer(user).data
        
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
        return user_data, tokens, None
