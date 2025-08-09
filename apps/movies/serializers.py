"""
Serializers for Movies App

This module contains Django REST Framework serializers for movie-related models.
Handles data validation, serialization, and deserialization for API endpoints.
"""

from rest_framework import serializers
from django.utils import timezone

from apps.movies.models import Movie, Genre
from utils.tmdb_client import TMDbClient


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for Genre model."""

    class Meta:
        model = Genre
        fields = ["id", "tmdb_id", "name", "created_at"]
        read_only_fields = ["id", "created_at"]


class MovieListSerializer(serializers.ModelSerializer):
    """Serializer for Movie model in list views (minimal data)."""

    genres = GenreSerializer(many=True, read_only=True)
    poster_url = serializers.SerializerMethodField()
    backdrop_url = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            "id",
            "tmdb_id",
            "title",
            "overview",
            "release_date",
            "poster_path",
            "poster_url",
            "backdrop_path",
            "backdrop_url",
            "vote_average",
            "vote_count",
            "popularity",
            "original_language",
            "genres",
        ]
        read_only_fields = ["id"]

    def get_poster_url(self, obj) -> str:
        """Get full poster URL."""
        if obj.poster_path:
            return TMDbClient.get_image_url(obj.poster_path, size="w500")
        return ""

    def get_backdrop_url(self, obj) -> str:
        """Get full backdrop URL."""
        if obj.backdrop_path:
            return TMDbClient.get_image_url(obj.backdrop_path, size="w780")
        return ""


class MovieDetailSerializer(serializers.ModelSerializer):
    """Serializer for Movie model in detail views (complete data)."""

    genres = GenreSerializer(many=True, read_only=True)
    poster_url = serializers.SerializerMethodField()
    backdrop_url = serializers.SerializerMethodField()
    poster_urls = serializers.SerializerMethodField()
    backdrop_urls = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            "id",
            "tmdb_id",
            "title",
            "original_title",
            "overview",
            "release_date",
            "poster_path",
            "poster_url",
            "poster_urls",
            "backdrop_path",
            "backdrop_url",
            "backdrop_urls",
            "vote_average",
            "vote_count",
            "popularity",
            "original_language",
            "genres",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_poster_url(self, obj) -> str:
        """Get full poster URL (default size)."""
        if obj.poster_path:
            return TMDbClient.get_image_url(obj.poster_path, size="w500")
        return ""

    def get_backdrop_url(self, obj) -> str:
        """Get full backdrop URL (default size)."""
        if obj.backdrop_path:
            return TMDbClient.get_image_url(obj.backdrop_path, size="w780")
        return ""

    def get_poster_urls(self, obj) -> dict:
        """Get poster URLs in different sizes."""
        if not obj.poster_path:
            return {}

        return {
            "w92": TMDbClient.get_image_url(obj.poster_path, size="w92"),
            "w154": TMDbClient.get_image_url(obj.poster_path, size="w154"),
            "w185": TMDbClient.get_image_url(obj.poster_path, size="w185"),
            "w342": TMDbClient.get_image_url(obj.poster_path, size="w342"),
            "w500": TMDbClient.get_image_url(obj.poster_path, size="w500"),
            "w780": TMDbClient.get_image_url(obj.poster_path, size="w780"),
            "original": TMDbClient.get_image_url(obj.poster_path, size="original"),
        }

    def get_backdrop_urls(self, obj) -> dict:
        """Get backdrop URLs in different sizes."""
        if not obj.backdrop_path:
            return {}

        return {
            "w300": TMDbClient.get_image_url(obj.backdrop_path, size="w300"),
            "w780": TMDbClient.get_image_url(obj.backdrop_path, size="w780"),
            "w1280": TMDbClient.get_image_url(obj.backdrop_path, size="w1280"),
            "original": TMDbClient.get_image_url(obj.backdrop_path, size="original"),
        }


class TMDbMovieSerializer(serializers.Serializer):
    """Serializer for TMDb movie data (from API responses)."""

    id = serializers.IntegerField()
    title = serializers.CharField()
    original_title = serializers.CharField(required=False, allow_blank=True)
    overview = serializers.CharField(required=False, allow_blank=True)
    release_date = serializers.DateField(required=False, allow_null=True)
    poster_path = serializers.CharField(required=False, allow_null=True)
    backdrop_path = serializers.CharField(required=False, allow_null=True)
    vote_average = serializers.FloatField(default=0.0)
    vote_count = serializers.IntegerField(default=0)
    popularity = serializers.FloatField(default=0.0)
    original_language = serializers.CharField(default="en")
    adult = serializers.BooleanField(default=False)
    video = serializers.BooleanField(default=False)
    genre_ids = serializers.ListField(child=serializers.IntegerField(), required=False)

    # Additional fields for movie detail responses
    genres = serializers.ListField(required=False)
    runtime = serializers.IntegerField(required=False, allow_null=True)
    budget = serializers.IntegerField(required=False, default=0)
    revenue = serializers.IntegerField(required=False, default=0)
    homepage = serializers.URLField(required=False, allow_blank=True)
    imdb_id = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    tagline = serializers.CharField(required=False, allow_blank=True)

    # Computed fields
    poster_url = serializers.SerializerMethodField()
    backdrop_url = serializers.SerializerMethodField()

    def get_poster_url(self, obj) -> str:
        """Get full poster URL."""
        poster_path = obj.get("poster_path")
        if poster_path:
            return TMDbClient.get_image_url(poster_path, size="w500")
        return ""

    def get_backdrop_url(self, obj) -> str:
        """Get full backdrop URL."""
        backdrop_path = obj.get("backdrop_path")
        if backdrop_path:
            return TMDbClient.get_image_url(backdrop_path, size="w780")
        return ""


class MovieSearchSerializer(serializers.Serializer):
    """Serializer for movie search parameters."""

    query = serializers.CharField(
        min_length=1, max_length=200, help_text="Search query for movie titles"
    )
    page = serializers.IntegerField(
        min_value=1, max_value=1000, default=1, help_text="Page number for pagination"
    )
    year = serializers.IntegerField(
        min_value=1900,
        max_value=2030,
        required=False,
        help_text="Filter by release year",
    )
    include_adult = serializers.BooleanField(
        default=False, help_text="Include adult content in results"
    )


class MovieDiscoverSerializer(serializers.Serializer):
    """Serializer for movie discovery parameters."""

    page = serializers.IntegerField(
        min_value=1, max_value=1000, default=1, help_text="Page number for pagination"
    )
    genre_ids = serializers.CharField(
        required=False, help_text="Comma-separated list of genre IDs"
    )
    sort_by = serializers.ChoiceField(
        choices=[
            "popularity.asc",
            "popularity.desc",
            "release_date.asc",
            "release_date.desc",
            "revenue.asc",
            "revenue.desc",
            "primary_release_date.asc",
            "primary_release_date.desc",
            "original_title.asc",
            "original_title.desc",
            "vote_average.asc",
            "vote_average.desc",
            "vote_count.asc",
            "vote_count.desc",
        ],
        default="popularity.desc",
        help_text="Sort criteria for results",
    )
    min_vote_average = serializers.FloatField(
        min_value=0.0, max_value=10.0, required=False, help_text="Minimum vote average"
    )
    min_vote_count = serializers.IntegerField(
        min_value=0, required=False, help_text="Minimum vote count"
    )
    year = serializers.IntegerField(
        min_value=1900,
        max_value=2030,
        required=False,
        help_text="Filter by release year",
    )
    with_genres = serializers.CharField(
        required=False,
        help_text="Include movies with these genres (comma-separated genre IDs)",
    )
    without_genres = serializers.CharField(
        required=False,
        help_text="Exclude movies with these genres (comma-separated genre IDs)",
    )

    def validate_genre_ids(self, value):
        """Validate genre_ids format."""
        if value:
            try:
                genre_ids = [int(id.strip()) for id in value.split(",")]
                return genre_ids
            except ValueError:
                raise serializers.ValidationError(
                    "genre_ids must be comma-separated integers"
                )
        return []


class PaginatedResponseSerializer(serializers.Serializer):
    """Serializer for paginated API responses."""

    page = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    total_results = serializers.IntegerField()
    results = serializers.ListField()


class MovieTrendingSerializer(serializers.Serializer):
    """Serializer for trending movies parameters."""

    time_window = serializers.ChoiceField(
        choices=["day", "week"],
        default="day",
        help_text="Time window for trending movies",
    )
    page = serializers.IntegerField(
        min_value=1, max_value=1000, default=1, help_text="Page number for pagination"
    )


class MoviePopularSerializer(serializers.Serializer):
    """Serializer for popular movies parameters."""

    page = serializers.IntegerField(
        min_value=1, max_value=1000, default=1, help_text="Page number for pagination"
    )


class MovieFilterSerializer(serializers.Serializer):
    """Serializer for local movie filtering parameters."""

    page = serializers.IntegerField(
        min_value=1, default=1, help_text="Page number for pagination"
    )
    page_size = serializers.IntegerField(
        min_value=1, max_value=100, default=20, help_text="Number of movies per page"
    )
    genre_id = serializers.IntegerField(
        required=False, help_text="Filter by genre TMDb ID"
    )
    min_vote_average = serializers.FloatField(
        min_value=0.0, max_value=10.0, required=False, help_text="Minimum vote average"
    )
    sort_by = serializers.ChoiceField(
        choices=[
            "popularity",
            "-popularity",
            "vote_average",
            "-vote_average",
            "release_date",
            "-release_date",
            "title",
            "-title",
        ],
        default="-popularity",
        help_text="Sort field for results",
    )


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses."""

    error = serializers.CharField()
    message = serializers.CharField()
    details = serializers.DictField(required=False)
