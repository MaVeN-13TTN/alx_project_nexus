"""
User preferences models for the Movie Recommendation Backend.

This module handles user preferences for movie recommendations,
including genre preferences, viewing history, and recommendation settings.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class UserPreference(models.Model):
    """
    Model to store user's movie preferences for personalized recommendations.

    This model stores user preferences including favorite genres,
    viewing preferences, and recommendation settings.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="preference",
        help_text="User these preferences belong to",
    )

    # Genre preferences (many-to-many with Genre)
    genres = models.ManyToManyField(
        "movies.Genre",
        blank=True,
        related_name="preferred_by_users",
        help_text="User's preferred movie genres",
    )

    # Viewing preferences
    preferred_decades = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated list of preferred decades (e.g., '1990s,2000s,2010s')",
    )
    min_rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Minimum TMDb rating for recommendations",
    )
    max_runtime = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum movie runtime in minutes for recommendations",
    )

    # Language preferences
    preferred_languages = models.CharField(
        max_length=100,
        blank=True,
        help_text="Comma-separated list of preferred language codes (ISO 639-1)",
    )
    include_foreign_films = models.BooleanField(
        default=True, help_text="Include non-English movies in recommendations"
    )

    # Recommendation settings
    recommendation_frequency = models.CharField(
        max_length=20,
        choices=[
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
            ("never", "Never"),
        ],
        default="weekly",
        help_text="How often to receive new recommendations",
    )
    enable_email_recommendations = models.BooleanField(
        default=False, help_text="Send recommendations via email"
    )

    # Advanced preferences
    avoid_genres = models.ManyToManyField(
        "movies.Genre",
        blank=True,
        related_name="avoided_by_users",
        help_text="Genres to avoid in recommendations",
    )
    include_adult_content = models.BooleanField(
        default=False, help_text="Include adult content in recommendations"
    )

    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When preferences were first created"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When preferences were last updated"
    )

    class Meta:
        verbose_name = "User Preference"
        verbose_name_plural = "User Preferences"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["updated_at"]),
            models.Index(fields=["recommendation_frequency"]),
        ]

    def __str__(self):
        return f"Preferences for {self.user.username}"

    def __repr__(self):
        return f"<UserPreference: {self.user.username}>"

    def get_preferred_genre_names(self):
        """Get a list of preferred genre names."""
        return list(self.genres.values_list("name", flat=True))

    def get_avoided_genre_names(self):
        """Get a list of avoided genre names."""
        return list(self.avoid_genres.values_list("name", flat=True))

    def get_preferred_decades_list(self):
        """Get preferred decades as a list."""
        if self.preferred_decades:
            return [decade.strip() for decade in self.preferred_decades.split(",")]
        return []

    def get_preferred_languages_list(self):
        """Get preferred languages as a list."""
        if self.preferred_languages:
            return [lang.strip() for lang in self.preferred_languages.split(",")]
        return []

    def has_genre_preferences(self):
        """Check if user has set any genre preferences."""
        return self.genres.exists()

    def should_recommend(self, movie):
        """
        Check if a movie matches user preferences.

        Args:
            movie: Movie instance to check

        Returns:
            bool: True if movie matches preferences
        """
        # Check minimum rating
        if self.min_rating and movie.vote_average < self.min_rating:
            return False

        # Check maximum runtime
        if self.max_runtime and movie.runtime and movie.runtime > self.max_runtime:
            return False

        # Check avoided genres
        if self.avoid_genres.exists():
            movie_genre_ids = set(movie.genres.values_list("id", flat=True))
            avoided_genre_ids = set(self.avoid_genres.values_list("id", flat=True))
            if movie_genre_ids.intersection(avoided_genre_ids):
                return False

        # Check language preferences
        if not self.include_foreign_films and movie.original_language != "en":
            preferred_langs = self.get_preferred_languages_list()
            if preferred_langs and movie.original_language not in preferred_langs:
                return False

        return True


class ViewingHistory(models.Model):
    """
    Model to track user's movie viewing history.

    This helps improve recommendations by understanding what users
    have already watched and their viewing patterns.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="viewing_history",
        help_text="User who viewed the movie",
    )
    movie = models.ForeignKey(
        "movies.Movie",
        on_delete=models.CASCADE,
        related_name="viewed_by",
        help_text="Movie that was viewed",
    )

    # Viewing details
    watched_at = models.DateTimeField(
        auto_now_add=True, help_text="When the movie was watched"
    )
    completion_percentage = models.PositiveSmallIntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage of movie completed (0-100)",
    )

    # User feedback
    liked = models.BooleanField(
        null=True,
        blank=True,
        help_text="Whether the user liked the movie (null = no feedback)",
    )
    user_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=[(i, f"{i} star{'s' if i != 1 else ''}") for i in range(1, 6)],
        help_text="User's rating (1-5 stars)",
    )

    class Meta:
        verbose_name = "Viewing History"
        verbose_name_plural = "Viewing Histories"
        unique_together = [["user", "movie", "watched_at"]]
        ordering = ["-watched_at"]
        indexes = [
            models.Index(fields=["user", "watched_at"]),
            models.Index(fields=["movie", "watched_at"]),
            models.Index(fields=["user", "liked"]),
        ]

    def __str__(self):
        return f"{self.user.username} watched {self.movie.title}"

    def __repr__(self):
        return f"<ViewingHistory: {self.user.username} → {self.movie.title}>"

    @property
    def was_completed(self):
        """Check if the movie was completed (>= 90%)."""
        return self.completion_percentage >= 90

    @property
    def rating_display(self):
        """Get a display-friendly rating."""
        if self.user_rating:
            stars = "★" * self.user_rating + "☆" * (5 - self.user_rating)
            return f"{stars} ({self.user_rating}/5)"
        return "Not rated"
