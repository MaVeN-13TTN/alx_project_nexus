"""
Settings package for the Movie Recommendation Backend.

The settings are split into:
- base.py: Common settings for all environments
- development.py: Development-specific settings
- production.py: Production-specific settings
- testing.py: Testing-specific settings
"""

import os
from decouple import config

# Get the environment from environment variables
ENVIRONMENT = config("DJANGO_ENVIRONMENT", default="development")

# Import the appropriate settings based on environment
if ENVIRONMENT == "production":
    from .production import *
elif ENVIRONMENT == "testing":
    from .testing import *
else:
    from .development import *
