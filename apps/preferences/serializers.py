from typing import Dict, Any

from rest_framework import serializers
from apps.movies.models import Genre
from apps.movies.serializers import GenreSerializer
from .models import UserPreference, ViewingHistory


class UserPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for user preferences.

    Handles user movie preferences including genres, viewing settings,
    and recommendation configurations.
    """

    genres = GenreSerializer(many=True, read_only=True)
    genre_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )

    avoid_genres = GenreSerializer(many=True, read_only=True)
    avoid_genre_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )

    preferred_genre_names = serializers.ListField(
        source="get_preferred_genre_names", read_only=True
    )
    avoided_genre_names = serializers.ListField(
        source="get_avoided_genre_names", read_only=True
    )
    preferred_decades_list = serializers.ListField(
        source="get_preferred_decades_list", read_only=True
    )
    preferred_languages_list = serializers.ListField(
        source="get_preferred_languages_list", read_only=True
    )
    has_preferences = serializers.BooleanField(
        source="has_genre_preferences", read_only=True
    )

    class Meta:
        model = UserPreference
        fields = [
            "id",
            "genres",
            "genre_ids",
            "avoid_genres",
            "avoid_genre_ids",
            "preferred_decades",
            "min_rating",
            "max_runtime",
            "preferred_languages",
            "include_foreign_films",
            "recommendation_frequency",
            "enable_email_recommendations",
            "include_adult_content",
            "preferred_genre_names",
            "avoided_genre_names",
            "preferred_decades_list",
            "preferred_languages_list",
            "has_preferences",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_genre_ids(self, value):
        """Validate that all genre IDs exist."""
        if value:
            existing_ids = set(
                Genre.objects.filter(id__in=value).values_list("id", flat=True)
            )
            invalid_ids = set(value) - existing_ids
            if invalid_ids:
                raise serializers.ValidationError(
                    f"Genres with IDs {list(invalid_ids)} do not exist."
                )
        return value

    def validate_avoid_genre_ids(self, value):
        """Validate that all avoid genre IDs exist."""
        if value:
            existing_ids = set(
                Genre.objects.filter(id__in=value).values_list("id", flat=True)
            )
            invalid_ids = set(value) - existing_ids
            if invalid_ids:
                raise serializers.ValidationError(
                    f"Genres with IDs {list(invalid_ids)} do not exist."
                )
        return value

    def validate_min_rating(self, value):
        """Validate minimum rating is between 0 and 10."""
        if value is not None and (value < 0 or value > 10):
            raise serializers.ValidationError(
                "Minimum rating must be between 0 and 10."
            )
        return value

    def validate_max_runtime(self, value):
        """Validate maximum runtime is reasonable."""
        if value is not None and (value < 30 or value > 600):
            raise serializers.ValidationError(
                "Maximum runtime must be between 30 and 600 minutes."
            )
        return value

    def validate(self, attrs):
        """Cross-field validation."""
        genre_ids = attrs.get("genre_ids", [])
        avoid_genre_ids = attrs.get("avoid_genre_ids", [])

        # Check for overlap between preferred and avoided genres
        if genre_ids and avoid_genre_ids:
            overlap = set(genre_ids) & set(avoid_genre_ids)
            if overlap:
                raise serializers.ValidationError(
                    "A genre cannot be both preferred and avoided."
                )

        return attrs

    def create(self, validated_data):
        """Create user preferences."""
        user = self.context["request"].user
        genre_ids = validated_data.pop("genre_ids", [])
        avoid_genre_ids = validated_data.pop("avoid_genre_ids", [])

        # Create or update preferences
        preference, created = UserPreference.objects.get_or_create(
            user=user, defaults=validated_data
        )

        if not created:
            # Update existing preferences
            for attr, value in validated_data.items():
                setattr(preference, attr, value)
            preference.save()

        # Set genre relationships
        if genre_ids is not None:
            genres = Genre.objects.filter(id__in=genre_ids)
            preference.genres.set(genres)

        if avoid_genre_ids is not None:
            avoid_genres = Genre.objects.filter(id__in=avoid_genre_ids)
            preference.avoid_genres.set(avoid_genres)

        return preference

    def update(self, instance, validated_data):
        """Update user preferences."""
        genre_ids = validated_data.pop("genre_ids", None)
        avoid_genre_ids = validated_data.pop("avoid_genre_ids", None)

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update genre relationships if provided
        if genre_ids is not None:
            genres = Genre.objects.filter(id__in=genre_ids)
            instance.genres.set(genres)

        if avoid_genre_ids is not None:
            avoid_genres = Genre.objects.filter(id__in=avoid_genre_ids)
            instance.avoid_genres.set(avoid_genres)

        return instance


class UserPreferenceSummarySerializer(serializers.ModelSerializer):
    """
    Serializer for user preference summaries.

    Provides a lightweight view of user preferences without full details.
    """

    preferred_genre_names = serializers.ListField(
        source="get_preferred_genre_names", read_only=True
    )
    has_preferences = serializers.BooleanField(
        source="has_genre_preferences", read_only=True
    )

    class Meta:
        model = UserPreference
        fields = [
            "id",
            "preferred_genre_names",
            "min_rating",
            "max_runtime",
            "recommendation_frequency",
            "has_preferences",
            "updated_at",
        ]


class ViewingHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for viewing history.

    Tracks movies that users have watched with completion and rating data.
    """

    movie = serializers.StringRelatedField(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)
    rating_display = serializers.CharField(source="rating_display", read_only=True)
    was_completed = serializers.BooleanField(read_only=True)

    class Meta:
        model = ViewingHistory
        fields = [
            "id",
            "movie",
            "movie_id",
            "watched_at",
            "completion_percentage",
            "liked",
            "user_rating",
            "rating_display",
            "was_completed",
        ]
        read_only_fields = ["id", "watched_at"]

    def validate_movie_id(self, value):
        """Validate that the movie exists."""
        from apps.movies.models import Movie

        try:
            Movie.objects.get(id=value)
        except Movie.DoesNotExist:
            raise serializers.ValidationError("Movie not found.")
        return value

    def validate_completion_percentage(self, value):
        """Validate completion percentage is between 0 and 100."""
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Completion percentage must be between 0 and 100."
            )
        return value

    def validate_user_rating(self, value):
        """Validate user rating is between 1 and 5."""
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("User rating must be between 1 and 5.")
        return value

    def create(self, validated_data):
        """Create viewing history entry."""
        from apps.movies.models import Movie

        user = self.context["request"].user
        movie_id = validated_data.pop("movie_id")
        movie = Movie.objects.get(id=movie_id)

        viewing_history = ViewingHistory.objects.create(
            user=user, movie=movie, **validated_data
        )
        return viewing_history


