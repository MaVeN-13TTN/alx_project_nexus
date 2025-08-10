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

    print("🎭 Running in STAGING mode (domain-detected)")
else:
    # Production settings (from production.py)
    print("🏭 Running in PRODUCTION mode (domain-detected)")
