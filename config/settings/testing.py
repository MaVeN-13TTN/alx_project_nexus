"""
Testing settings for Movie Recommendation Backend.

These settings are optimized for running tests with faster database,
disabled caching, and simplified configurations.
"""

from .base import *

# Testing-specific settings
DEBUG = False
SECRET_KEY = "test-secret-key-for-testing-only"
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

# Use in-memory SQLite for faster tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "OPTIONS": {
            "timeout": 20,
        },
    }
}

# Disable caching during tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Email backend for testing (in-memory)
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Password hashers (faster for testing)
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",  # Faster but less secure (testing only)
]


# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Logging configuration for testing (minimal)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "ERROR",
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "ERROR",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

# JWT settings for testing (shorter token lifetimes)
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(minutes=10),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
}

# CORS settings for testing
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# CSRF settings for testing
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Mock TMDb API settings for testing
TMDB_API_KEY = "test-api-key"
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Celery settings for testing (eager execution)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# REST Framework settings for testing
REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = [
    "rest_framework_simplejwt.authentication.JWTAuthentication",
    "rest_framework.authentication.SessionAuthentication",  # For easier test setup
]

print("🧪 Running in TESTING mode")
