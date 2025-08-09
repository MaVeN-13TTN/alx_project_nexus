from datetime import datetime
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Avg, Count
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import (
    RecommendationSettings,
    RecommendationFeedback,
    RecommendationCache,
    UserSimilarity,
    MovieSimilarity
)
from .serializers import (
    RecommendationSettingsSerializer,
    RecommendationFeedbackSerializer,
    MovieRecommendationSerializer,
    RecommendationListSerializer,
    RecommendationAnalyticsSerializer,
    RecommendationRequestSerializer,
    UserSimilaritySerializer,
    MovieSimilaritySerializer
)
from .basic_engine import BasicRecommendationEngine

User = get_user_model()


class RecommendationListView(APIView):
    """Get personalized movie recommendations for authenticated user"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='type',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Type of recommendation (content, collaborative, hybrid, trending, similar)',
                default='hybrid'
            ),
            OpenApiParameter(
                name='limit',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Number of recommendations to return (1-100)',
                default=20
            ),
            OpenApiParameter(
                name='force_refresh',
                type=bool,
                location=OpenApiParameter.QUERY,
                description='Force refresh cache',
                default=False
            ),
        ],
        responses={200: RecommendationListSerializer},
        description="Get personalized movie recommendations"
    )
    def get(self, request):
        """Get recommendations for the authenticated user"""
        
        # Parse query parameters
        recommendation_type = request.query_params.get('type', 'hybrid')
        limit = int(request.query_params.get('limit', 20))
        force_refresh = request.query_params.get('force_refresh', 'false').lower() == 'true'
        
        # Validate parameters
        valid_types = ['content', 'collaborative', 'hybrid', 'trending', 'similar']
        if recommendation_type not in valid_types:
            return Response(
                {'error': f'Invalid recommendation type. Must be one of: {", ".join(valid_types)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not 1 <= limit <= 100:
            return Response(
                {'error': 'Limit must be between 1 and 100'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get recommendations using the engine
            engine = BasicRecommendationEngine()
            recommendations = engine.get_recommendations(
                user=request.user,
                recommendation_type=recommendation_type,
                limit=limit,
                force_refresh=force_refresh
            )
            
            # Check if recommendations came from cache
            cached = not force_refresh and self._check_cache_hit(request.user, recommendation_type)
            
            # Prepare response data
            response_data = {
                'recommendation_type': recommendation_type,
                'total_count': len(recommendations),
                'cached': cached,
                'generated_at': timezone.now(),
                'recommendations': recommendations
            }
            
            serializer = RecommendationListSerializer(response_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to generate recommendations: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _check_cache_hit(self, user, recommendation_type):
        """Check if recommendations came from cache"""
        try:
            cache_entry = RecommendationCache.objects.get(
                user=user,
                recommendation_type=recommendation_type,
                expires_at__gt=timezone.now()
            )
            return True
        except RecommendationCache.DoesNotExist:
            return False


class RecommendationSettingsView(generics.RetrieveUpdateAPIView):
    """Get and update user recommendation settings"""
    
    serializer_class = RecommendationSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get or create recommendation settings for the user"""
        settings, created = RecommendationSettings.objects.get_or_create(
            user=self.request.user,
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
    
    @extend_schema(
        responses={200: RecommendationSettingsSerializer},
        description="Get user recommendation settings"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        request=RecommendationSettingsSerializer,
        responses={200: RecommendationSettingsSerializer},
        description="Update user recommendation settings"
    )
    def patch(self, request, *args, **kwargs):
        # Clear recommendation cache when settings are updated
        RecommendationCache.objects.filter(user=request.user).delete()
        return super().patch(request, *args, **kwargs)


class RecommendationFeedbackView(APIView):
    """Submit feedback on movie recommendations"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=RecommendationFeedbackSerializer,
        responses={201: RecommendationFeedbackSerializer},
        description="Submit feedback on a recommendation"
    )
    def post(self, request):
        """Submit feedback on a recommendation"""
        
        serializer = RecommendationFeedbackSerializer(data=request.data)
        if serializer.is_valid():
            # Check if feedback already exists
            existing_feedback = RecommendationFeedback.objects.filter(
                user=request.user,
                movie_id=serializer.validated_data['movie_id'],
                recommendation_type=serializer.validated_data['recommendation_type']
            ).first()
            
            if existing_feedback:
                # Update existing feedback
                existing_feedback.feedback = serializer.validated_data['feedback']
                existing_feedback.save()
                response_serializer = RecommendationFeedbackSerializer(existing_feedback)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                # Create new feedback
                feedback = serializer.save(user=request.user)
                response_serializer = RecommendationFeedbackSerializer(feedback)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecommendationAnalyticsView(APIView):
    """Get recommendation analytics and insights"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses={200: RecommendationAnalyticsSerializer},
        description="Get recommendation analytics for the user"
    )
    def get(self, request):
        """Get analytics data for user's recommendations"""
        
        user = request.user
        
        # Get recommendation counts
        total_recommendations = RecommendationCache.objects.filter(user=user).count()
        
        # Get feedback statistics
        feedback_queryset = RecommendationFeedback.objects.filter(user=user)
        feedback_count = feedback_queryset.count()
        
        positive_feedback = feedback_queryset.filter(
            feedback__in=['like', 'watched']
        ).count()
        
        positive_percentage = (positive_feedback / feedback_count * 100) if feedback_count > 0 else 0
        
        # Get most recommended genres (this would require more complex logic)
        most_recommended_genres = []  # Placeholder
        
        # Calculate recommendation accuracy (placeholder)
        recommendation_accuracy = positive_percentage / 100 if feedback_count > 0 else 0
        
        # Calculate average recommendation score (placeholder)
        avg_score = 0.75  # Placeholder
        
        # Calculate cache hit rate
        cache_entries = RecommendationCache.objects.filter(user=user)
        total_cache_checks = cache_entries.count() * 2  # Estimate
        cache_hits = cache_entries.filter(expires_at__gt=timezone.now()).count()
        cache_hit_rate = (cache_hits / total_cache_checks * 100) if total_cache_checks > 0 else 0
        
        analytics_data = {
            'total_recommendations_given': total_recommendations,
            'user_feedback_count': feedback_count,
            'positive_feedback_percentage': positive_percentage,
            'most_recommended_genres': most_recommended_genres,
            'recommendation_accuracy': recommendation_accuracy,
            'average_recommendation_score': avg_score,
            'cache_hit_rate': cache_hit_rate
        }
        
        serializer = RecommendationAnalyticsSerializer(analytics_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    responses={200: UserSimilaritySerializer(many=True)},
    description="Get users similar to the authenticated user"
)
def similar_users_view(request):
    """Get users similar to the authenticated user"""
    
    similar_users = UserSimilarity.objects.filter(
        user1=request.user
    ).select_related('user2').order_by('-similarity_score')[:10]
    
    serializer = UserSimilaritySerializer(similar_users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    parameters=[
        OpenApiParameter(
            name='movie_id',
            type=int,
            location=OpenApiParameter.QUERY,
            description='TMDb movie ID to find similar movies for',
            required=True
        ),
    ],
    responses={200: MovieSimilaritySerializer(many=True)},
    description="Get movies similar to the specified movie"
)
def similar_movies_view(request):
    """Get movies similar to a specified movie"""
    
    movie_id = request.query_params.get('movie_id')
    
    if not movie_id:
        return Response(
            {'error': 'movie_id parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        movie_id = int(movie_id)
    except (ValueError, TypeError):
        return Response(
            {'error': 'movie_id must be a valid integer'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    similar_movies = MovieSimilarity.objects.filter(
        movie1_id=movie_id
    ).order_by('-similarity_score')[:20]
    
    serializer = MovieSimilaritySerializer(similar_movies, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    request=RecommendationRequestSerializer,
    responses={200: RecommendationListSerializer},
    description="Get recommendations with advanced parameters"
)
def advanced_recommendations_view(request):
    """Get recommendations with advanced filtering and parameters"""
    
    serializer = RecommendationRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    validated_data = serializer.validated_data
    
    try:
        engine = BasicRecommendationEngine()
        recommendations = engine.get_recommendations(
            user=request.user,
            recommendation_type=validated_data['recommendation_type'],
            limit=validated_data['limit'],
            force_refresh=validated_data['force_refresh']
        )
        
        cached = not validated_data['force_refresh']
        
        response_data = {
            'recommendation_type': validated_data['recommendation_type'],
            'total_count': len(recommendations),
            'cached': cached,
            'generated_at': timezone.now(),
            'recommendations': recommendations
        }
        
        if validated_data['include_metadata']:
            response_data['metadata'] = {
                'algorithm_used': validated_data['recommendation_type'],
                'parameters': validated_data,
                'user_id': request.user.id
            }
        
        response_serializer = RecommendationListSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to generate recommendations: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    responses={204: None},
    description="Clear all recommendation cache for the user"
)
def clear_recommendation_cache_view(request):
    """Clear all recommendation cache for the authenticated user"""
    
    deleted_count = RecommendationCache.objects.filter(user=request.user).delete()[0]
    
    return Response(
        {'message': f'Cleared {deleted_count} cache entries'},
        status=status.HTTP_200_OK
    )
