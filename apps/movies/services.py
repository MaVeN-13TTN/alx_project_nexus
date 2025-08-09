"""
Movie Services for TMDb Integration

Th                for genre_data in genres_list:
                    genre, created = Genre.objects.update_or_create(
                        tmdb_id=genre_data['id'],
                        defaults={
                            'name': genre_data['name']
                        }
                    )e provides service layer functions for movie data operations,
including fetching from TMDb API, caching, and database synchronization.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError

from apps.movies.models import Movie, Genre
from utils.tmdb_client import get_tmdb_client, TMDbAPIError

logger = logging.getLogger(__name__)


class MovieService:
    """Service class for movie-related operations."""

    def __init__(self):
        self.tmdb_client = get_tmdb_client()

    def sync_genres_from_tmdb(self) -> Tuple[int, int]:
        """
        Sync genres from TMDb API to local database.

        Returns:
            Tuple of (created_count, updated_count)
        """
        try:
            genres_data = self.tmdb_client.get_genres()
            genres_list = genres_data.get("genres", [])

            created_count = 0
            updated_count = 0

            with transaction.atomic():
                for genre_data in genres_list:
                    genre, created = Genre.objects.update_or_create(
                        tmdb_id=genre_data["id"],
                        defaults={
                            "name": genre_data["name"],
                        },
                    )

                    if created:
                        created_count += 1
                        logger.info(f"Created new genre: {genre.name}")
                    else:
                        updated_count += 1
                        logger.debug(f"Updated genre: {genre.name}")

            logger.info(
                f"Genre sync completed: {created_count} created, {updated_count} updated"
            )
            return created_count, updated_count

        except TMDbAPIError as e:
            logger.error(f"Failed to sync genres from TMDb: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during genre sync: {e}")
            raise

    def create_or_update_movie_from_tmdb(
        self, tmdb_movie_data: Dict[str, Any]
    ) -> Movie:
        """
        Create or update a movie from TMDb data.

        Args:
            tmdb_movie_data: Movie data from TMDb API

        Returns:
            Movie instance
        """
        try:
            # Parse release date
            release_date = None
            if tmdb_movie_data.get("release_date"):
                try:
                    release_date = datetime.strptime(
                        tmdb_movie_data["release_date"], "%Y-%m-%d"
                    ).date()
                except ValueError:
                    logger.warning(
                        f"Invalid release date format: {tmdb_movie_data.get('release_date')}"
                    )

            # Create or update movie
            movie, created = Movie.objects.update_or_create(
                tmdb_id=tmdb_movie_data["id"],
                defaults={
                    "title": tmdb_movie_data.get("title", ""),
                    "overview": tmdb_movie_data.get("overview", ""),
                    "release_date": release_date,
                    "poster_path": tmdb_movie_data.get("poster_path", ""),
                    "backdrop_path": tmdb_movie_data.get("backdrop_path", ""),
                    "vote_average": tmdb_movie_data.get("vote_average", 0.0),
                    "vote_count": tmdb_movie_data.get("vote_count", 0),
                    "popularity": tmdb_movie_data.get("popularity", 0.0),
                    "original_language": tmdb_movie_data.get("original_language", ""),
                    "original_title": tmdb_movie_data.get("original_title", ""),
                    "adult": tmdb_movie_data.get("adult", False),
                    "video": tmdb_movie_data.get("video", False),
                    "updated_at": timezone.now(),
                },
            )

            # Handle genres
            if "genre_ids" in tmdb_movie_data:
                # From lists (trending, popular, etc.)
                genre_ids = tmdb_movie_data["genre_ids"]
                genres = Genre.objects.filter(tmdb_id__in=genre_ids)
                movie.genres.set(genres)
            elif "genres" in tmdb_movie_data:
                # From movie details
                genre_tmdb_ids = [g["id"] for g in tmdb_movie_data["genres"]]
                genres = Genre.objects.filter(tmdb_id__in=genre_tmdb_ids)
                movie.genres.set(genres)

            if created:
                logger.info(f"Created new movie: {movie.title}")
            else:
                logger.debug(f"Updated movie: {movie.title}")

            return movie

        except Exception as e:
            logger.error(f"Error creating/updating movie from TMDb data: {e}")
            raise

    def fetch_and_store_trending_movies(
        self, time_window: str = "day", page: int = 1
    ) -> List[Movie]:
        """
        Fetch trending movies from TMDb and store in database.

        Args:
            time_window: 'day' or 'week'
            page: Page number

        Returns:
            List of Movie instances
        """
        try:
            trending_data = self.tmdb_client.get_trending_movies(time_window, page)
            movies = []

            with transaction.atomic():
                for movie_data in trending_data.get("results", []):
                    movie = self.create_or_update_movie_from_tmdb(movie_data)
                    movies.append(movie)

            logger.info(f"Fetched and stored {len(movies)} trending movies")
            return movies

        except TMDbAPIError as e:
            logger.error(f"Failed to fetch trending movies: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching trending movies: {e}")
            raise

    def fetch_and_store_popular_movies(self, page: int = 1) -> List[Movie]:
        """
        Fetch popular movies from TMDb and store in database.

        Args:
            page: Page number

        Returns:
            List of Movie instances
        """
        try:
            popular_data = self.tmdb_client.get_popular_movies(page)
            movies = []

            with transaction.atomic():
                for movie_data in popular_data.get("results", []):
                    movie = self.create_or_update_movie_from_tmdb(movie_data)
                    movies.append(movie)

            logger.info(f"Fetched and stored {len(movies)} popular movies")
            return movies

        except TMDbAPIError as e:
            logger.error(f"Failed to fetch popular movies: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching popular movies: {e}")
            raise

    def fetch_movie_details_from_tmdb(self, movie_id: int) -> Optional[Movie]:
        """
        Fetch detailed movie information from TMDb and update database.

        Args:
            movie_id: TMDb movie ID

        Returns:
            Movie instance or None if not found
        """
        try:
            movie_data = self.tmdb_client.get_movie_details(movie_id)

            with transaction.atomic():
                movie = self.create_or_update_movie_from_tmdb(movie_data)

            logger.info(f"Fetched and updated movie details: {movie.title}")
            return movie

        except TMDbAPIError as e:
            logger.error(f"Failed to fetch movie details for ID {movie_id}: {e}")
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error fetching movie details for ID {movie_id}: {e}"
            )
            return None

    def search_movies(
        self,
        query: str,
        page: int = 1,
        year: Optional[int] = None,
        store_results: bool = False,
    ) -> Dict[str, Any]:
        """
        Search for movies using TMDb API.

        Args:
            query: Search query
            page: Page number
            year: Filter by release year
            store_results: Whether to store results in database

        Returns:
            Search results with metadata
        """
        try:
            search_data = self.tmdb_client.search_movies(query, page, year)

            results = search_data.get("results", [])

            # Optionally store results in database
            if store_results and results:
                with transaction.atomic():
                    for movie_data in results:
                        self.create_or_update_movie_from_tmdb(movie_data)
                logger.info(f"Stored {len(results)} search results in database")

            return {
                "results": results,
                "page": search_data.get("page", 1),
                "total_pages": search_data.get("total_pages", 1),
                "total_results": search_data.get("total_results", 0),
            }

        except TMDbAPIError as e:
            logger.error(f"Failed to search movies with query '{query}': {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error searching movies with query '{query}': {e}")
            raise

    def discover_movies(
        self,
        page: int = 1,
        genre_ids: Optional[List[int]] = None,
        sort_by: str = "popularity.desc",
        min_vote_average: Optional[float] = None,
        min_vote_count: Optional[int] = None,
        year: Optional[int] = None,
        store_results: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Discover movies based on criteria using TMDb API.

        Args:
            page: Page number
            genre_ids: List of genre IDs to filter by
            sort_by: Sort criteria
            min_vote_average: Minimum vote average
            min_vote_count: Minimum vote count
            year: Release year
            store_results: Whether to store results in database
            **kwargs: Additional discovery parameters

        Returns:
            Discovery results with metadata
        """
        try:
            discover_data = self.tmdb_client.discover_movies(
                page=page,
                genre_ids=genre_ids,
                sort_by=sort_by,
                min_vote_average=min_vote_average,
                min_vote_count=min_vote_count,
                year=year,
                **kwargs,
            )

            results = discover_data.get("results", [])

            # Optionally store results in database
            if store_results and results:
                with transaction.atomic():
                    for movie_data in results:
                        self.create_or_update_movie_from_tmdb(movie_data)
                logger.info(f"Stored {len(results)} discovered movies in database")

            return {
                "results": results,
                "page": discover_data.get("page", 1),
                "total_pages": discover_data.get("total_pages", 1),
                "total_results": discover_data.get("total_results", 0),
            }

        except TMDbAPIError as e:
            logger.error(f"Failed to discover movies: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error discovering movies: {e}")
            raise

    def get_local_movies(
        self,
        page: int = 1,
        page_size: int = 20,
        genre_id: Optional[int] = None,
        min_vote_average: Optional[float] = None,
        sort_by: str = "popularity",
    ) -> Dict[str, Any]:
        """
        Get movies from local database with filtering and pagination.

        Args:
            page: Page number
            page_size: Number of movies per page
            genre_id: Filter by genre ID
            min_vote_average: Minimum vote average
            sort_by: Sort field ('popularity', 'vote_average', 'release_date', 'title')

        Returns:
            Paginated movies data
        """
        try:
            queryset = Movie.objects.all()

            # Apply filters
            if genre_id:
                queryset = queryset.filter(genres__tmdb_id=genre_id)

            if min_vote_average:
                queryset = queryset.filter(vote_average__gte=min_vote_average)

            # Apply sorting
            sort_fields = {
                "popularity": "-popularity",
                "vote_average": "-vote_average",
                "release_date": "-release_date",
                "title": "title",
                "-popularity": "-popularity",
                "-vote_average": "-vote_average",
                "-release_date": "-release_date",
                "-title": "-title",
            }

            sort_field = sort_fields.get(sort_by, "-popularity")
            queryset = queryset.order_by(sort_field)

            # Optimize database queries
            queryset = queryset.prefetch_related("genres")

            # Paginate
            paginator = Paginator(queryset, page_size)
            movies_page = paginator.get_page(page)

            return {
                "movies": list(movies_page),
                "page": page,
                "total_pages": paginator.num_pages,
                "total_movies": paginator.count,
                "has_next": movies_page.has_next(),
                "has_previous": movies_page.has_previous(),
            }

        except Exception as e:
            logger.error(f"Error retrieving local movies: {e}")
            raise

    def get_movie_recommendations(self, movie_id: int, page: int = 1) -> Dict[str, Any]:
        """
        Get movie recommendations from TMDb.

        Args:
            movie_id: TMDb movie ID
            page: Page number

        Returns:
            Recommendations data
        """
        try:
            recommendations_data = self.tmdb_client.get_movie_recommendations(
                movie_id, page
            )

            return {
                "results": recommendations_data.get("results", []),
                "page": recommendations_data.get("page", 1),
                "total_pages": recommendations_data.get("total_pages", 1),
                "total_results": recommendations_data.get("total_results", 0),
            }

        except TMDbAPIError as e:
            logger.error(f"Failed to get recommendations for movie {movie_id}: {e}")
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error getting recommendations for movie {movie_id}: {e}"
            )
            raise


# Global service instance
movie_service = MovieService()


def get_movie_service() -> MovieService:
    """
    Get movie service instance.

    Returns:
        MovieService instance
    """
    return movie_service
