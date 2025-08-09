"""
Serializers for the authentication app.

This module contains serializers for user registration, login, profile management,
and JWT token handling for the Movie Recommendation Backend.
"""

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import User, UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Handles user account creation with email as username,
    password confirmation, and basic profile information.
    """

    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )

    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
        min_length=3,
        max_length=150,
    )

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    password_confirm = serializers.CharField(write_only=True, required=True)

    first_name = serializers.CharField(required=False, allow_blank=True, max_length=30)

    last_name = serializers.CharField(required=False, allow_blank=True, max_length=30)

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "bio",
            "birth_date",
            "location",
        )
        extra_kwargs = {
            "bio": {"required": False, "allow_blank": True},
            "birth_date": {"required": False, "allow_null": True},
            "location": {"required": False, "allow_blank": True},
        }

    def validate(self, attrs):
        """Validate password confirmation and other fields."""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Password fields do not match."}
            )
        return attrs

    def create(self, validated_data):
        """Create and return a new user instance."""
        # Remove password_confirm from validated_data
        validated_data.pop("password_confirm", None)

        # Create the user
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        # Create associated UserProfile
        UserProfile.objects.create(user=user)

        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    Validates email and password credentials.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        """Validate email and password."""
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            # Authenticate with email instead of username
            user = authenticate(
                request=self.context.get("request"),
                username=email,  # Django auth uses 'username' parameter
                password=password,
            )

            if not user:
                raise serializers.ValidationError(
                    "Invalid email or password.", code="authorization"
                )

            if not user.is_active:
                raise serializers.ValidationError(
                    "This account has been deactivated.", code="authorization"
                )

            attrs["user"] = user
            return attrs
        else:
            raise serializers.ValidationError(
                "Must provide email and password.", code="authorization"
            )


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that includes additional user information.

    Extends the default JWT serializer to include user profile data
    in the token response.
    """

    username_field = "email"

    @classmethod
    def get_token(cls, user):
        """Get token with custom claims."""
        token = super().get_token(user)

        # Add custom claims
        token["username"] = user.username
        token["email"] = user.email
        token["full_name"] = user.display_name
        token["is_verified"] = getattr(user, "email_verified", False)

        return token

    def validate(self, attrs):
        """Validate and return token data with user information."""
        data = super().validate(attrs)

        # Add user information to response
        user = self.user
        data.update(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "full_name": user.display_name,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "date_joined": user.date_joined,
                    "last_login": user.last_login,
                }
            }
        )

        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information.

    Handles reading and updating user profile data.
    """

    full_name = serializers.CharField(source="display_name", read_only=True)
    favorite_count = serializers.IntegerField(
        source="get_favorite_count", read_only=True
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "bio",
            "birth_date",
            "location",
            "avatar",
            "is_public_profile",
            "allow_recommendations",
            "favorite_count",
            "date_joined",
            "last_login",
        )
        read_only_fields = ("id", "username", "email", "date_joined", "last_login")


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile information.

    Allows users to update their profile data except sensitive fields.
    """

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "bio",
            "birth_date",
            "location",
            "avatar",
            "is_public_profile",
            "allow_recommendations",
        )

    def validate_birth_date(self, value):
        """Validate birth date is not in the future."""
        if value and value > timezone.now().date():
            raise serializers.ValidationError("Birth date cannot be in the future.")
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing user password.

    Requires current password and validates new password.
    """

    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True, write_only=True, validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate_current_password(self, value):
        """Validate current password is correct."""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        """Validate new password confirmation."""
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "New password fields do not match."}
            )
        return attrs

    def save(self):
        """Update user password."""
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class UserExtendedProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for extended user profile including UserProfile model.

    Combines User and UserProfile information.
    """

    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "birth_date",
            "location",
            "avatar",
            "is_public_profile",
            "allow_recommendations",
            "date_joined",
            "last_login",
            "profile",
        )
        read_only_fields = ("id", "username", "email", "date_joined", "last_login")

    def get_profile(self, obj):
        """Get extended profile information."""
        try:
            profile = obj.profile
            return {
                "preferred_language": profile.preferred_language,
                "min_rating": profile.min_rating,
                "email_notifications": profile.email_notifications,
                "recommendation_emails": profile.recommendation_emails,
                "last_active": profile.last_active,
            }
        except UserProfile.DoesNotExist:
            return None
