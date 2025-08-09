"""
Views for the favorites app.

This module contains API views for managing user favorites,
including adding/removing favorites, creating favorite lists,
and retrieving favorite movie data.
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from drf_spectacular.utils import extend_schema, OpenApiResponse
from typing import Any

from apps.movies.models import Movie
from .models import UserFavorite, FavoriteList
from .serializers import (
    UserFavoriteSerializer,
    UserFavoriteUpdateSerializer,
    FavoriteListSerializer,
    FavoriteListSummarySerializer,
    AddToFavoritesSerializer,
    RemoveFromFavoritesSerializer,
)


class UserFavoritesListView(ListCreateAPIView):
    """
    API view for listing and creating user favorites.

    GET: List all favorites for the authenticated user
    POST: Add a new movie to favorites
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserFavoriteSerializer

    def get_queryset(self) -> Any:
        """Get user favorites for the authenticated user."""
        return (
            UserFavorite.objects.filter(user=self.request.user)
            .select_related("movie")
            .order_by("-created_at")
        )

    @extend_schema(
        responses={200: UserFavoriteSerializer(many=True)},
        summary="List user favorites",
        description="Get all movies in the authenticated user's favorites list.",
    )
    def get(self, request, *args, **kwargs):
        """List user favorites."""
        response = super().get(request, *args, **kwargs)
        favorites_data = response.data if response.data is not None else []
        response.data = {
            "success": True,
            "message": "Favorites retrieved successfully",
            "data": favorites_data,
            "count": len(favorites_data) if isinstance(favorites_data, list) else 0,
        }
        return response

    @extend_schema(
        request=UserFavoriteSerializer,
        responses={
            201: OpenApiResponse(description="Movie added to favorites"),
            400: OpenApiResponse(description="Validation errors"),
        },
        summary="Add movie to favorites",
        description="Add a movie to the authenticated user's favorites list.",
    )
    def post(self, request, *args, **kwargs):
        """Add movie to favorites."""
        response = super().post(request, *args, **kwargs)
        if response.status_code == 201:
            response.data = {
                "success": True,
                "message": "Movie added to favorites successfully",
                "data": response.data,
            }
        else:
            response.data = {
                "success": False,
                "message": "Failed to add movie to favorites",
                "errors": response.data,
            }
        return response


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    responses={200: OpenApiResponse(description="Check if movie is favorited")},
    summary="Check favorite status",
    description="Check if a specific movie is in the user's favorites.",
)
def check_favorite_status(request, movie_id):
    """Check if a movie is in user's favorites."""
    try:
        movie = get_object_or_404(Movie, id=movie_id)
        is_favorite = UserFavorite.objects.filter(
            user=request.user, movie=movie
        ).exists()

        favorite_data = None
        if is_favorite:
            favorite = UserFavorite.objects.get(user=request.user, movie=movie)
            favorite_data = UserFavoriteSerializer(favorite).data

        return Response(
            {
                "success": True,
                "message": "Favorite status retrieved successfully",
                "data": {
                    "is_favorite": is_favorite,
                    "movie_id": movie_id,
                    "favorite_details": favorite_data,
                },
            },
            status=status.HTTP_200_OK,
        )

    except Movie.DoesNotExist:
        return Response(
            {"success": False, "message": "Movie not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
