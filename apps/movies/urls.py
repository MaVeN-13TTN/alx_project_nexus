"""
URL configuration for movies app.

This module defines URL patterns for movie-related API endpoints.
Provides comprehensive movie data access with TMDb integration.
"""

from django.urls import path
from apps.movies import views

app_name = "movies"

urlpatterns = [
    # Local database movie endpoints
    path("movies/", views.MovieListView.as_view(), name="movie-list"),
    path("movies/<int:tmdb_id>/", views.MovieDetailView.as_view(), name="movie-detail"),
    # Genre management endpoints
    path("genres/", views.GenreListView.as_view(), name="genre-list"),
    path("genres/sync/", views.sync_genres, name="genre-sync"),
    # TMDb API integration endpoints
    path("trending/", views.trending_movies, name="trending-movies"),
    path("popular/", views.popular_movies, name="popular-movies"),
    path("search/", views.search_movies, name="search-movies"),
    path("discover/", views.discover_movies, name="discover-movies"),
]
