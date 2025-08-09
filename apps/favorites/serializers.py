"""
Serializers for the favorites app.

This module contains serializers for user favorites functionality,
including favorite movies, favorite lists, and related operations.
"""

from rest_framework import serializers
from django.core.exceptions import ValidationError
from apps.movies.models import Movie
from apps.movies.serializers import MovieListSerializer, MovieDetailSerializer
from .models import UserFavorite, FavoriteList


class UserFavoriteSerializer(serializers.ModelSerializer):
    """
    Serializer for user favorite movies.

    Handles individual favorite movie entries with ratings and notes.
    """

    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)
    rating_display = serializers.CharField(read_only=True)

    class Meta:
        model = UserFavorite
        fields = [
            "id",
            "movie",
            "movie_id",
            "rating",
            "rating_display",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_movie_id(self, value):
        """Validate that the movie exists."""
        try:
            Movie.objects.get(id=value)
        except Movie.DoesNotExist:
            raise serializers.ValidationError("Movie not found.")
        return value

    def validate_rating(self, value):
        """Validate that rating is between 1 and 5."""
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def create(self, validated_data):
        """Create a new favorite entry."""
        user = self.context["request"].user
        movie_id = validated_data.pop("movie_id")
        movie = Movie.objects.get(id=movie_id)

        # Check if already favorited
        if UserFavorite.objects.filter(user=user, movie=movie).exists():
            raise serializers.ValidationError(
                {"movie_id": "This movie is already in your favorites."}
            )

        return UserFavorite.objects.create(user=user, movie=movie, **validated_data)


class UserFavoriteUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating favorite movie entries.

    Allows updating rating and notes for existing favorites.
    """

    class Meta:
        model = UserFavorite
        fields = ["rating", "notes"]

    def validate_rating(self, value):
        """Validate that rating is between 1 and 5."""
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class FavoriteListSerializer(serializers.ModelSerializer):
    """
    Serializer for favorite lists.

    Handles collections of favorite movies organized by user.
    """

    movie_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    movie_count = serializers.IntegerField(source="get_movie_count", read_only=True)
    movies = MovieListSerializer(many=True, read_only=True)

    class Meta:
        model = FavoriteList
        fields = [
            "id",
            "name",
            "description",
            "is_public",
            "movie_ids",
            "movie_count",
            "movies",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_movie_ids(self, value):
        """Validate that all movie IDs exist."""
        if value:
            existing_ids = set(
                Movie.objects.filter(id__in=value).values_list("id", flat=True)
            )
            invalid_ids = set(value) - existing_ids
            if invalid_ids:
                raise serializers.ValidationError(
                    f"Movies with IDs {list(invalid_ids)} do not exist."
                )
        return value

    def create(self, validated_data):
        """Create a new favorite list."""
        user = self.context["request"].user
        movie_ids = validated_data.pop("movie_ids", [])

        # Check if user already has a list with this name
        if FavoriteList.objects.filter(user=user, name=validated_data["name"]).exists():
            raise serializers.ValidationError(
                {"name": "You already have a favorite list with this name."}
            )

        favorite_list = FavoriteList.objects.create(user=user, **validated_data)

        # Add movies to the list
        if movie_ids:
            movies = Movie.objects.filter(id__in=movie_ids)
            favorite_list.movies.set(movies)

        return favorite_list

    def update(self, instance, validated_data):
        """Update an existing favorite list."""
        movie_ids = validated_data.pop("movie_ids", None)

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update movies if provided
        if movie_ids is not None:
            movies = Movie.objects.filter(id__in=movie_ids)
            instance.movies.set(movies)

        return instance


class FavoriteListSummarySerializer(serializers.ModelSerializer):
    """
    Serializer for favorite list summaries.

    Provides a lightweight view of favorite lists without full movie details.
    """

    movie_count = serializers.IntegerField(source="get_movie_count", read_only=True)

    class Meta:
        model = FavoriteList
        fields = [
            "id",
            "name",
            "description",
            "is_public",
            "movie_count",
            "created_at",
            "updated_at",
        ]


class AddToFavoritesSerializer(serializers.Serializer):
    """
    Serializer for adding movies to favorites.

    Handles the action of adding a movie to user's favorites with optional rating.
    """

    movie_id = serializers.IntegerField()
    rating = serializers.IntegerField(required=False, min_value=1, max_value=5)
    notes = serializers.CharField(required=False, max_length=500, allow_blank=True)

    def validate_movie_id(self, value):
        """Validate that the movie exists."""
        try:
            Movie.objects.get(id=value)
        except Movie.DoesNotExist:
            raise serializers.ValidationError("Movie not found.")
        return value

    def add_to_favorites(self, user):
        """Add movie to user's favorites."""
        # Get validated data safely
        validated_data = getattr(self, "validated_data", {})
        if not validated_data or "movie_id" not in validated_data:
            raise serializers.ValidationError("Movie ID is required")

        movie_id = validated_data["movie_id"]
        movie = Movie.objects.get(id=movie_id)

        # Create or update favorite
        favorite, created = UserFavorite.objects.get_or_create(
            user=user,
            movie=movie,
            defaults={
                "rating": validated_data.get("rating"),
                "notes": validated_data.get("notes", ""),
            },
        )

        if not created:
            # Update existing favorite
            if "rating" in validated_data:
                favorite.rating = validated_data["rating"]
            if "notes" in validated_data:
                favorite.notes = validated_data["notes"]
            favorite.save()

        return favorite


class RemoveFromFavoritesSerializer(serializers.Serializer):
    """
    Serializer for removing movies from favorites.

    Handles the action of removing a movie from user's favorites.
    """

    movie_id = serializers.IntegerField()

    def validate_movie_id(self, value):
        """Validate that the movie exists."""
        try:
            Movie.objects.get(id=value)
        except Movie.DoesNotExist:
            raise serializers.ValidationError("Movie not found.")
        return value

    def remove_from_favorites(self, user):
        """Remove movie from user's favorites."""
        validated_data = getattr(self, "validated_data", {})
        if not validated_data or "movie_id" not in validated_data:
            raise serializers.ValidationError("Movie ID is required")

        movie_id = validated_data["movie_id"]
        movie = Movie.objects.get(id=movie_id)

        try:
            favorite = UserFavorite.objects.get(user=user, movie=movie)
            favorite.delete()
            return True
        except UserFavorite.DoesNotExist:
            raise serializers.ValidationError("Movie is not in your favorites.")


class BulkFavoriteActionSerializer(serializers.Serializer):
    """
    Serializer for bulk favorite operations.

    Handles adding or removing multiple movies from favorites at once.
    """

    movie_ids = serializers.ListField(
        child=serializers.IntegerField(), min_length=1, max_length=50
    )
    action = serializers.ChoiceField(choices=["add", "remove"])

    def validate_movie_ids(self, value):
        """Validate that all movie IDs exist."""
        existing_ids = set(
            Movie.objects.filter(id__in=value).values_list("id", flat=True)
        )
        invalid_ids = set(value) - existing_ids
        if invalid_ids:
            raise serializers.ValidationError(
                f"Movies with IDs {list(invalid_ids)} do not exist."
            )
        return value

    def perform_bulk_action(self, user):
        """Perform bulk add or remove action."""
        validated_data = getattr(self, "validated_data", {})
        if not validated_data:
            raise serializers.ValidationError("No validated data available")

        movie_ids = validated_data["movie_ids"]
        action = validated_data["action"]

        results = {
            "success": [],
            "errors": [],
            "action": action,
            "total_processed": len(movie_ids),
        }

        for movie_id in movie_ids:
            try:
                movie = Movie.objects.get(id=movie_id)

                if action == "add":
                    favorite, created = UserFavorite.objects.get_or_create(
                        user=user,
                        movie=movie,
                    )
                    if created:
                        results["success"].append(movie_id)
                    else:
                        results["errors"].append(
                            {"movie_id": movie_id, "error": "Already in favorites"}
                        )

                elif action == "remove":
                    deleted_count, _ = UserFavorite.objects.filter(
                        user=user, movie=movie
                    ).delete()
                    if deleted_count > 0:
                        results["success"].append(movie_id)
                    else:
                        results["errors"].append(
                            {"movie_id": movie_id, "error": "Not in favorites"}
                        )

            except Movie.DoesNotExist:
                results["errors"].append(
                    {"movie_id": movie_id, "error": "Movie not found"}
                )

        return results
