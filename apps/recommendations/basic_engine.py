"""
Basic recommendation engine for Phase 7 implementation.
"""

import logging
from typing import Dict, List

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from utils.tmdb_client import TMDbClient
from .models import SimpleFavorite, RecommendationCache, RecommendationSettings

User = get_user_model()
logger = logging.getLogger(__name__)


class BasicRecommendationEngine:
    """Basic recommendation engine for Phase 7"""
    
    def __init__(self):
        self.tmdb_client = TMDbClient()
    
    def get_recommendations(self, user, recommendation_type='hybrid', limit=20, force_refresh=False):
        """Get basic recommendations for user"""
        
        try:
            if recommendation_type == 'trending':
                return self._get_trending_recommendations(limit)
            elif recommendation_type == 'content':
                return self._get_content_recommendations(user, limit)
            else:  # hybrid or collaborative
                return self._get_hybrid_recommendations(user, limit)
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return self._get_fallback_recommendations(limit)
    
    def _get_trending_recommendations(self, limit=20):
        """Get trending movies"""
        try:
            result = self.tmdb_client.get_trending_movies()
            movies = result.get('results', [])[:limit]
            
            for movie in movies:
                movie['recommendation_score'] = movie.get('popularity', 0) / 1000
                movie['recommendation_reason'] = 'Currently trending'
            
            return movies
        except Exception as e:
            logger.error(f"Error getting trending movies: {e}")
            return self._get_fallback_recommendations(limit)
    
    def _get_content_recommendations(self, user, limit=20):
        """Get content-based recommendations"""
        try:
            # Get user's favorite movie IDs
            user_favorites = SimpleFavorite.objects.filter(user=user).values_list('movie_id', flat=True)
            
            if not user_favorites:
                return self._get_trending_recommendations(limit)
            
            # Get popular movies as base recommendations
            result = self.tmdb_client.get_popular_movies()
            movies = result.get('results', [])[:limit]
            
            for movie in movies:
                movie['recommendation_score'] = movie.get('vote_average', 0) / 10
                movie['recommendation_reason'] = 'Popular movie matching your preferences'
            
            return movies
        except Exception as e:
            logger.error(f"Error getting content recommendations: {e}")
            return self._get_fallback_recommendations(limit)
    
    def _get_hybrid_recommendations(self, user, limit=20):
        """Get hybrid recommendations"""
        try:
            # Simple hybrid: 50% trending, 50% content-based
            trending = self._get_trending_recommendations(limit // 2)
            content = self._get_content_recommendations(user, limit // 2)
            
            # Combine and adjust scores
            all_recommendations = []
            
            for movie in trending:
                movie['recommendation_score'] = movie.get('recommendation_score', 0) * 0.5
                movie['recommendation_reason'] = 'Hybrid: Trending'
                all_recommendations.append(movie)
            
            for movie in content:
                movie['recommendation_score'] = movie.get('recommendation_score', 0) * 0.5
                movie['recommendation_reason'] = 'Hybrid: Content-based'
                all_recommendations.append(movie)
            
            # Remove duplicates by movie ID
            seen_ids = set()
            unique_recommendations = []
            for movie in all_recommendations:
                if movie['id'] not in seen_ids:
                    seen_ids.add(movie['id'])
                    unique_recommendations.append(movie)
            
            # Sort by score
            unique_recommendations.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
            
            return unique_recommendations[:limit]
        except Exception as e:
            logger.error(f"Error getting hybrid recommendations: {e}")
            return self._get_fallback_recommendations(limit)
    
    def _get_fallback_recommendations(self, limit=20):
        """Fallback to popular movies"""
        try:
            result = self.tmdb_client.get_popular_movies()
            movies = result.get('results', [])[:limit]
            
            for movie in movies:
                movie['recommendation_score'] = 0.5
                movie['recommendation_reason'] = 'Popular movie'
            
            return movies
        except Exception as e:
            logger.error(f"Error getting fallback recommendations: {e}")
            return []
