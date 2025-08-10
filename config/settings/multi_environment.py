"""
Multi-environment settings that detect staging vs production by domain.
Used for single VPS deployment serving both environments.
"""

from .production import *
import os


def get_environment_from_host():
    """Detect environment from HTTP_HOST header"""
    try:
        host = os.environ.get("HTTP_HOST", "")
        if "staging-nexus" in host:
            return "staging"
        return "production"
    except Exception:
        return "production"  # Default to production if detection fails


# Dynamic environment detection
CURRENT_ENV = get_environment_from_host()

# Override logging to use console output instead of files for Docker
# This prevents permission issues with log files
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "DEBUG" if CURRENT_ENV == "staging" else "INFO",
            "propagate": False,
        },
    },
}

if CURRENT_ENV == "staging":
    # Staging-specific overrides
    DEBUG = True

    # Staging database
    DATABASES = {
        "default": dj_database_url.config(
            default=f"postgresql://{config('DB_USER')}:{config('DB_PASSWORD')}@db:5432/movie_recommendation_staging",
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

    # Staging cache (different Redis DB)
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://redis:6379/1",  # Use Redis DB 1 for staging
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
            "KEY_PREFIX": "movie_rec_staging",
            "TIMEOUT": 300,
        }
    }

    # Enable browsable API for staging
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ]

    # Staging-specific Swagger UI configuration
    SPECTACULAR_SETTINGS.update({
        "TITLE": "Movie Recommendation API - Staging",
        "DESCRIPTION": """
        🎭 **STAGING ENVIRONMENT**
        
        A comprehensive RESTful API for movie recommendations and user management.
        
        ## Features
        - **JWT Authentication**: Secure user authentication with token-based auth
        - **TMDb Integration**: Real-time movie data from The Movie Database
        - **Advanced Recommendations**: Multiple algorithms including matrix factorization, neural collaborative filtering
        - **User Management**: Comprehensive user profiles, preferences, and viewing history
        - **Multi-Environment**: Single application serving both staging and production via domain detection
        
        ## Environment Information
        - **Environment**: Staging
        - **Domain**: staging-nexus.k1nyanjui.com
        - **Features**: Debug mode enabled, browsable API available
        - **Database**: Separate staging database
        - **Cache**: Dedicated Redis database (DB 1)
        
        ## Authentication
        Most endpoints require authentication. Use the `/api/v1/auth/login/` endpoint to obtain JWT tokens.
        """,
        "VERSION": "1.0.0-staging",
        "SERVERS": [
            {
                "url": "https://staging-nexus.k1nyanjui.com",
                "description": "🎭 Staging server (current environment)",
            },
            {
                "url": "https://nexus.k1nyanjui.com",
                "description": "🏭 Production server",
            },
            {"url": "http://localhost:8000", "description": "🚀 Development server"},
        ],
        "SWAGGER_UI_SETTINGS": {
            "deepLinking": True,
            "persistAuthorization": True,
            "displayOperationId": True,  # Show operation IDs in staging
            "filter": True,
            "tryItOutEnabled": True,
            "defaultModelsExpandDepth": 2,  # Expand models in staging
            "defaultModelExpandDepth": 3,
            "showExtensions": True,
            "showCommonExtensions": True,
        },
        "TAGS": [
            {"name": "Authentication", "description": "User authentication and JWT token management"},
            {"name": "Movies", "description": "Movie database operations and TMDb integration"},
            {"name": "Favorites", "description": "User favorite movies management"},
            {"name": "Preferences", "description": "User preferences and genre settings"},
            {"name": "Recommendations", "description": "Movie recommendation algorithms"},
            {"name": "Health", "description": "System health and monitoring endpoints"},
        ],
    })

    print("🎭 Running in STAGING mode (domain-detected)")
else:
    # Production settings (from production.py)
    
    # Production-specific Swagger UI configuration
    SPECTACULAR_SETTINGS.update({
        "TITLE": "Movie Recommendation API - Production",
        "DESCRIPTION": """
        🏭 **PRODUCTION ENVIRONMENT**
        
        A comprehensive RESTful API for movie recommendations and user management.
        
        ## Features
        - **JWT Authentication**: Secure user authentication with token-based auth
        - **TMDb Integration**: Real-time movie data from The Movie Database
        - **Advanced Recommendations**: Multiple algorithms including matrix factorization, neural collaborative filtering
        - **User Management**: Comprehensive user profiles, preferences, and viewing history
        - **Multi-Environment**: Single application serving both staging and production via domain detection
        
        ## Environment Information
        - **Environment**: Production
        - **Domain**: nexus.k1nyanjui.com
        - **Features**: Optimized for performance and security
        - **Database**: Production PostgreSQL database
        - **Cache**: Production Redis cache
        
        ## Authentication
        All endpoints require authentication. Use the `/api/v1/auth/login/` endpoint to obtain JWT tokens.
        
        ## Rate Limiting
        API requests are rate-limited for optimal performance.
        """,
        "VERSION": "1.0.0",
        "SERVERS": [
            {
                "url": "https://nexus.k1nyanjui.com",
                "description": "🏭 Production server (current environment)",
            },
            {
                "url": "https://staging-nexus.k1nyanjui.com",
                "description": "🎭 Staging server",
            },
            {"url": "http://localhost:8000", "description": "🚀 Development server"},
        ],
        "SWAGGER_UI_SETTINGS": {
            "deepLinking": True,
            "persistAuthorization": True,
            "displayOperationId": False,  # Hide operation IDs in production
            "filter": True,
            "tryItOutEnabled": True,
            "defaultModelsExpandDepth": 1,  # Minimize expanded models in production
            "defaultModelExpandDepth": 1,
            "showExtensions": False,
            "showCommonExtensions": False,
        },
        "TAGS": [
            {"name": "Authentication", "description": "User authentication and JWT token management"},
            {"name": "Movies", "description": "Movie database operations and TMDb integration"},
            {"name": "Favorites", "description": "User favorite movies management"},
            {"name": "Preferences", "description": "User preferences and genre settings"},
            {"name": "Recommendations", "description": "Movie recommendation algorithms"},
            {"name": "Health", "description": "System health and monitoring endpoints"},
        ],
    })
    
    print("🏭 Running in PRODUCTION mode (domain-detected)")
