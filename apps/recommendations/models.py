from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


# Include simple models for TMDb compatibility
class SimpleFavorite(models.Model):
    """Simple favorites model using TMDb movie IDs directly"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="simple_favorites"
    )
    movie_id = models.PositiveIntegerField(help_text="TMDb movie ID")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "movie_id"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["movie_id"]),
        ]

    def __str__(self):
        return f"{self.user.email} -> Movie {self.movie_id}"


class SimpleViewingHistory(models.Model):
    """Simple viewing history model using TMDb movie IDs directly"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="simple_viewing_history"
    )
    movie_id = models.PositiveIntegerField(help_text="TMDb movie ID")
    rating = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    watched_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "watched_at"]),
            models.Index(fields=["movie_id"]),
        ]

    def __str__(self):
        return f"{self.user.email} -> Movie {self.movie_id} ({self.rating}/10)"


class RecommendationCache(models.Model):
    """Cache for user recommendations to improve performance"""

    RECOMMENDATION_TYPES = [
        ("content", "Content-Based"),
        ("collaborative", "Collaborative Filtering"),
        ("hybrid", "Hybrid"),
        ("trending", "Trending"),
        ("similar", "Similar Movies"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recommendation_caches"
    )
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)
    movie_ids = models.JSONField(help_text="List of recommended movie IDs from TMDb")
    scores = models.JSONField(
        help_text="Recommendation scores for each movie", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="When this cache entry expires")

    class Meta:
        unique_together = ["user", "recommendation_type"]
        indexes = [
            models.Index(fields=["user", "recommendation_type"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.get_recommendation_type_display()}"


class UserSimilarity(models.Model):
    """Store user similarity scores for collaborative filtering"""

    user1 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="similarity_as_user1"
    )
    user2 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="similarity_as_user2"
    )
    similarity_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Similarity score between 0 and 1",
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user1", "user2"]
        indexes = [
            models.Index(fields=["user1", "similarity_score"]),
            models.Index(fields=["user2", "similarity_score"]),
        ]

    def __str__(self):
        return f"{self.user1.email} <-> {self.user2.email}: {self.similarity_score:.2f}"


class MovieSimilarity(models.Model):
    """Store movie similarity scores for content-based filtering"""

    movie1_id = models.IntegerField(help_text="TMDb movie ID")
    movie2_id = models.IntegerField(help_text="TMDb movie ID")
    similarity_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Content similarity score between 0 and 1",
    )
    similarity_type = models.CharField(
        max_length=20,
        choices=[
            ("genre", "Genre Similarity"),
            ("cast", "Cast Similarity"),
            ("director", "Director Similarity"),
            ("combined", "Combined Similarity"),
        ],
        default="combined",
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["movie1_id", "movie2_id", "similarity_type"]
        indexes = [
            models.Index(fields=["movie1_id", "similarity_score"]),
            models.Index(fields=["movie2_id", "similarity_score"]),
            models.Index(fields=["similarity_type"]),
        ]

    def __str__(self):
        return f"Movies {self.movie1_id} <-> {self.movie2_id}: {self.similarity_score:.2f} ({self.similarity_type})"


class RecommendationFeedback(models.Model):
    """Store user feedback on recommendations for improvement"""

    FEEDBACK_TYPES = [
        ("like", "Liked"),
        ("dislike", "Disliked"),
        ("not_interested", "Not Interested"),
        ("watched", "Watched"),
        ("ignore", "Ignore"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recommendation_feedback"
    )
    movie_id = models.IntegerField(help_text="TMDb movie ID")
    recommendation_type = models.CharField(
        max_length=20, choices=RecommendationCache.RECOMMENDATION_TYPES
    )
    feedback = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "movie_id", "recommendation_type"]
        indexes = [
            models.Index(fields=["user", "feedback"]),
            models.Index(fields=["movie_id", "feedback"]),
            models.Index(fields=["recommendation_type"]),
        ]

    def __str__(self):
        return (
            f"{self.user.email} - Movie {self.movie_id}: {self.get_feedback_display()}"
        )


class RecommendationSettings(models.Model):
    """User-specific recommendation settings"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="recommendation_settings"
    )

    # Algorithm preferences
    prefer_content_based = models.BooleanField(default=True)
    prefer_collaborative = models.BooleanField(default=True)
    prefer_trending = models.BooleanField(default=False)

    # Diversity settings
    genre_diversity = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="0.0 = Similar genres, 1.0 = Diverse genres",
    )
    release_year_range = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        help_text="Include movies from last N years",
    )

    # Quality filters
    min_vote_average = models.FloatField(
        default=6.0, validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    min_vote_count = models.IntegerField(default=100, validators=[MinValueValidator(0)])

    # Frequency settings
    max_recommendations = models.IntegerField(
        default=20, validators=[MinValueValidator(5), MaxValueValidator(100)]
    )
    cache_duration_hours = models.IntegerField(
        default=2, validators=[MinValueValidator(1), MaxValueValidator(24)]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Recommendation Settings for {self.user.email}"
