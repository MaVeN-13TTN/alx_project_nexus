"""
Development settings for Movie Recommendation Backend.

These settings are used du# Additional development apps (commented out - install if needed)
# INSTALLED_APPS += [
#     'django_extensions',  # If installed
# ] development and include debugging tools,
relaxed security settings, and local database configurations.
"""

from .base import *

# Development-specific settings
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Development database (SQLite for quick setup)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {
            "timeout": 20,
        },
    }
}

# Email backend for development (console output)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# CORS settings for development (allow all origins)
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# CSRF settings for development
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Cache settings for development (use local memory cache)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# Logging configuration for development
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
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# Additional development apps
INSTALLED_APPS += [
    "django_extensions",  # If installed
]

# DRF settings for development
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",  # Enable browsable API in development
]

# Development-specific security settings (relaxed)
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# TMDb API settings (use from environment)
TMDB_API_KEY = config("TMDB_API_KEY", default="")
if not TMDB_API_KEY:
    print("⚠️  WARNING: TMDB_API_KEY not set. TMDb integration will not work.")

print("🚀 Running in DEVELOPMENT mode")
