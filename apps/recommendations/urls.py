from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    # Main recommendation endpoints
    path('', views.RecommendationListView.as_view(), name='recommendations-list'),
    path('advanced/', views.advanced_recommendations_view, name='recommendations-advanced'),
    
    # User settings and feedback
    path('settings/', views.RecommendationSettingsView.as_view(), name='recommendations-settings'),
    path('feedback/', views.RecommendationFeedbackView.as_view(), name='recommendations-feedback'),
    
    # Analytics and insights
    path('analytics/', views.RecommendationAnalyticsView.as_view(), name='recommendations-analytics'),
    
    # Similarity endpoints
    path('similar-users/', views.similar_users_view, name='similar-users'),
    path('similar-movies/', views.similar_movies_view, name='similar-movies'),
    
    # Cache management
    path('cache/clear/', views.clear_recommendation_cache_view, name='clear-cache'),
]
