"""
URL configuration for the preferences app.

This module defines the URL patterns for user preferences functionality,
including preference management, viewing history, and recommendation settings.
"""

from django.urls import path
from . import views

app_name = "preferences"

urlpatterns = [
    # User preferences management
    path("", views.UserPreferencesView.as_view(), name="user-preferences"),
    path(
        "summary/",
        views.UserPreferencesSummaryView.as_view(),
        name="preferences-summary",
    ),
    path(
        "quick-update/", views.quick_preference_update, name="quick-preference-update"
    ),
    path("reset/", views.reset_preferences, name="reset-preferences"),
    # Viewing history management
    path(
        "history/", views.ViewingHistoryListView.as_view(), name="viewing-history-list"
    ),
    path(
        "history/<int:pk>/",
        views.ViewingHistoryDetailView.as_view(),
        name="viewing-history-detail",
    ),
    path("history/clear/", views.clear_viewing_history, name="clear-viewing-history"),
    path("mark-watched/<int:movie_id>/", views.mark_watched, name="mark-watched"),
    # Recommendation and stats endpoints
    path(
        "recommendations/",
        views.preference_recommendations,
        name="preference-recommendations",
    ),
    path("stats/", views.watching_stats, name="watching-stats"),
]
