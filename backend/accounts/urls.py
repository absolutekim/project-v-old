from django.shortcuts import render
from django.urls import path
from accounts.views import register_user, CustomTokenObtainPairView, get_subcategory_tags, get_user_profile, update_user_tags, delete_user_account, get_user_profile_by_username, change_password
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Authentication related endpoints
    path('register/', register_user, name='register'),  # Register a new user
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login and get JWT tokens
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh JWT token
    
    # User data endpoints
    path('profile/', get_user_profile, name='user_profile'),  # Get current user profile
    path('profile/<str:username>/', get_user_profile_by_username, name='user_profile_by_username'),  # Get profile by username
    path('tags/', get_subcategory_tags, name='get_subcategory_tags'),  # Get subcategory tags
    path('update-tags/', update_user_tags, name='update_user_tags'),  # Update user tags
    
    # Account management endpoints
    path('delete-account/', delete_user_account, name='delete_user_account'),  # Delete user account
    # path('change-password/', change_password, name='change_password'),  # Change user password - Now moved to mypage app
]
