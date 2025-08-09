"""
Views for the preferences app.

This module contains API views for user preferences functionality,
including preference management, viewing history, and recommendation settings.
"""

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, CreateModelMixin
from django.shortcuts import get_object_or_404
from django.db import transaction
from typing import Any
from .models import UserPreference, ViewingHistory
from .serializers import (
    UserPreferenceSerializer,
    UserPreferenceSummarySerializer,
    ViewingHistorySerializer,
    QuickPreferenceUpdateSerializer,
)


class UserPreferencesView(
    RetrieveModelMixin, UpdateModelMixin, CreateModelMixin, generics.GenericAPIView
):
    """
    View for managing user preferences.

    Allows users to get, create, or update their movie preferences.
    """

    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> Any:
        """Get or create user preferences."""
        preference, created = UserPreference.objects.get_or_create(
            user=self.request.user
        )
        return preference

    def get(self, request, *args, **kwargs):
        """Get user preferences."""
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """Update user preferences."""
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """Partially update user preferences."""
        return self.partial_update(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Create user preferences."""
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Create preferences for the authenticated user."""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Update preferences for the authenticated user."""
        serializer.save(user=self.request.user)


class UserPreferencesSummaryView(generics.RetrieveAPIView):
    """
    View for getting a summary of user preferences.

    Returns a lightweight view of user preferences.
    """

    serializer_class = UserPreferenceSummarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> Any:
        """Get user preferences summary."""
        preference, created = UserPreference.objects.get_or_create(
            user=self.request.user
        )
        return preference


class ViewingHistoryListView(generics.ListCreateAPIView):
    """
    View for managing viewing history.

    Allows users to view their watching history and add new entries.
    """

    serializer_class = ViewingHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        """Get viewing history for the authenticated user."""
        return (
            ViewingHistory.objects.filter(user=self.request.user)
            .select_related("movie")
            .order_by("-watched_at")
        )

    def perform_create(self, serializer):
        """Create viewing history entry for the authenticated user."""
        serializer.save(user=self.request.user)


class ViewingHistoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for managing individual viewing history entries.

    Allows users to get, update, or delete specific viewing history entries.
    """

    serializer_class = ViewingHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        """Get viewing history for the authenticated user."""
        return ViewingHistory.objects.filter(user=self.request.user)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def quick_preference_update(request):
    """
    Quick update of specific preference fields.

    Allows updating individual preference fields without sending
    the entire preference object.
    """
    serializer = QuickPreferenceUpdateSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            # Access the method through type annotation
            if hasattr(serializer, "update_preferences"):
                preference = serializer.update_preferences(request.user)  # type: ignore
            else:
                # Fallback to manual update
                user_preference, created = UserPreference.objects.get_or_create(
                    user=request.user
                )
                preference = user_preference

            response_serializer = UserPreferenceSummarySerializer(preference)
            return Response(
                {
                    "message": "Preferences updated successfully",
                    "preferences": response_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def mark_watched(request, movie_id):
    """
    Mark a movie as watched.

    Creates or updates a viewing history entry for the specified movie.
    """
    from apps.movies.models import Movie

    # Get the movie
    movie = get_object_or_404(Movie, id=movie_id)

    # Get or create viewing history entry
    viewing_history, created = ViewingHistory.objects.get_or_create(
        user=request.user,
        movie=movie,
        defaults={
            "completion_percentage": 100,
            "liked": request.data.get("liked", None),
            "user_rating": request.data.get("user_rating", None),
        },
    )

    if not created:
        # Update existing entry
        viewing_history.completion_percentage = 100
        if "liked" in request.data:
            viewing_history.liked = request.data["liked"]
        if "user_rating" in request.data:
            viewing_history.user_rating = request.data["user_rating"]
        viewing_history.save()

    serializer = ViewingHistorySerializer(viewing_history)
    return Response(
        {
            "message": f'Movie "{movie.title}" marked as watched',
            "viewing_history": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def preference_recommendations(request):
    """
    Get recommendation settings for the user.

    Returns user's current recommendation preferences and settings.
    """
    preference, created = UserPreference.objects.get_or_create(user=request.user)

    return Response(
        {
            "recommendation_frequency": preference.recommendation_frequency,
            "enable_email_recommendations": preference.enable_email_recommendations,
            "has_preferences": preference.has_genre_preferences(),
            "preferred_genres": [genre.name for genre in preference.genres.all()],
            "min_rating": preference.min_rating,
            "max_runtime": preference.max_runtime,
            "include_foreign_films": preference.include_foreign_films,
            "include_adult_content": preference.include_adult_content,
        }
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def watching_stats(request):
    """
    Get user's watching statistics.

    Returns statistics about the user's viewing history and preferences.
    """
    viewing_history = ViewingHistory.objects.filter(user=request.user)

    total_watched = viewing_history.count()
    completed_movies = viewing_history.filter(completion_percentage=100).count()
    liked_movies = viewing_history.filter(liked=True).count()
    rated_movies = viewing_history.exclude(user_rating__isnull=True).count()

    # Average user rating
    avg_rating = None
    if rated_movies > 0:
        ratings = viewing_history.exclude(user_rating__isnull=True).values_list(
            "user_rating", flat=True
        )
        avg_rating = sum(ratings) / len(ratings)

    # Most watched genres (from viewing history)
    genre_counts = {}
    for history in viewing_history.select_related("movie"):
        for genre in history.movie.genres.all():
            genre_counts[genre.name] = genre_counts.get(genre.name, 0) + 1

    top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return Response(
        {
            "total_watched": total_watched,
            "completed_movies": completed_movies,
            "completion_rate": (
                (completed_movies / total_watched * 100) if total_watched > 0 else 0
            ),
            "liked_movies": liked_movies,
            "like_rate": (
                (liked_movies / total_watched * 100) if total_watched > 0 else 0
            ),
            "rated_movies": rated_movies,
            "average_rating": round(avg_rating, 1) if avg_rating else None,
            "top_genres": [
                {"name": name, "count": count} for name, count in top_genres
            ],
        }
    )


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def clear_viewing_history(request):
    """
    Clear all viewing history for the user.

    Deletes all viewing history entries for the authenticated user.
    """
    deleted_count, _ = ViewingHistory.objects.filter(user=request.user).delete()

    return Response(
        {
            "message": f"Cleared {deleted_count} viewing history entries",
            "deleted_count": deleted_count,
        }
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def reset_preferences(request):
    """
    Reset user preferences to default values.

    Resets all preference fields to their default values.
    """
    preference, created = UserPreference.objects.get_or_create(user=request.user)

    # Reset to defaults
    preference.genres.clear()
    preference.avoid_genres.clear()
    preference.preferred_decades = ""
    preference.min_rating = None
    preference.max_runtime = None
    preference.preferred_languages = ""
    preference.include_foreign_films = True
    preference.recommendation_frequency = "weekly"
    preference.enable_email_recommendations = False
    preference.include_adult_content = False
    preference.save()

    serializer = UserPreferenceSerializer(preference)
    return Response(
        {"message": "Preferences reset to defaults", "preferences": serializer.data}
    )
