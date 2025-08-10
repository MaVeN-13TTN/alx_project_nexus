"""
Movie API Views

This module contains Django REST Framework views for movie-related endpoints.
Provides comprehensive movie data access with TMDb integration.
"""

import logging
from typing import Dict, Any, Union

from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from django.http import Http404
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.movies.models import Movie, Genre
from apps.movies.serializers import (
    MovieListSerializer,
    MovieDetailSerializer,
    GenreSerializer,
    TMDbMovieSerializer,
    MovieSearchSerializer,
    MovieDiscoverSerializer,
    MovieTrendingSerializer,
    MoviePopularSerializer,
    MovieFilterSerializer,
    PaginatedResponseSerializer,
    ErrorResponseSerializer,
)
from apps.movies.services import get_movie_service
from utils.tmdb_client import TMDbAPIError

logger = logging.getLogger(__name__)


class MovieListView(generics.ListAPIView):
    """
    List movies from local database with filtering and pagination.
    """

    serializer_class = MovieListSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Movies"],
        summary="List movies from database",
        description="Get paginated list of movies from local database with optional filtering",
        parameters=[
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number for pagination",
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Number of movies per page (max 100)",
            ),
            OpenApiParameter(
                name="genre_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by genre TMDb ID",
            ),
            OpenApiParameter(
                name="min_vote_average",
                type=OpenApiTypes.FLOAT,
                location=OpenApiParameter.QUERY,
                description="Minimum vote average (0.0-10.0)",
            ),
            OpenApiParameter(
                name="sort_by",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Sort field: popularity, vote_average, release_date, title (prefix with - for descending)",
            ),
        ],
        responses={200: PaginatedResponseSerializer, 400: ErrorResponseSerializer},
    )
    def get(self, request: Request, *args, **kwargs) -> Response:
        # Validate query parameters
        filter_serializer = MovieFilterSerializer(data=request.query_params)
        if not filter_serializer.is_valid():
            return Response(
                {
                    "error": "Invalid parameters",
                    "message": "One or more query parameters are invalid",
                    "details": filter_serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            movie_service = get_movie_service()
            validated_data = filter_serializer.validated_data or {}
            movies_data = movie_service.get_local_movies(
                page=validated_data.get("page", 1),
                page_size=validated_data.get("page_size", 20),
                genre_id=validated_data.get("genre_id"),
                min_vote_average=validated_data.get("min_vote_average"),
                sort_by=validated_data.get("sort_by", "-popularity"),
            )

            # Serialize movies
            movies_serializer = self.serializer_class(movies_data["movies"], many=True)

            response_data = {
                "page": movies_data["page"],
                "total_pages": movies_data["total_pages"],
                "total_results": movies_data["total_movies"],
                "results": movies_serializer.data,
                "has_next": movies_data["has_next"],
                "has_previous": movies_data["has_previous"],
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error retrieving movies: {e}")
            return Response(
                {
                    "error": "Internal server error",
                    "message": "Failed to retrieve movies",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MovieDetailView(generics.RetrieveAPIView):
    """
    Get detailed information about a specific movie.
    """

    serializer_class = MovieDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "tmdb_id"

    @extend_schema(
        tags=["Movies"],
        summary="Get movie details",
        description="Get detailed information about a specific movie by TMDb ID",
        responses={
            200: MovieDetailSerializer,
            404: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
    )
    def get_object(self) -> Movie:
        tmdb_id = self.kwargs.get("tmdb_id")

        try:
            # Try to get from local database first
            movie = Movie.objects.prefetch_related("genres").get(tmdb_id=tmdb_id)
            return movie
        except Movie.DoesNotExist:
            # If not in database, try to fetch from TMDb
            movie_service = get_movie_service()
            movie = movie_service.fetch_movie_details_from_tmdb(tmdb_id)

            if not movie:
                raise Http404(f"Movie with TMDb ID {tmdb_id} not found")

            return movie


@api_view(["GET"])
@permission_classes([AllowAny])
@extend_schema(
    tags=["Movies"],
    summary="Get trending movies",
    description="Get trending movies from TMDb API",
    parameters=[
        OpenApiParameter(
            name="time_window",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Time window: day or week",
            enum=["day", "week"],
        ),
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Page number for pagination",
        ),
    ],
    responses={
        200: PaginatedResponseSerializer,
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer,
    },
)
def trending_movies(request: Request) -> Response:
    """Get trending movies from TMDb API."""
    # Validate parameters
    serializer = MovieTrendingSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(
            {
                "error": "Invalid parameters",
                "message": "One or more query parameters are invalid",
                "details": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        movie_service = get_movie_service()
        validated_data = serializer.validated_data or {}
        time_window = validated_data.get("time_window", "day")
        page = validated_data.get("page", 1)

        # Check cache first
        cache_key = f"trending_movies_api_{time_window}_{page}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        # Fetch from TMDb API
        trending_data = movie_service.tmdb_client.get_trending_movies(time_window, page)

        # Serialize results
        movies_serializer = TMDbMovieSerializer(
            trending_data.get("results", []), many=True
        )

        response_data = {
            "page": trending_data.get("page", 1),
            "total_pages": trending_data.get("total_pages", 1),
            "total_results": trending_data.get("total_results", 0),
            "results": movies_serializer.data,
        }

        # Cache for 15 minutes
        cache.set(cache_key, response_data, 15 * 60)

        return Response(response_data, status=status.HTTP_200_OK)

    except TMDbAPIError as e:
        logger.error(f"TMDb API error for trending movies: {e}")
        return Response(
            {
                "error": "External API error",
                "message": "Failed to fetch trending movies from TMDb",
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except Exception as e:
        logger.error(f"Unexpected error for trending movies: {e}")
        return Response(
            {
                "error": "Internal server error",
                "message": "Failed to retrieve trending movies",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
@extend_schema(
    tags=["Movies"],
    summary="Get popular movies",
    description="Get popular movies from TMDb API",
    parameters=[
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Page number for pagination",
        ),
    ],
    responses={
        200: PaginatedResponseSerializer,
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer,
    },
)
def popular_movies(request: Request) -> Response:
    """Get popular movies from TMDb API."""
    # Validate parameters
    serializer = MoviePopularSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(
            {
                "error": "Invalid parameters",
                "message": "One or more query parameters are invalid",
                "details": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        movie_service = get_movie_service()
        validated_data = serializer.validated_data or {}
        page = validated_data.get("page", 1)

        # Check cache first
        cache_key = f"popular_movies_api_{page}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        # Fetch from TMDb API
        popular_data = movie_service.tmdb_client.get_popular_movies(page)

        # Serialize results
        movies_serializer = TMDbMovieSerializer(
            popular_data.get("results", []), many=True
        )

        response_data = {
            "page": popular_data.get("page", 1),
            "total_pages": popular_data.get("total_pages", 1),
            "total_results": popular_data.get("total_results", 0),
            "results": movies_serializer.data,
        }

        # Cache for 30 minutes
        cache.set(cache_key, response_data, 30 * 60)

        return Response(response_data, status=status.HTTP_200_OK)

    except TMDbAPIError as e:
        logger.error(f"TMDb API error for popular movies: {e}")
        return Response(
            {
                "error": "External API error",
                "message": "Failed to fetch popular movies from TMDb",
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except Exception as e:
        logger.error(f"Unexpected error for popular movies: {e}")
        return Response(
            {
                "error": "Internal server error",
                "message": "Failed to retrieve popular movies",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
@extend_schema(
    summary="Search movies",
    description="Search for movies using TMDb API",
    parameters=[
        OpenApiParameter(
            name="query",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search query for movie titles",
            required=True,
        ),
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Page number for pagination",
        ),
        OpenApiParameter(
            name="year",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter by release year",
        ),
        OpenApiParameter(
            name="include_adult",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="Include adult content in results",
        ),
    ],
    responses={
        200: PaginatedResponseSerializer,
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer,
    },
)
def search_movies(request: Request) -> Response:
    """Search for movies using TMDb API."""
    # Validate parameters
    serializer = MovieSearchSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(
            {
                "error": "Invalid parameters",
                "message": "One or more query parameters are invalid",
                "details": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        movie_service = get_movie_service()
        validated_data = serializer.validated_data or {}
        search_data = movie_service.search_movies(
            query=validated_data.get("query", ""),
            page=validated_data.get("page", 1),
            year=validated_data.get("year"),
            store_results=False,
        )

        # Serialize results
        movies_serializer = TMDbMovieSerializer(
            search_data.get("results", []), many=True
        )

        response_data = {
            "page": search_data.get("page", 1),
            "total_pages": search_data.get("total_pages", 1),
            "total_results": search_data.get("total_results", 0),
            "results": movies_serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except TMDbAPIError as e:
        logger.error(f"TMDb API error for movie search: {e}")
        return Response(
            {
                "error": "External API error",
                "message": "Failed to search movies in TMDb",
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except Exception as e:
        logger.error(f"Unexpected error for movie search: {e}")
        return Response(
            {"error": "Internal server error", "message": "Failed to search movies"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
@extend_schema(
    summary="Discover movies",
    description="Discover movies based on criteria using TMDb API",
    parameters=[
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Page number for pagination",
        ),
        OpenApiParameter(
            name="genre_ids",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Comma-separated list of genre IDs",
        ),
        OpenApiParameter(
            name="sort_by",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Sort criteria for results",
        ),
        OpenApiParameter(
            name="min_vote_average",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description="Minimum vote average",
        ),
        OpenApiParameter(
            name="year",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter by release year",
        ),
    ],
    responses={
        200: PaginatedResponseSerializer,
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer,
    },
)
def discover_movies(request: Request) -> Response:
    """Discover movies based on criteria using TMDb API."""
    # Validate parameters
    serializer = MovieDiscoverSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(
            {
                "error": "Invalid parameters",
                "message": "One or more query parameters are invalid",
                "details": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        movie_service = get_movie_service()
        validated_data = serializer.validated_data or {}
        discover_data = movie_service.discover_movies(
            page=validated_data.get("page", 1),
            genre_ids=validated_data.get("genre_ids"),
            sort_by=validated_data.get("sort_by", "popularity.desc"),
            min_vote_average=validated_data.get("min_vote_average"),
            year=validated_data.get("year"),
            store_results=False,
        )

        # Serialize results
        movies_serializer = TMDbMovieSerializer(
            discover_data.get("results", []), many=True
        )

        response_data = {
            "page": discover_data.get("page", 1),
            "total_pages": discover_data.get("total_pages", 1),
            "total_results": discover_data.get("total_results", 0),
            "results": movies_serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except TMDbAPIError as e:
        logger.error(f"TMDb API error for movie discovery: {e}")
        return Response(
            {
                "error": "External API error",
                "message": "Failed to discover movies in TMDb",
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except Exception as e:
        logger.error(f"Unexpected error for movie discovery: {e}")
        return Response(
            {"error": "Internal server error", "message": "Failed to discover movies"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class GenreListView(generics.ListAPIView):
    """
    List all movie genres.
    """

    queryset = Genre.objects.all().order_by("name")
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="List movie genres",
        description="Get list of all movie genres from database",
        responses={200: GenreSerializer(many=True), 500: ErrorResponseSerializer},
    )
    @method_decorator(cache_page(60 * 60))  # Cache for 1 hour
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@api_view(["POST"])
@permission_classes([AllowAny])
@extend_schema(
    summary="Sync genres from TMDb",
    description="Sync movie genres from TMDb API to local database",
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "created_count": {"type": "integer"},
                "updated_count": {"type": "integer"},
            },
        },
        500: ErrorResponseSerializer,
    },
)
def sync_genres(request: Request) -> Response:
    """Sync genres from TMDb API to local database."""
    try:
        movie_service = get_movie_service()
        created_count, updated_count = movie_service.sync_genres_from_tmdb()

        return Response(
            {
                "message": "Genres synced successfully",
                "created_count": created_count,
                "updated_count": updated_count,
            },
            status=status.HTTP_200_OK,
        )

    except TMDbAPIError as e:
        logger.error(f"TMDb API error for genre sync: {e}")
        return Response(
            {
                "error": "External API error",
                "message": "Failed to sync genres from TMDb",
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except Exception as e:
        logger.error(f"Unexpected error for genre sync: {e}")
        return Response(
            {"error": "Internal server error", "message": "Failed to sync genres"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
