import os
from pathlib import Path
from datetime import timedelta
import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / '.env', override=True)

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-ai-resume-generator-secret-key-change-in-production-2026')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

raw_allowed_hosts = os.getenv('ALLOWED_HOSTS', '*')
if raw_allowed_hosts.strip() == '*':
    ALLOWED_HOSTS = ['*']
else:
    parsed_hosts = [h.strip() for h in raw_allowed_hosts.split(',') if h.strip()]
    for fallback in ['localhost', '127.0.0.1', '[::1]', '.vercel.app', '.now.sh']:
        if fallback not in parsed_hosts:
            parsed_hosts.append(fallback)
    ALLOWED_HOSTS = parsed_hosts

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',

    # Local apps
    'apps.authentication',
    'apps.profiles',
    'apps.documents',
    'apps.generations',
    'apps.history',
    'apps.pdf_engine',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database Configuration
USE_SQLITE = os.getenv('USE_SQLITE', 'True').lower() in ('true', '1', 'yes')
DATABASE_URL = os.getenv('DATABASE_URL', '')

if USE_SQLITE or not DATABASE_URL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=False
        )
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static & Media files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ),
}

# Simple JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS Configuration - Strictly restrict access to Localhost & Vercel deployments
# Only allow all origins if explicitly opted in via env (default: False)
CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', 'False').lower() in ('true', '1', 'yes')

def _clean_origin(url: str) -> str:
    url = url.strip().rstrip('/')
    if url and not url.startswith('http://') and not url.startswith('https://'):
        url = f'https://{url}'
    return url

# Base allowed origins (Localhost ports and known frontends)
_default_origins = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:3001',
    'http://127.0.0.1:3001',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Explicit allowed origins from CORS_ALLOWED_ORIGINS env
raw_cors = os.getenv('CORS_ALLOWED_ORIGINS', '')
env_cors_origins = [
    _clean_origin(orig) for orig in raw_cors.split(',')
    if orig.strip() and not orig.strip().startswith('*.')
]

# Support FRONTEND_URL and VERCEL_URL if provided
extra_origins = []
frontend_url = os.getenv('FRONTEND_URL', '').strip()
if frontend_url:
    extra_origins.append(_clean_origin(frontend_url))

vercel_url = os.getenv('VERCEL_URL', '').strip()
if vercel_url:
    extra_origins.append(_clean_origin(vercel_url))

CORS_ALLOWED_ORIGINS = list(dict.fromkeys(_default_origins + env_cors_origins + extra_origins))

# Regex patterns to dynamically match ANY Vercel deployment URL (production, preview branches, PR previews)
# and localhost on any port
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https:\/\/.*\.vercel\.app$",
    r"^https:\/\/.*\.now\.sh$",
    r"^http:\/\/localhost(:\d+)?$",
    r"^http:\/\/127\.0\.0\.1(:\d+)?$",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'HEAD',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'access-control-request-headers',
    'access-control-request-method',
    'authorization',
    'cache-control',
    'content-disposition',
    'content-type',
    'dnt',
    'if-modified-since',
    'origin',
    'pragma',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_EXPOSE_HEADERS = [
    'content-type',
    'content-disposition',
    'content-length',
    'accept-ranges',
]

CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours

# CSRF Trusted Origins for HTTPS deployments & Vercel
raw_csrf = os.getenv('CSRF_TRUSTED_ORIGINS', '')
custom_csrf = [_clean_origin(c) for c in raw_csrf.split(',') if c.strip()]
CSRF_TRUSTED_ORIGINS = list(set(
    custom_csrf + [
        'https://*.vercel.app',
        'https://*.now.sh',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:3001',
        'http://127.0.0.1:3001',
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:8000',
        'http://127.0.0.1:8000',
    ] + extra_origins
))

# LLM & Gemini Configuration (Provider-Independent Backend Service)
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
_raw_model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
GEMINI_MODEL = 'gemini-2.5-flash' if _raw_model in ('gemini-1.5-flash', 'models/gemini-1.5-flash', 'gemini-1.0-pro') else _raw_model
GEMINI_MAX_RETRIES = int(os.getenv('GEMINI_MAX_RETRIES', '3'))
GEMINI_TIMEOUT_SECONDS = int(os.getenv('GEMINI_TIMEOUT_SECONDS', '60'))
