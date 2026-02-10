"""
Django settings for core project.
Hybrid platform backend prototype.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-me")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "1") == "1"

ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "*").split(",") if h.strip()]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'rest_framework',
    'users',
    'wallet',
    'rewards',
    'orders',
    'rides',
    'captains',
    'restaurants',
    'recommendations',
    'payments',
    'notifications',
    'pricing',
    'ratings',
    'fraud',
    'adminpanel',
    'routing',
    'analytics',
    'maps',
    'cancellation',
    'chat',
    'promotions',
    'payouts',
    'restaurant_ops',
    'trust',
    'eta',
    'growth',
    'vehicles',
    'support',
    'observability',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'core.middleware.RateLimitMiddleware',
    'core.middleware.IdempotencyKeyMiddleware',
    'core.middleware.PrometheusMetricsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.RoleRequiredMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "core.auth.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

API_VERSION = "v1"

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "hybrid_db")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXP_MINUTES = int(os.getenv("JWT_EXP_MINUTES", "720"))
JWT_REFRESH_EXP_MINUTES = int(os.getenv("JWT_REFRESH_EXP_MINUTES", "43200"))
JWT_ISSUER = os.getenv("JWT_ISSUER", "hybrid-core")

ALLOWED_ROLES = ["USER", "CAPTAIN", "RESTAURANT", "ADMIN"]

RAZORPAY_KEY = os.getenv("RAZORPAY_KEY")
RAZORPAY_SECRET = os.getenv("RAZORPAY_SECRET")

FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")
FIREBASE_CREDENTIALS_JSON = os.getenv("FIREBASE_CREDENTIALS_JSON")

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_URL]},
    }
}

CAPTAIN_MATCH_RADIUS_M = int(os.getenv("CAPTAIN_MATCH_RADIUS_M", "5000"))
CAPTAIN_MATCH_TIMEOUT_SEC = int(os.getenv("CAPTAIN_MATCH_TIMEOUT_SEC", "15"))
CAPTAIN_MATCH_MAX_CANDIDATES = int(os.getenv("CAPTAIN_MATCH_MAX_CANDIDATES", "20"))
CAPTAIN_MAX_BATCH_ORDERS = int(os.getenv("CAPTAIN_MAX_BATCH_ORDERS", "3"))
DISPATCH_RATING_WEIGHT = float(os.getenv("DISPATCH_RATING_WEIGHT", "0.4"))
DISPATCH_FAIRNESS_WEIGHT = float(os.getenv("DISPATCH_FAIRNESS_WEIGHT", "0.2"))
DISPATCH_DISTANCE_WEIGHT = float(os.getenv("DISPATCH_DISTANCE_WEIGHT", "1.0"))
WEATHER_FACTOR = float(os.getenv("WEATHER_FACTOR", "1.0"))
GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_KEY")
MAPS_CACHE_TTL_MIN = int(os.getenv("MAPS_CACHE_TTL_MIN", "30"))
EV_REWARD_PERCENTAGE = float(os.getenv("EV_REWARD_PERCENTAGE", "0.10"))
EV_BONUS_MULTIPLIER = float(os.getenv("EV_BONUS_MULTIPLIER", "1.0"))
FOOD_ALLOWED_VEHICLES = [
    v.strip().upper()
    for v in os.getenv("FOOD_ALLOWED_VEHICLES", "BIKE_PETROL,BIKE_EV").split(",")
    if v.strip()
]
CHAT_ABUSE_WORDS = [w.strip() for w in os.getenv("CHAT_ABUSE_WORDS", "abuse,spam").split(",") if w.strip()]
NOTIFICATION_MAX_RETRIES = int(os.getenv("NOTIFICATION_MAX_RETRIES", "3"))
GO_HOME_ROUTE_BUFFER_KM = float(os.getenv("GO_HOME_ROUTE_BUFFER_KM", "1.0"))
GO_HOME_ETA_BUFFER_MIN = int(os.getenv("GO_HOME_ETA_BUFFER_MIN", "10"))
GO_HOME_MAX_SPEED_KMPH = float(os.getenv("GO_HOME_MAX_SPEED_KMPH", "200"))

RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "1") == "1"
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "300"))
RATE_LIMIT_WINDOW_SEC = int(os.getenv("RATE_LIMIT_WINDOW_SEC", "60"))
RATE_LIMIT_EXEMPT_PATHS = [
    "/api/v1/health",
    "/api/v1/metrics",
]

IDEMPOTENCY_TTL_SEC = int(os.getenv("IDEMPOTENCY_TTL_SEC", "86400"))

ORDER_ASSIGN_TIMEOUT_SEC = int(os.getenv("ORDER_ASSIGN_TIMEOUT_SEC", "600"))
ORDER_DELIVERY_SLA_MIN = int(os.getenv("ORDER_DELIVERY_SLA_MIN", "45"))
RIDE_ASSIGN_TIMEOUT_SEC = int(os.getenv("RIDE_ASSIGN_TIMEOUT_SEC", "300"))
RIDE_COMPLETE_SLA_MIN = int(os.getenv("RIDE_COMPLETE_SLA_MIN", "60"))
MATCH_RETRY_MAX = int(os.getenv("MATCH_RETRY_MAX", "2"))
MATCH_RETRY_DELAY_SEC = int(os.getenv("MATCH_RETRY_DELAY_SEC", "20"))
FATIGUE_MIN_REST_MIN = int(os.getenv("FATIGUE_MIN_REST_MIN", "15"))
FATIGUE_PENALTY_WEIGHT = float(os.getenv("FATIGUE_PENALTY_WEIGHT", "0.5"))
ZONE_BALANCE_WEIGHT = float(os.getenv("ZONE_BALANCE_WEIGHT", "0.2"))
GO_HOME_SCORE_WEIGHT = float(os.getenv("GO_HOME_SCORE_WEIGHT", "0.3"))
COMMISSION_PCT = float(os.getenv("COMMISSION_PCT", "0.2"))
