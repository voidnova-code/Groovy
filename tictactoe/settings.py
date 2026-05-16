"""
Django settings for tictactoe project - Production Ready
Optimized for Vercel & Render deployment with PostgreSQL
"""

import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY - Use environment variables
SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(50).hex())
DEBUG = os.getenv("DEBUG", "False") == "True"

# Get allowed hosts from environment
# Add your Vercel or Render domain here
hosts_from_env = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
host_list = [h.strip() for h in hosts_from_env.split(",") if h.strip()]

# Allow Vercel, Render, and other subdomain deployments
ALLOWED_HOSTS = host_list + [
    ".vercel.app",
    ".onrender.com",
    "localhost",
    "127.0.0.1",
    "testserver",  # For Django test client
]


# Application definition
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "game",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "tictactoe.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "tictactoe.wsgi.application"


# Database - Support both SQLite (dev) and PostgreSQL (production)
# If DATABASE_URL is set (by Render or Azure), use it; otherwise use SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if DATABASE_URL:
    # For PostgreSQL, ensure SSL mode is set
    if "postgresql" in DATABASE_URL:
        if "sslmode=" not in DATABASE_URL:
            DATABASE_URL = DATABASE_URL + "?sslmode=require"
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL)
    }
else:
    # Fallback to SQLite for local development
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Connection pooling - reuse connections instead of creating new ones
DATABASES["default"]["CONN_MAX_AGE"] = 600


# Cache Configuration - Use Redis for production, local memory for development
REDIS_URL = os.getenv("REDIS_URL", "")

if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "SOCKET_CONNECT_TIMEOUT": 5,
                "SOCKET_TIMEOUT": 5,
                "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
                "IGNORE_EXCEPTIONS": True,
            }
        }
    }
else:
    # Fallback to local memory cache for development
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Default primary key field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Password hashers - fallback to default for old passwords
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
]


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# For Vercel serverless: use /tmp for ephemeral storage
STATIC_URL = "static/"
if os.getenv("VERCEL"):
    STATIC_ROOT = "/tmp/staticfiles"
else:
    STATIC_ROOT = BASE_DIR / "staticfiles"

# Disable serving static files from Django in production
# Let Vercel/Render handle static files
WHITENOISE_AUTOREFRESH = True
WHITENOISE_USE_FINDERS = True

# Login URLs - use custom admin login
LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/admin/dashboard/"
LOGOUT_REDIRECT_URL = "/"

# Media files
MEDIA_URL = "media/"
if os.getenv("VERCEL"):
    MEDIA_ROOT = "/tmp/media"
else:
    MEDIA_ROOT = BASE_DIR / "media"


# REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
}


# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# CORS Settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True


# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")


# Security settings for production
if not DEBUG:
    # Secure SSL/TLS settings
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Session settings
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Content Security
    SECURE_CONTENT_TYPE_NOSNIFF = True


# Logging - Use Python's logging facility
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
