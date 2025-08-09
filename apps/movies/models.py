"""
Movie-related models for the Movie Recommendation Backend.

This module contains models for movies, genres, and their relationships
based on The Movie Database (TMDb) API integration.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class Genre(models.Model):
    """
    Movie genre model based on TMDb genre categories.

    This model stores genre information retrieved from TMDb API
    and provides categorization for movies.
    """

    tmdb_id = models.PositiveIntegerField(
        unique=True, help_text="The Movie Database genre ID"
    )
    name = models.CharField(
        max_length=100, help_text="Genre name (e.g., 'Action', 'Comedy', 'Drama')"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the genre was added to the database",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Genre"
        verbose_name_plural = "Genres"
        indexes = [
            models.Index(fields=["tmdb_id"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Genre: {self.name} (TMDb ID: {self.tmdb_id})>"


class Movie(models.Model):
    """
    Movie model based on TMDb movie data.

    This model stores comprehensive movie information retrieved from
    The Movie Database API, including metadata and statistics.
    """

    # TMDb Integration Fields
    tmdb_id = models.PositiveIntegerField(
        unique=True, help_text="The Movie Database movie ID"
    )

    # Basic Movie Information
    title = models.CharField(max_length=255, db_index=True, help_text="Movie title")
    original_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Original movie title (if different from title)",
    )
    overview = models.TextField(blank=True, help_text="Movie plot summary/overview")
    tagline = models.CharField(max_length=500, blank=True, help_text="Movie tagline")

    # Release Information
    release_date = models.DateField(
        null=True, blank=True, help_text="Movie release date"
    )
    status = models.CharField(
        max_length=50,
        blank=True,
        help_text="Release status (e.g., 'Released', 'In Production')",
    )

    # Media Assets
    poster_path = models.CharField(
        max_length=255, blank=True, help_text="Poster image URL path from TMDb"
    )
    backdrop_path = models.CharField(
        max_length=255, blank=True, help_text="Backdrop image URL path from TMDb"
    )

    # Ratings and Statistics
    vote_average = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=Decimal("0.0"),
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Average user rating (0.0-10.0)",
    )
    vote_count = models.PositiveIntegerField(
        default=0, help_text="Number of votes/ratings"
    )
    popularity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal("0.0"),
        help_text="TMDb popularity score",
    )

    # Technical Information
    runtime = models.PositiveIntegerField(
        null=True, blank=True, help_text="Movie duration in minutes"
    )
    budget = models.PositiveBigIntegerField(
        null=True, blank=True, help_text="Movie budget in USD"
    )
    revenue = models.PositiveBigIntegerField(
        null=True, blank=True, help_text="Movie revenue in USD"
    )

    # Language and Location
    original_language = models.CharField(
        max_length=10, blank=True, help_text="Original language code (ISO 639-1)"
    )

    # Relationships
    genres = models.ManyToManyField(
        Genre, blank=True, related_name="movies", help_text="Movie genres"
    )

    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the movie was added to the database",
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Timestamp when the movie was last updated"
    )

    class Meta:
        ordering = ["-popularity", "-vote_average"]
        verbose_name = "Movie"
        verbose_name_plural = "Movies"
        indexes = [
            models.Index(fields=["tmdb_id"]),
            models.Index(fields=["title"]),
            models.Index(fields=["release_date"]),
            models.Index(fields=["vote_average"]),
            models.Index(fields=["popularity"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        year = self.release_date.year if self.release_date else "Unknown"
        return f"{self.title} ({year})"

    def __repr__(self):
        return f"<Movie: {self.title} (TMDb ID: {self.tmdb_id})>"

    @property
    def poster_url(self):
        """Get full poster URL from TMDb."""
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return None

    @property
    def backdrop_url(self):
        """Get full backdrop URL from TMDb."""
        if self.backdrop_path:
            return f"https://image.tmdb.org/t/p/w1280{self.backdrop_path}"
        return None

    @property
    def is_recent(self):
        """Check if the movie was released in the last 2 years."""
        if not self.release_date:
            return False
        two_years_ago = timezone.now().date().replace(year=timezone.now().year - 2)
        return self.release_date >= two_years_ago

    def get_genre_names(self):
        """Get a list of genre names for this movie."""
        return list(self.genres.values_list("name", flat=True))

    def get_rating_display(self):
        """Get formatted rating display."""
        return f"{self.vote_average}/10 ({self.vote_count} votes)"
