"""
TMDb API Client for Movie Recommendation Backend

This module provides a comprehensive client for interacting with The Movie Database (TMDb) API.
It handles authentication, rate limiting, error handling, and caching for optimal performance.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class TMDbAPIError(Exception):
    """Custom exception for TMDb API errors."""

    pass


class TMDbRateLimitError(TMDbAPIError):
    """Exception raised when API rate limit is exceeded."""

    pass


class TMDbClient:
    """
    TMDb API Client with comprehensive error handling and caching.

    This client provides methods to interact with TMDb API endpoints,
    handles authentication, implements rate limiting, and caches responses
    for optimal performance.
    """

    BASE_URL = "https://api.themoviedb.org/3/"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/"

    # Cache timeouts (in seconds)
    CACHE_TIMEOUTS = {
        "trending": 30 * 60,  # 30 minutes
        "popular": 60 * 60,  # 1 hour
        "movie_details": 24 * 60 * 60,  # 24 hours
        "genres": 24 * 60 * 60,  # 24 hours
        "search": 15 * 60,  # 15 minutes
    }

    # Rate limiting
    RATE_LIMIT_REQUESTS = 40  # TMDb allows 40 requests per 10 seconds
    RATE_LIMIT_WINDOW = 10  # 10 seconds

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize TMDb client.

        Args:
            api_key: TMDb API key. If not provided, will use settings.TMDB_API_KEY
        """
        self.api_key = api_key or getattr(settings, "TMDB_API_KEY", None)
        if not self.api_key:
            logger.warning(
                "TMDB_API_KEY not configured. TMDb functionality will be limited."
            )

        self.session = requests.Session()
        self.session.params = {"api_key": self.api_key} if self.api_key else {}

        # Rate limiting tracking
        self._request_times = []

    def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting."""
        current_time = time.time()

        # Remove old requests outside the window
        self._request_times = [
            req_time
            for req_time in self._request_times
            if current_time - req_time < self.RATE_LIMIT_WINDOW
        ]

        # Check if we're at the limit
        if len(self._request_times) >= self.RATE_LIMIT_REQUESTS:
            sleep_time = self.RATE_LIMIT_WINDOW - (
                current_time - self._request_times[0]
            )
            if sleep_time > 0:
                logger.info(
                    f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds."
                )
                time.sleep(sleep_time)

        # Add current request time
        self._request_times.append(current_time)

    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        cache_key: Optional[str] = None,
        cache_timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Make a request to TMDb API with error handling and caching.

        Args:
            endpoint: API endpoint path
            params: Additional query parameters
            cache_key: Cache key for storing response
            cache_timeout: Cache timeout in seconds

        Returns:
            API response data

        Raises:
            TMDbAPIError: If API request fails
            TMDbRateLimitError: If rate limit is exceeded
        """
        if not self.api_key:
            raise TMDbAPIError("TMDb API key not configured")

        # Check cache first
        if cache_key:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_data

        # Check rate limit
        self._check_rate_limit()

        # Prepare request
        url = urljoin(self.BASE_URL, endpoint)
        request_params = params or {}

        response = None
        try:
            logger.debug(f"Making request to: {url} with params: {request_params}")
            response = self.session.get(url, params=request_params, timeout=10)

            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 10))
                logger.warning(f"Rate limited. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
                raise TMDbRateLimitError(
                    f"Rate limited. Retry after {retry_after} seconds."
                )

            # Handle other errors
            response.raise_for_status()

            data = response.json()

            # Cache successful response
            if cache_key and cache_timeout:
                cache.set(cache_key, data, cache_timeout)
                logger.debug(
                    f"Cached response with key: {cache_key} for {cache_timeout} seconds"
                )

            return data

        except requests.exceptions.Timeout:
            logger.error(f"Timeout occurred for request to {url}")
            raise TMDbAPIError("Request timeout")
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for request to {url}")
            raise TMDbAPIError("Connection error")
        except requests.exceptions.HTTPError as e:
            status_code = response.status_code if response else "Unknown"
            logger.error(f"HTTP error {status_code} for request to {url}: {e}")
            raise TMDbAPIError(f"HTTP error: {status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            raise TMDbAPIError(f"Request error: {str(e)}")
        except ValueError as e:
            logger.error(f"Invalid JSON response from {url}: {e}")
            raise TMDbAPIError("Invalid JSON response")

    def get_trending_movies(
        self, time_window: str = "day", page: int = 1
    ) -> Dict[str, Any]:
        """
        Get trending movies.

        Args:
            time_window: 'day' or 'week'
            page: Page number (1-indexed)

        Returns:
            Trending movies data
        """
        cache_key = f"trending_movies_{time_window}_{page}"
        endpoint = f"trending/movie/{time_window}"
        params = {"page": page}

        return self._make_request(
            endpoint, params, cache_key, self.CACHE_TIMEOUTS["trending"]
        )

    def get_popular_movies(self, page: int = 1) -> Dict[str, Any]:
        """
        Get popular movies.

        Args:
            page: Page number (1-indexed)

        Returns:
            Popular movies data
        """
        cache_key = f"popular_movies_{page}"
        endpoint = "movie/popular"
        params = {"page": page}

        return self._make_request(
            endpoint, params, cache_key, self.CACHE_TIMEOUTS["popular"]
        )

    def get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific movie.

        Args:
            movie_id: TMDb movie ID

        Returns:
            Movie details data
        """
        cache_key = f"movie_details_{movie_id}"
        endpoint = f"movie/{movie_id}"
        params = {
            "append_to_response": "credits,videos,images,keywords,recommendations"
        }

        return self._make_request(
            endpoint, params, cache_key, self.CACHE_TIMEOUTS["movie_details"]
        )

    def search_movies(
        self,
        query: str,
        page: int = 1,
        year: Optional[int] = None,
        include_adult: bool = False,
    ) -> Dict[str, Any]:
        """
        Search for movies.

        Args:
            query: Search query
            page: Page number (1-indexed)
            year: Filter by release year
            include_adult: Include adult content

        Returns:
            Search results data
        """
        cache_key = f"search_movies_{hash(query)}_{page}_{year}_{include_adult}"
        endpoint = "search/movie"
        params = {"query": query, "page": page, "include_adult": include_adult}

        if year:
            params["year"] = year

        return self._make_request(
            endpoint, params, cache_key, self.CACHE_TIMEOUTS["search"]
        )

    def get_genres(self) -> Dict[str, Any]:
        """
        Get list of movie genres.

        Returns:
            Genres data
        """
        cache_key = "movie_genres"
        endpoint = "genre/movie/list"

        return self._make_request(
            endpoint, cache_key=cache_key, cache_timeout=self.CACHE_TIMEOUTS["genres"]
        )

    def get_top_rated_movies(self, page: int = 1) -> Dict[str, Any]:
        """
        Get top rated movies.

        Args:
            page: Page number (1-indexed)

        Returns:
            Top rated movies data
        """
        cache_key = f"top_rated_movies_{page}"
        endpoint = "movie/top_rated"
        params = {"page": page}

        return self._make_request(
            endpoint, params, cache_key, self.CACHE_TIMEOUTS["popular"]
        )

    def get_now_playing_movies(self, page: int = 1) -> Dict[str, Any]:
        """
        Get movies currently in theaters.

        Args:
            page: Page number (1-indexed)

        Returns:
            Now playing movies data
        """
        cache_key = f"now_playing_movies_{page}"
        endpoint = "movie/now_playing"
        params = {"page": page}

        return self._make_request(
            endpoint, params, cache_key, self.CACHE_TIMEOUTS["trending"]
        )

    def get_upcoming_movies(self, page: int = 1) -> Dict[str, Any]:
        """
        Get upcoming movies.

        Args:
            page: Page number (1-indexed)

        Returns:
            Upcoming movies data
        """
        cache_key = f"upcoming_movies_{page}"
        endpoint = "movie/upcoming"
        params = {"page": page}

        return self._make_request(
            endpoint, params, cache_key, self.CACHE_TIMEOUTS["trending"]
        )

    def discover_movies(
        self,
        page: int = 1,
        genre_ids: Optional[List[int]] = None,
        sort_by: str = "popularity.desc",
        min_vote_average: Optional[float] = None,
        min_vote_count: Optional[int] = None,
        year: Optional[int] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Discover movies based on criteria.

        Args:
            page: Page number (1-indexed)
            genre_ids: List of genre IDs to filter by
            sort_by: Sort criteria
            min_vote_average: Minimum vote average
            min_vote_count: Minimum vote count
            year: Release year
            **kwargs: Additional discovery parameters

        Returns:
            Discovered movies data
        """
        params = {"page": page, "sort_by": sort_by, **kwargs}

        if genre_ids:
            params["with_genres"] = ",".join(map(str, genre_ids))
        if min_vote_average:
            params["vote_average.gte"] = min_vote_average
        if min_vote_count:
            params["vote_count.gte"] = min_vote_count
        if year:
            params["year"] = year

        # Create cache key from sorted params
        cache_key = f"discover_movies_{hash(str(sorted(params.items())))}"
        endpoint = "discover/movie"

        return self._make_request(
            endpoint, params, cache_key, self.CACHE_TIMEOUTS["search"]
        )

    @staticmethod
    def get_image_url(path: str, size: str = "w500", secure: bool = True) -> str:
        """
        Get full URL for TMDb image.

        Args:
            path: Image path from TMDb response
            size: Image size (w92, w154, w185, w342, w500, w780, original)
            secure: Use HTTPS

        Returns:
            Full image URL
        """
        if not path:
            return ""

        base_url = TMDbClient.IMAGE_BASE_URL
        if secure:
            base_url = base_url.replace("http://", "https://")

        return f"{base_url}{size}{path}"

    def get_movie_videos(self, movie_id: int) -> Dict[str, Any]:
        """
        Get videos (trailers, teasers, etc.) for a movie.

        Args:
            movie_id: TMDb movie ID

        Returns:
            Movie videos data
        """
        cache_key = f"movie_videos_{movie_id}"
        endpoint = f"movie/{movie_id}/videos"

        return self._make_request(
            endpoint,
            cache_key=cache_key,
            cache_timeout=self.CACHE_TIMEOUTS["movie_details"],
        )

    def get_movie_credits(self, movie_id: int) -> Dict[str, Any]:
        """
        Get cast and crew information for a movie.

        Args:
            movie_id: TMDb movie ID

        Returns:
            Movie credits data
        """
        cache_key = f"movie_credits_{movie_id}"
        endpoint = f"movie/{movie_id}/credits"

        return self._make_request(
            endpoint,
            cache_key=cache_key,
            cache_timeout=self.CACHE_TIMEOUTS["movie_details"],
        )

    def get_movie_recommendations(self, movie_id: int, page: int = 1) -> Dict[str, Any]:
        """
        Get movie recommendations based on a specific movie.

        Args:
            movie_id: TMDb movie ID
            page: Page number (1-indexed)

        Returns:
            Movie recommendations data
        """
        cache_key = f"movie_recommendations_{movie_id}_{page}"
        endpoint = f"movie/{movie_id}/recommendations"
        params = {"page": page}

        return self._make_request(
            endpoint, params, cache_key, self.CACHE_TIMEOUTS["search"]
        )

    def get_similar_movies(self, movie_id: int, page: int = 1) -> Dict[str, Any]:
        """
        Get movies similar to a specific movie.

        Args:
            movie_id: TMDb movie ID
            page: Page number (1-indexed)

        Returns:
            Similar movies data
        """
        cache_key = f"similar_movies_{movie_id}_{page}"
        endpoint = f"movie/{movie_id}/similar"
        params = {"page": page}

        return self._make_request(
            endpoint, params, cache_key, self.CACHE_TIMEOUTS["search"]
        )


# Global client instance
tmdb_client = TMDbClient()


def get_tmdb_client() -> TMDbClient:
    """
    Get TMDb client instance.

    Returns:
        TMDbClient instance
    """
    return tmdb_client
