"""
Simple favorites models using TMDb IDs directly for Phase 6 compatibility.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


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
