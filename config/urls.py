"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for monitoring and load balancers."""
    return JsonResponse(
        {
            "status": "healthy",
            "service": "Movie Recommendation API",
            "version": "1.0.0",
            "timestamp": "2025-08-10T00:00:00Z",
        }
    )


@require_http_methods(["GET"])
def api_root(request):
    """API root endpoint with available endpoints."""
    return JsonResponse(
        {
            "message": "Welcome to Movie Recommendation API",
            "version": "1.0.0",
            "documentation": {
                "swagger": "/api/docs/",
                "redoc": "/api/redoc/",
                "openapi_schema": "/api/schema/",
            },
            "endpoints": {
                "authentication": "/api/v1/auth/",
                "movies": "/api/v1/movies/",
                "favorites": "/api/v1/favorites/",
                "preferences": "/api/v1/preferences/",
                "recommendations": "/api/v1/recommendations/",
            },
        }
    )


urlpatterns = [
    # Admin interface
    path("admin/", admin.site.urls),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Health check and API root
    path("api/health/", health_check, name="health-check"),
    path("api/", api_root, name="api-root"),
    # API endpoints
    path("api/v1/auth/", include("apps.authentication.urls")),
    path("api/v1/movies/", include("apps.movies.urls")),
    path("api/v1/favorites/", include("apps.favorites.urls")),
    path("api/v1/preferences/", include("apps.preferences.urls")),
    path("api/v1/recommendations/", include("apps.recommendations.urls")),
]
