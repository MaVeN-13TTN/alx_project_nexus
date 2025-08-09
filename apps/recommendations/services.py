"""
Recommendation algorithms for the movie recommendation system.

This module implements various recommendation strategies:
- Content-based filtering (genre, cast, director similarity)
- Collaborative filtering (user-based)
- Hybrid approach combining multiple strategies
- Trending and popular r        # From favorites
        favorites = SimpleFavorite.objects.filter(user=user)
        for favorite in favorites:
            try:
                movie_data = self.tmdb_client.get_movie_details(favorite.movie_id)
                for genre in movie_data.get('genres', []):
                    genre_scores[genre['id']] += 1.0
            except Exception:
                continue
        
        # From viewing history with rating weights
        viewing_history = SimpleViewingHistory.objects.filter(user=user)
        for history in viewing_history:
            try:
                movie_data = self.tmdb_client.get_movie_details(history.movie_id)
                weight = (history.rating or 5) / 10.0  # Normalize rating to 0-1
                for genre in movie_data.get('genres', []):
                    genre_scores[genre['id']] += weight
            except Exception:
                continueimport math
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from collections import defaultdict, Counter

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Q
from django.utils import timezone
from django.core.cache import cache

from apps.movies.services import MovieService
from apps.favorites.models import UserFavorite
from apps.preferences.models import UserPreference, ViewingHistory
# Use simple models for TMDb ID compatibility
from .models import SimpleFavorite, SimpleViewingHistory
from .models import (
    RecommendationCache, 
    UserSimilarity, 
    MovieSimilarity, 
    RecommendationSettings,
    RecommendationFeedback
)

User = get_user_model()
logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Main recommendation engine combining multiple strategies"""
    
    def __init__(self):
        self.movie_service = MovieService()
        # Access the TMDb client directly for some operations
        self.tmdb_client = self.movie_service.tmdb_client
    
    def get_recommendations(
        self, 
        user: User, 
        recommendation_type: str = 'hybrid',
        limit: int = 20,
        force_refresh: bool = False
    ) -> List[Dict]:
        """
        Get personalized recommendations for a user
        
        Args:
            user: User instance
            recommendation_type: Type of recommendation (content, collaborative, hybrid, trending)
            limit: Number of recommendations to return
            force_refresh: Force cache refresh
            
        Returns:
            List of movie dictionaries with recommendation scores
        """
        # Get user's recommendation settings
        settings = self._get_user_settings(user)
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_recommendations = self._get_cached_recommendations(user, recommendation_type)
            if cached_recommendations:
                return cached_recommendations[:limit]
        
        # Generate new recommendations based on type
        if recommendation_type == 'content':
            recommendations = self._content_based_recommendations(user, limit)
        elif recommendation_type == 'collaborative':
            recommendations = self._collaborative_filtering(user, limit)
        elif recommendation_type == 'trending':
            recommendations = self._trending_recommendations(user, limit)
        elif recommendation_type == 'similar':
            recommendations = self._similar_movie_recommendations(user, limit)
        else:  # hybrid
            recommendations = self._hybrid_recommendations(user, limit)
        
        # Apply user filters and preferences
        recommendations = self._apply_user_filters(recommendations, settings)
        
        # Cache the results
        self._cache_recommendations(user, recommendation_type, recommendations, settings)
        
        return recommendations[:limit]
    
    def _content_based_recommendations(self, user: User, limit: int = 20) -> List[Dict]:
        """Generate content-based recommendations based on user's favorites and viewing history"""
        
        # Get user's liked genres from favorites and viewing history
        user_genre_preferences = self._get_user_genre_preferences(user)
        
        if not user_genre_preferences:
            # Fallback to popular movies if no user data
            return self._get_popular_movies(limit)
        
        # Get movies similar to user's preferences
        recommendations = []
        
        # Use TMDb discover API with user's preferred genres
        preferred_genres = list(user_genre_preferences.keys())
        
        try:
            # Get movies from multiple genre combinations
            for genre_id in preferred_genres[:3]:  # Top 3 preferred genres
                movies = self.movie_service.discover_movies(
                    genre_ids=[genre_id],
                    sort_by='vote_average.desc',
                    page=1
                )
                
                for movie in movies.get('results', []):
                    # Calculate content-based score
                    score = self._calculate_content_score(movie, user_genre_preferences)
                    movie['recommendation_score'] = score
                    movie['recommendation_reason'] = f"Based on your interest in {self._get_genre_name(genre_id)}"
                    recommendations.append(movie)
        
        except Exception as e:
            logger.error(f"Error in content-based recommendations: {e}")
            return self._get_popular_movies(limit)
        
        # Remove duplicates and sort by score
        seen_ids = set()
        unique_recommendations = []
        for movie in recommendations:
            if movie['id'] not in seen_ids:
                seen_ids.add(movie['id'])
                unique_recommendations.append(movie)
        
        # Sort by recommendation score
        unique_recommendations.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
        
        return unique_recommendations[:limit]
    
    def _collaborative_filtering(self, user: User, limit: int = 20) -> List[Dict]:
        """Generate recommendations based on similar users' preferences"""
        
        # Find similar users based on favorites and viewing history
        similar_users = self._find_similar_users(user)
        
        if not similar_users:
            # Fallback to content-based if no similar users
            return self._content_based_recommendations(user, limit)
        
        # Get movie recommendations from similar users
        recommended_movie_ids = defaultdict(float)
        user_favorites = set(
            SimpleFavorite.objects.filter(user=user).values_list('movie_id', flat=True)
        )
        
        for similar_user_id, similarity_score in similar_users[:10]:  # Top 10 similar users
            similar_user = User.objects.get(id=similar_user_id)
            
            # Get their favorites
            similar_user_favorites = SimpleFavorite.objects.filter(
                user=similar_user
            ).exclude(movie_id__in=user_favorites)
            
            for favorite in similar_user_favorites:
                recommended_movie_ids[favorite.movie_id] += similarity_score
        
        # Get movie details and create recommendations
        recommendations = []
        
        for movie_id, score in sorted(recommended_movie_ids.items(), key=lambda x: x[1], reverse=True)[:limit * 2]:
            try:
                movie_data = self.tmdb_client.get_movie_details(movie_id)
                movie_data['recommendation_score'] = score
                movie_data['recommendation_reason'] = "Based on users with similar taste"
                recommendations.append(movie_data)
            except Exception as e:
                logger.warning(f"Could not get details for movie {movie_id}: {e}")
                continue
        
        return recommendations[:limit]
    
    def _hybrid_recommendations(self, user: User, limit: int = 20) -> List[Dict]:
        """Combine multiple recommendation strategies for better results"""
        
        # Get recommendations from different strategies
        content_recs = self._content_based_recommendations(user, limit // 2)
        collaborative_recs = self._collaborative_filtering(user, limit // 2)
        trending_recs = self._trending_recommendations(user, limit // 4)
        
        # Combine and weight the recommendations
        all_recommendations = []
        
        # Content-based (weight: 0.4)
        for movie in content_recs:
            movie['recommendation_score'] = movie.get('recommendation_score', 0) * 0.4
            movie['recommendation_reason'] = "Content-based: " + movie.get('recommendation_reason', '')
            all_recommendations.append(movie)
        
        # Collaborative filtering (weight: 0.4)
        for movie in collaborative_recs:
            movie['recommendation_score'] = movie.get('recommendation_score', 0) * 0.4
            movie['recommendation_reason'] = "Collaborative: " + movie.get('recommendation_reason', '')
            all_recommendations.append(movie)
        
        # Trending boost (weight: 0.2)
        for movie in trending_recs:
            movie['recommendation_score'] = movie.get('recommendation_score', 0) * 0.2
            movie['recommendation_reason'] = "Trending: " + movie.get('recommendation_reason', '')
            all_recommendations.append(movie)
        
        # Merge duplicates by summing scores
        movie_scores = defaultdict(lambda: {'movie': None, 'total_score': 0, 'reasons': []})
        
        for movie in all_recommendations:
            movie_id = movie['id']
            if movie_scores[movie_id]['movie'] is None:
                movie_scores[movie_id]['movie'] = movie
            movie_scores[movie_id]['total_score'] += movie.get('recommendation_score', 0)
            movie_scores[movie_id]['reasons'].append(movie.get('recommendation_reason', ''))
        
        # Create final recommendations
        final_recommendations = []
        for movie_id, data in movie_scores.items():
            movie = data['movie']
            movie['recommendation_score'] = data['total_score']
            movie['recommendation_reason'] = ' | '.join(set(data['reasons']))
            final_recommendations.append(movie)
        
        # Sort by total score
        final_recommendations.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
        
        return final_recommendations[:limit]
    
    def _trending_recommendations(self, user: User, limit: int = 20) -> List[Dict]:
        """Get trending movies with user preference filtering"""
        
        try:
            trending_movies = self.tmdb_client.get_trending_movies(time_window='week')
            
            recommendations = []
            for movie in trending_movies.get('results', []):
                movie['recommendation_score'] = movie.get('popularity', 0) / 1000  # Normalize
                movie['recommendation_reason'] = "Currently trending"
                recommendations.append(movie)
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error getting trending recommendations: {e}")
            return self._get_popular_movies(limit)
    
    def _similar_movie_recommendations(self, user: User, limit: int = 20) -> List[Dict]:
        """Get recommendations based on movies similar to user's favorites"""
        
        user_favorites = SimpleFavorite.objects.filter(user=user).values_list('movie_id', flat=True)
        
        if not user_favorites:
            return self._content_based_recommendations(user, limit)
        
        recommendations = []
        
        for favorite_movie_id in user_favorites[:5]:  # Use top 5 favorites
            try:
                similar_movies = self.tmdb_client.get_movie_recommendations(favorite_movie_id)
                
                for movie in similar_movies.get('results', []):
                    if movie['id'] not in user_favorites:  # Don't recommend already favorited movies
                        movie['recommendation_score'] = movie.get('vote_average', 0) / 10
                        movie['recommendation_reason'] = f"Similar to movies you liked"
                        recommendations.append(movie)
            
            except Exception as e:
                logger.warning(f"Could not get similar movies for {favorite_movie_id}: {e}")
                continue
        
        # Remove duplicates and sort
        seen_ids = set()
        unique_recommendations = []
        for movie in recommendations:
            if movie['id'] not in seen_ids:
                seen_ids.add(movie['id'])
                unique_recommendations.append(movie)
        
        unique_recommendations.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
        
        return unique_recommendations[:limit]
    
    # Helper methods
    
    def _get_user_genre_preferences(self, user: User) -> Dict[int, float]:
        """Get user's genre preferences based on favorites and viewing history"""
        
        genre_scores = defaultdict(float)
        
        # From favorites
        favorites = UserFavorite.objects.filter(user=user).select_related()
        for favorite in favorites:
            try:
                movie_data = self.tmdb_client.get_movie_details(favorite.movie_id)
                for genre in movie_data.get('genres', []):
                    genre_scores[genre['id']] += 1.0
            except Exception:
                continue
        
        # From viewing history with rating weights
        viewing_history = ViewingHistory.objects.filter(user=user)
        for history in viewing_history:
            try:
                movie_data = self.movie_service.get_movie_details(history.movie_id)
                weight = (history.rating or 5) / 10.0  # Normalize rating to 0-1
                for genre in movie_data.get('genres', []):
                    genre_scores[genre['id']] += weight
            except Exception:
                continue
        
        return dict(genre_scores)
    
    def _find_similar_users(self, user: User, limit: int = 10) -> List[Tuple[int, float]]:
        """Find users with similar preferences using collaborative filtering"""
        
        user_favorites = set(
            UserFavorite.objects.filter(user=user).values_list('movie_id', flat=True)
        )
        
        if not user_favorites:
            return []
        
        # Get all users with favorites
        other_users_favorites = defaultdict(set)
        
        for favorite in UserFavorite.objects.exclude(user=user).select_related('user'):
            other_users_favorites[favorite.user.id].add(favorite.movie_id)
        
        # Calculate Jaccard similarity
        similarities = []
        
        for other_user_id, other_favorites in other_users_favorites.items():
            if len(other_favorites) < 2:  # Skip users with very few favorites
                continue
            
            intersection = len(user_favorites.intersection(other_favorites))
            union = len(user_favorites.union(other_favorites))
            
            if union > 0:
                similarity = intersection / union
                if similarity > 0.1:  # Only include users with some similarity
                    similarities.append((other_user_id, similarity))
        
        # Sort by similarity and return top users
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:limit]
    
    def _calculate_content_score(self, movie: Dict, user_genre_preferences: Dict[int, float]) -> float:
        """Calculate content-based recommendation score for a movie"""
        
        score = 0.0
        
        # Genre match score
        movie_genres = movie.get('genre_ids', [])
        for genre_id in movie_genres:
            if genre_id in user_genre_preferences:
                score += user_genre_preferences[genre_id]
        
        # Popularity and rating boost
        popularity_score = min(movie.get('popularity', 0) / 1000, 1.0)
        rating_score = movie.get('vote_average', 0) / 10.0
        
        score = score + (popularity_score * 0.3) + (rating_score * 0.7)
        
        return score
    
    def _get_genre_name(self, genre_id: int) -> str:
        """Get genre name from ID (cached)"""
        cache_key = f"genre_name_{genre_id}"
        genre_name = cache.get(cache_key)
        
        if not genre_name:
            try:
                genres = self.movie_service.get_genres()
                for genre in genres.get('genres', []):
                    if genre['id'] == genre_id:
                        genre_name = genre['name']
                        cache.set(cache_key, genre_name, 86400)  # Cache for 24 hours
                        break
            except Exception:
                genre_name = "Unknown Genre"
        
        return genre_name or "Unknown Genre"
    
    def _get_popular_movies(self, limit: int = 20) -> List[Dict]:
        """Fallback to popular movies when no user data is available"""
        try:
            popular_movies = self.movie_service.get_popular_movies()
            recommendations = []
            
            for movie in popular_movies.get('results', []):
                movie['recommendation_score'] = movie.get('vote_average', 0) / 10
                movie['recommendation_reason'] = "Popular movie"
                recommendations.append(movie)
            
            return recommendations[:limit]
        except Exception as e:
            logger.error(f"Error getting popular movies: {e}")
            return []
    
    def _get_user_settings(self, user: User) -> RecommendationSettings:
        """Get or create user recommendation settings"""
        settings, created = RecommendationSettings.objects.get_or_create(
            user=user,
            defaults={
                'prefer_content_based': True,
                'prefer_collaborative': True,
                'prefer_trending': False,
                'genre_diversity': 0.5,
                'release_year_range': 10,
                'min_vote_average': 6.0,
                'min_vote_count': 100,
                'max_recommendations': 20,
                'cache_duration_hours': 2,
            }
        )
        return settings
    
    def _apply_user_filters(self, recommendations: List[Dict], settings: RecommendationSettings) -> List[Dict]:
        """Apply user preference filters to recommendations"""
        
        filtered_recommendations = []
        current_year = datetime.now().year
        min_year = current_year - settings.release_year_range
        
        for movie in recommendations:
            # Year filter
            release_date = movie.get('release_date', '')
            if release_date:
                try:
                    movie_year = int(release_date.split('-')[0])
                    if movie_year < min_year:
                        continue
                except (ValueError, IndexError):
                    pass
            
            # Rating filters
            if movie.get('vote_average', 0) < settings.min_vote_average:
                continue
            
            if movie.get('vote_count', 0) < settings.min_vote_count:
                continue
            
            filtered_recommendations.append(movie)
        
        return filtered_recommendations
    
    def _get_cached_recommendations(self, user: User, recommendation_type: str) -> Optional[List[Dict]]:
        """Get cached recommendations if they exist and are not expired"""
        
        try:
            cache_entry = RecommendationCache.objects.get(
                user=user,
                recommendation_type=recommendation_type,
                expires_at__gt=timezone.now()
            )
            
            # Get movie details for cached IDs
            recommendations = []
            for movie_id in cache_entry.movie_ids:
                try:
                    movie_data = self.movie_service.get_movie_details(movie_id)
                    # Add cached score if available
                    if cache_entry.scores and str(movie_id) in cache_entry.scores:
                        movie_data['recommendation_score'] = cache_entry.scores[str(movie_id)]
                    recommendations.append(movie_data)
                except Exception:
                    continue
            
            return recommendations
            
        except RecommendationCache.DoesNotExist:
            return None
    
    def _cache_recommendations(
        self, 
        user: User, 
        recommendation_type: str, 
        recommendations: List[Dict], 
        settings: RecommendationSettings
    ):
        """Cache recommendations for future use"""
        
        movie_ids = [movie['id'] for movie in recommendations]
        scores = {str(movie['id']): movie.get('recommendation_score', 0) for movie in recommendations}
        
        expires_at = timezone.now() + timedelta(hours=settings.cache_duration_hours)
        
        # Update or create cache entry
        RecommendationCache.objects.update_or_create(
            user=user,
            recommendation_type=recommendation_type,
            defaults={
                'movie_ids': movie_ids,
                'scores': scores,
                'expires_at': expires_at,
            }
        )
