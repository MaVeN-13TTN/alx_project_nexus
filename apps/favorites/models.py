"""
User favorites models for the Movie Recommendation Backend.

This module handles user's favorite movies functionality,
including adding, removing, and managing favorite movie lists.
"""

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class UserFavorite(models.Model):
    """
    Model to track user's favorite movies.

    This model creates a many-to-many relationship between users and movies
    through favorites, allowing users to mark movies they like.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        help_text="User who favorited the movie",
    )
    movie = models.ForeignKey(
        "movies.Movie",
        on_delete=models.CASCADE,
        related_name="favorited_by",
        help_text="Movie that was favorited",
    )

    # Additional metadata
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When the movie was added to favorites"
    )
    notes = models.TextField(
        blank=True, max_length=500, help_text="User's personal notes about this movie"
    )
    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=[(i, f"{i} star{'s' if i != 1 else ''}") for i in range(1, 6)],
        help_text="User's personal rating (1-5 stars)",
    )

    class Meta:
        verbose_name = "User Favorite"
        verbose_name_plural = "User Favorites"
        unique_together = [["user", "movie"]]  # Prevent duplicate favorites
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["movie", "created_at"]),
            models.Index(fields=["user", "rating"]),
        ]

    def __str__(self):
        return f"{self.user.username} → {self.movie.title}"

    def __repr__(self):
        return f"<UserFavorite: {self.user.username} → {self.movie.title}>"

    def clean(self):
        """Validate that the movie exists and is valid."""
        if not self.movie:
            raise ValidationError("Movie is required")
        if not self.user:
            raise ValidationError("User is required")

    @property
    def rating_display(self):
        """Get a display-friendly rating."""
        if self.rating:
            stars = "★" * self.rating + "☆" * (5 - self.rating)
            return f"{stars} ({self.rating}/5)"
        return "Not rated"


class FavoriteList(models.Model):
    """
    Model for user-created favorite movie lists.

    This allows users to organize their favorites into custom lists
    like "Action Movies", "Date Night Movies", etc.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_lists",
        help_text="User who owns this list",
    )
    name = models.CharField(max_length=100, help_text="Name of the favorite list")
    description = models.TextField(
        blank=True, max_length=500, help_text="Description of this favorite list"
    )
    movies = models.ManyToManyField(
        "movies.Movie",
        blank=True,
        related_name="in_favorite_lists",
        help_text="Movies in this favorite list",
    )

    # Privacy settings
    is_public = models.BooleanField(
        default=False, help_text="Whether this list is visible to other users"
    )

    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When this list was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When this list was last updated"
    )

    class Meta:
        verbose_name = "Favorite List"
        verbose_name_plural = "Favorite Lists"
        unique_together = [["user", "name"]]  # Users can't have duplicate list names
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["is_public", "updated_at"]),
        ]

    def __str__(self):
        return f"{self.user.username}'s {self.name}"

    def __repr__(self):
        return f"<FavoriteList: {self.user.username} → {self.name}>"

    def get_movie_count(self):
        """Get the number of movies in this list."""
        return self.movies.count()

    def add_movie(self, movie):
        """Add a movie to this list."""
        self.movies.add(movie)

    def remove_movie(self, movie):
        """Remove a movie from this list."""
        self.movies.remove(movie)

    def has_movie(self, movie):
        """Check if a movie is in this list."""
        return self.movies.filter(id=movie.id).exists()
