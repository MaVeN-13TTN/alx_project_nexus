"""
Authentication and user-related models for the Movie Recommendation Backend.

This module extends Django's built-in User model with additional fields
and functionality specific to movie recommendations.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator


class User(AbstractUser):
    """
    Extended User model with additional fields for movie recommendations.

    This model extends Django's AbstractUser to include movie-specific
    user preferences and profile information.
    """

    # Override email field to make it required and unique
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text="User's email address (used for login and notifications)",
    )

    # Additional profile fields
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text="Short biography or description of the user",
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        help_text="User's birth date (for age-appropriate recommendations)",
    )
    location = models.CharField(
        max_length=100, blank=True, help_text="User's location (city, country)"
    )

    # Profile image
    avatar = models.URLField(blank=True, help_text="URL to user's profile picture")

    # Privacy settings
    is_public_profile = models.BooleanField(
        default=True, help_text="Whether the user's profile is public"
    )
    allow_recommendations = models.BooleanField(
        default=True, help_text="Whether to show personalized recommendations"
    )

    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Account creation timestamp"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Last profile update timestamp"
    )

    # Use email as the username field for authentication
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.username} ({self.email})"

    def __repr__(self):
        return f"<User: {self.username} (ID: {self.id})>"

    @property
    def full_name(self):
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def display_name(self):
        """Get the best display name for the user."""
        if self.full_name:
            return self.full_name
        return self.username

    def get_favorite_count(self):
        """Get the number of movies this user has favorited."""
        return self.favorites.count()

    def has_preferences(self):
        """Check if the user has set up genre preferences."""
        return hasattr(self, "preference") and self.preference.genres.exists()


class UserProfile(models.Model):
    """
    Extended user profile information.

    This model stores additional user information that doesn't fit
    in the main User model but is useful for recommendations.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # Watching preferences
    preferred_language = models.CharField(
        max_length=10,
        blank=True,
        help_text="Preferred language for movies (ISO 639-1 code)",
    )
    min_rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Minimum rating for movie recommendations",
    )

    # Notification preferences
    email_notifications = models.BooleanField(
        default=True, help_text="Receive email notifications"
    )
    recommendation_emails = models.BooleanField(
        default=False, help_text="Receive weekly recommendation emails"
    )

    # Activity tracking
    last_active = models.DateTimeField(
        auto_now=True, help_text="Last activity timestamp"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"Profile for {self.user.username}"
