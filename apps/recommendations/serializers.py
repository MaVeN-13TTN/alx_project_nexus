from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    RecommendationCache,
    UserSimilarity,
    MovieSimilarity,
    RecommendationFeedback,
    RecommendationSettings,
)

User = get_user_model()


class RecommendationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for user recommendation settings"""

    class Meta:
        model = RecommendationSettings
        fields = [
            "prefer_content_based",
            "prefer_collaborative",
            "prefer_trending",
            "genre_diversity",
            "release_year_range",
            "min_vote_average",
            "min_vote_count",
            "max_recommendations",
            "cache_duration_hours",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_genre_diversity(self, value):
        """Validate genre diversity is between 0 and 1"""
        if not 0.0 <= value <= 1.0:
            raise serializers.ValidationError(
                "Genre diversity must be between 0.0 and 1.0"
            )
        return value

    def validate_min_vote_average(self, value):
        """Validate minimum vote average is between 0 and 10"""
        if not 0.0 <= value <= 10.0:
            raise serializers.ValidationError(
                "Minimum vote average must be between 0.0 and 10.0"
            )
        return value


class RecommendationFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for recommendation feedback"""

    class Meta:
        model = RecommendationFeedback
        fields = ["movie_id", "recommendation_type", "feedback", "created_at"]
        read_only_fields = ["created_at"]

    def validate_movie_id(self, value):
        """Validate movie ID is positive"""
        if value <= 0:
            raise serializers.ValidationError("Movie ID must be positive")
        return value


class MovieRecommendationSerializer(serializers.Serializer):
    """Serializer for individual movie recommendations"""

    id = serializers.IntegerField()
    title = serializers.CharField()
    overview = serializers.CharField()
    poster_path = serializers.CharField(allow_null=True, allow_blank=True)
    backdrop_path = serializers.CharField(allow_null=True, allow_blank=True)
    release_date = serializers.CharField(allow_null=True, allow_blank=True)
    vote_average = serializers.FloatField()
    vote_count = serializers.IntegerField()
    popularity = serializers.FloatField()
    genre_ids = serializers.ListField(child=serializers.IntegerField())
    recommendation_score = serializers.FloatField()
    recommendation_reason = serializers.CharField()

    def to_representation(self, instance):
        """Format the recommendation for API response"""
        data = super().to_representation(instance)

        # Format poster and backdrop URLs
        if data.get("poster_path"):
            data["poster_url"] = f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
        else:
            data["poster_url"] = None

        if data.get("backdrop_path"):
            data["backdrop_url"] = (
                f"https://image.tmdb.org/t/p/w1280{data['backdrop_path']}"
            )
        else:
            data["backdrop_url"] = None

        # Round the recommendation score for readability
        if data.get("recommendation_score"):
            data["recommendation_score"] = round(data["recommendation_score"], 3)

        return data


class RecommendationListSerializer(serializers.Serializer):
    """Serializer for list of recommendations"""

    recommendation_type = serializers.CharField()
    total_count = serializers.IntegerField()
    cached = serializers.BooleanField(default=False)
    generated_at = serializers.DateTimeField()
    recommendations = MovieRecommendationSerializer(many=True)

    def to_representation(self, instance):
        """Format the recommendation list for API response"""
        data = super().to_representation(instance)

        # Add metadata
        data["metadata"] = {
            "algorithm_used": data["recommendation_type"],
            "total_recommendations": data["total_count"],
            "from_cache": data["cached"],
            "generated_at": data["generated_at"],
        }

        return data


class RecommendationAnalyticsSerializer(serializers.Serializer):
    """Serializer for recommendation analytics and insights"""

    total_recommendations_given = serializers.IntegerField()
    user_feedback_count = serializers.IntegerField()
    positive_feedback_percentage = serializers.FloatField()
    most_recommended_genres = serializers.ListField(child=serializers.DictField())
    recommendation_accuracy = serializers.FloatField()
    average_recommendation_score = serializers.FloatField()
    cache_hit_rate = serializers.FloatField()

    def to_representation(self, instance):
        """Format analytics data"""
        data = super().to_representation(instance)

        # Add insights
        data["insights"] = []

        if data["positive_feedback_percentage"] > 80:
            data["insights"].append("High user satisfaction with recommendations")
        elif data["positive_feedback_percentage"] < 40:
            data["insights"].append("Consider adjusting recommendation algorithm")

        if data["cache_hit_rate"] < 30:
            data["insights"].append(
                "Low cache efficiency - consider increasing cache duration"
            )

        return data


class UserSimilaritySerializer(serializers.ModelSerializer):
    """Serializer for user similarity data"""

    user1_email = serializers.EmailField(source="user1.email", read_only=True)
    user2_email = serializers.EmailField(source="user2.email", read_only=True)

    class Meta:
        model = UserSimilarity
        fields = ["user1_email", "user2_email", "similarity_score", "last_updated"]
        read_only_fields = ["last_updated"]


class MovieSimilaritySerializer(serializers.ModelSerializer):
    """Serializer for movie similarity data"""

    class Meta:
        model = MovieSimilarity
        fields = [
            "movie1_id",
            "movie2_id",
            "similarity_score",
            "similarity_type",
            "last_updated",
        ]
        read_only_fields = ["last_updated"]


class RecommendationRequestSerializer(serializers.Serializer):
    """Serializer for recommendation request parameters"""

    RECOMMENDATION_TYPES = [
        ("content", "Content-Based"),
        ("collaborative", "Collaborative Filtering"),
        ("hybrid", "Hybrid"),
        ("trending", "Trending"),
        ("similar", "Similar Movies"),
    ]

    recommendation_type = serializers.ChoiceField(
        choices=RECOMMENDATION_TYPES, default="hybrid"
    )
    limit = serializers.IntegerField(default=20, min_value=1, max_value=100)
    force_refresh = serializers.BooleanField(default=False)
    include_metadata = serializers.BooleanField(default=True)

    def validate_limit(self, value):
        """Validate recommendation limit"""
        if value < 1 or value > 100:
            raise serializers.ValidationError("Limit must be between 1 and 100")
        return value
