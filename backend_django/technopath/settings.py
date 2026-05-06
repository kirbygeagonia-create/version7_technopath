import os
from pathlib import Path
from decouple import config, UndefinedValueError

BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY: use env var if set, otherwise generate a stable fallback.
# In true production you should always set SECRET_KEY in the Render dashboard.
_debug = config('DEBUG', default=False, cast=bool)
try:
    SECRET_KEY = config('SECRET_KEY')
except UndefinedValueError:
    import secrets
    SECRET_KEY = secrets.token_urlsafe(50)
    print('[WARNING] SECRET_KEY not set — using auto-generated key. Sessions will reset on restart. Set SECRET_KEY in Render dashboard.')
DEBUG = config('DEBUG', default=False, cast=bool)
_allowed_hosts_env = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])
# Always include the production backend domain so Django doesn't reject
# requests before CORS headers can be applied.
_production_hosts = [
    'technopath-backend.onrender.com',
]
ALLOWED_HOSTS = list(set(_allowed_hosts_env + _production_hosts))

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'apps.users',
    'apps.facilities',
    'apps.rooms',
    'apps.navigation',
    'apps.chatbot',
    'apps.notifications',
    'apps.feedback',
    'apps.core',
    'apps.announcements',
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

ROOT_URLCONF = 'technopath.urls'

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

WSGI_APPLICATION = 'technopath.wsgi.application'

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
else:
    # Fall back to SQLite — on Render this means data won't persist across
    # restarts, but the service will at least start. Set DATABASE_URL in the
    # Render dashboard to use PostgreSQL in production.
    if not _debug:
        print('[WARNING] DATABASE_URL is not set. Falling back to SQLite. Data will NOT persist on Render restarts. Set DATABASE_URL in the Render dashboard.')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'technopath.db',
        }
    }

AUTH_USER_MODEL = 'users.AdminUser'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/minute',
        'user': '300/minute',
    },
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

_cors_extra = config('CORS_EXTRA_ORIGINS', default=config('CORS_EXTRA_ORIGIN', default=''))
_cors_extra_list = [o.strip() for o in _cors_extra.split(',') if o.strip()]

# In production on Render, allow all origins so CORS never blocks the frontend.
# The API is protected by JWT authentication, so open CORS is safe here.
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Expose common headers needed by the frontend
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True
