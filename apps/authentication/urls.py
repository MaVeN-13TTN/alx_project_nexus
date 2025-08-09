"""
URL patterns for the authentication app.

This module defines URL routing for user authentication,
registration, profile management, and JWT token endpoints.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserRegistrationView,
    CustomTokenObtainPairView,
    UserLogoutView,
    UserProfileView,
)

app_name = "authentication"

urlpatterns = [
    # Authentication endpoints
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Profile management
    path("profile/", UserProfileView.as_view(), name="profile"),
]
