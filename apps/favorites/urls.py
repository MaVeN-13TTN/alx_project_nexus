"""
URL patterns for the favorites app.

This module defines URL routing for user favorites functionality,
including favorites management and favorite lists.
"""

from django.urls import path
from .views import (
    UserFavoritesListView,
    check_favorite_status,
)

app_name = "favorites"

urlpatterns = [
    # User favorites endpoints
    path("", UserFavoritesListView.as_view(), name="favorites_list"),
    path("check/<int:movie_id>/", check_favorite_status, name="check_favorite"),
]
