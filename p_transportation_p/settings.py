
import os
from pathlib import Path
import dj_database_url
from corsheaders.defaults import default_headers # إضافة استيراد الترويسات الافتراضية

# المسارات الأساسية
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'replace-this-with-a-secure-secret-key'
DEBUG = True

# السماح لجميع المضيفين
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'daphne',      
    'channels',
    'corsheaders', 
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'PTP.apps.PTPConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # وضعناها في الأعلى تماماً
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- إعدادات CORS و CSRF المحدثة ---
CORS_ALLOW_ALL_ORIGINS = True 
CORS_ALLOW_CREDENTIALS = True

# السماح للترويسات التي يستخدمها Vite و Axios عادةً
CORS_ALLOW_HEADERS = list(default_headers) + [
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# ضروري جداً لنجاح طلبات الـ POST من رابط Vite أو Railway
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "https://web-production-d9b56.up.railway.app", # رابط الـ Railway الخاص بك
]
# --------------------------------

ROOT_URLCONF = 'p_transportation_p.urls'
ASGI_APPLICATION = 'p_transportation_p.asgi.application'
WSGI_APPLICATION = 'p_transportation_p.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
    )
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
        },
    },
}

AUTH_USER_MODEL = 'PTP.User'

LANGUAGE_CODE = 'ar-sy'
TIME_ZONE = 'Asia/Damascus' # متوافق مع توقيت دمشق الحالي
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

OSRM_BASE_URL = os.environ.get('OSRM_BASE_URL', 'https://router.project-osrm.org')
OSRM_PROFILE = os.environ.get('OSRM_PROFILE', 'driving')
GEOCODING_USER_AGENT = os.environ.get('GEOCODING_USER_AGENT', 'PublicTransportationPlatform/1.0')

DAMASCUS_ROUTE_BOUNDS = {
    'min_latitude': '33.430000',
    'max_latitude': '33.580000',
    'min_longitude': '36.180000',
    'max_longitude': '36.380000',
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
