"""
Authentication views for the Movie Recommendation Backend.

This module contains API views for user registration, login, logout,
profile management, and JWT token handling.
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    PasswordChangeSerializer,
    UserExtendedProfileSerializer,
)


class UserRegistrationView(APIView):
    """
    API view for user registration.

    Creates a new user account with email as username and returns JWT tokens.
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(description="User registered successfully"),
            400: OpenApiResponse(description="Validation errors"),
        },
        summary="Register a new user",
        description="Create a new user account with email, username, and password.",
    )
    def post(self, request):
        """Register a new user."""
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # Generate JWT tokens for the new user
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            return Response(
                {
                    "success": True,
                    "message": "User registered successfully",
                    "data": {
                        "user": {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                            "full_name": user.display_name,
                        },
                        "tokens": {
                            "access": str(access_token),
                            "refresh": str(refresh),
                        },
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "message": "Registration failed",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view.

    Extends the default token view to include user information
    and custom validation.
    """

    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        summary="Obtain JWT tokens",
        description="Login with email and password to get access and refresh tokens.",
    )
    def post(self, request, *args, **kwargs):
        """Handle user login and token generation."""
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Update response format
            response.data = {
                "success": True,
                "message": "Login successful",
                "data": response.data,
            }
        else:
            response.data = {
                "success": False,
                "message": "Login failed",
                "errors": response.data,
            }

        return response


class UserLogoutView(APIView):
    """
    API view for user logout.

    Blacklists the refresh token to prevent further use.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request={
            "type": "object",
            "properties": {
                "refresh": {
                    "type": "string",
                    "description": "Refresh token to blacklist",
                }
            },
            "required": ["refresh"],
        },
        responses={
            200: OpenApiResponse(description="Logout successful"),
            400: OpenApiResponse(description="Invalid token"),
        },
        summary="Logout user",
        description="Blacklist the refresh token to logout the user.",
    )
    def post(self, request):
        """Logout user by blacklisting refresh token."""
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"success": False, "message": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"success": True, "message": "Logout successful"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"success": False, "message": "Invalid token", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserProfileView(RetrieveUpdateAPIView):
    """
    API view for retrieving and updating user profile.

    Allows authenticated users to view and update their profile information.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Return the current user's profile."""
        return self.request.user

    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == "GET":
            return UserProfileSerializer
        return UserProfileUpdateSerializer

    @extend_schema(
        responses={200: UserProfileSerializer},
        summary="Get user profile",
        description="Retrieve the authenticated user's profile information.",
    )
    def get(self, request, *args, **kwargs):
        """Get user profile."""
        response = super().get(request, *args, **kwargs)
        response.data = {
            "success": True,
            "message": "Profile retrieved successfully",
            "data": response.data,
        }
        return response

    @extend_schema(
        request=UserProfileUpdateSerializer,
        responses={200: UserProfileSerializer},
        summary="Update user profile",
        description="Update the authenticated user's profile information.",
    )
    def patch(self, request, *args, **kwargs):
        """Update user profile."""
        response = super().patch(request, *args, **kwargs)
        if response.status_code == 200:
            response.data = {
                "success": True,
                "message": "Profile updated successfully",
                "data": response.data,
            }
        else:
            response.data = {
                "success": False,
                "message": "Profile update failed",
                "errors": response.data,
            }
        return response