class QuickPreferenceUpdateSerializer(serializers.Serializer):
    """
    Serializer for quick preference updates.

    Allows updating specific preference fields without full preference data.
    """

    genre_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )
    min_rating = serializers.DecimalField(
        max_digits=3, decimal_places=1, required=False, allow_null=True
    )
    recommendation_frequency = serializers.ChoiceField(
        choices=["daily", "weekly", "monthly", "never"], required=False
    )
    include_foreign_films = serializers.BooleanField(required=False)

    def validate_genre_ids(self, value):
        """Validate that all genre IDs exist."""
        if value:
            existing_ids = set(
                Genre.objects.filter(id__in=value).values_list("id", flat=True)
            )
            invalid_ids = set(value) - existing_ids
            if invalid_ids:
                raise serializers.ValidationError(
                    f"Genres with IDs {list(invalid_ids)} do not exist."
                )
        return value

    def validate_min_rating(self, value):
        """Validate minimum rating is between 0 and 10."""
        if value is not None and (value < 0 or value > 10):
            raise serializers.ValidationError(
                "Minimum rating must be between 0 and 10."
            )
        return value

    def update_preferences(self, user) -> UserPreference:
        """Update user preferences with provided data."""
        preference, created = UserPreference.objects.get_or_create(user=user)

        # Get validated data safely
        validated_data: Dict[str, Any] = getattr(self, "validated_data", {})
        if not validated_data:
            return preference

        # Update basic fields
        if "min_rating" in validated_data:
            preference.min_rating = validated_data["min_rating"]
        if "recommendation_frequency" in validated_data:
            preference.recommendation_frequency = validated_data[
                "recommendation_frequency"
            ]
        if "include_foreign_films" in validated_data:
            preference.include_foreign_films = validated_data["include_foreign_films"]

        preference.save()

        # Update genres if provided
        if "genre_ids" in validated_data:
            genres = Genre.objects.filter(id__in=validated_data["genre_ids"])
            preference.genres.set(genres)

        return preference
