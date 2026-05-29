
from datetime import timedelta
from pathlib import Path
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-9vfjnowh@@jd99%=u%+sxca)gp9(gco490)#u^-b)hslr07(bj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')


AUTH_USER_MODEL = 'apiusuario.Usuario'


CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:3000",
]

CORS_ALLOWED_ALL_ORIGINS = True

# Application definition

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'apiusuario',
    'corsheaders',
    'matches',
    'statistics',
    'friendship',
    'coaching',
    'notifications',
    'channels',
]

ASGI_APPLICATION = 'back.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(os.environ.get('REDIS_HOST', 'localhost'), int(os.environ.get('REDIS_PORT', 6379)))],
        },
    },
}

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

ROOT_URLCONF = 'back.urls'

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

WSGI_APPLICATION = 'back.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


SIMPLE_JWT = {
    'SIGNING_KEY': SECRET_KEY,
    'ALGORITHM': 'HS256',
    'USER_ID_FIELD': 'id',
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

def _f(key, default):
    return float(os.environ.get(key, default))

TENNIS_DISTANCE_PARAMS = {
    ('Amateur',     'Clay', 'Masculino'): {'effective': _f('DIST_AMATEUR_CLAY_M_EFF',    '23.0'), 'mpm': _f('DIST_AMATEUR_CLAY_M_MPM',    '28.5')},
    ('Amateur',     'Clay', 'Femenino'):  {'effective': _f('DIST_AMATEUR_CLAY_F_EFF',    '21.0'), 'mpm': _f('DIST_AMATEUR_CLAY_F_MPM',    '25.0')},
    ('Amateur',     'Hard', 'Masculino'): {'effective': _f('DIST_AMATEUR_HARD_M_EFF',    '17.0'), 'mpm': _f('DIST_AMATEUR_HARD_M_MPM',    '34.0')},
    ('Amateur',     'Hard', 'Femenino'):  {'effective': _f('DIST_AMATEUR_HARD_F_EFF',    '13.0'), 'mpm': _f('DIST_AMATEUR_HARD_F_MPM',    '29.0')},
    ('Semi-Pro',    'Clay', 'Masculino'): {'effective': _f('DIST_SEMIPRO_CLAY_M_EFF',    '31.0'), 'mpm': _f('DIST_SEMIPRO_CLAY_M_MPM',    '36.0')},
    ('Semi-Pro',    'Clay', 'Femenino'):  {'effective': _f('DIST_SEMIPRO_CLAY_F_EFF',    '28.0'), 'mpm': _f('DIST_SEMIPRO_CLAY_F_MPM',    '31.5')},
    ('Semi-Pro',    'Hard', 'Masculino'): {'effective': _f('DIST_SEMIPRO_HARD_M_EFF',    '22.0'), 'mpm': _f('DIST_SEMIPRO_HARD_M_MPM',    '43.0')},
    ('Semi-Pro',    'Hard', 'Femenino'):  {'effective': _f('DIST_SEMIPRO_HARD_F_EFF',    '20.0'), 'mpm': _f('DIST_SEMIPRO_HARD_F_MPM',    '38.0')},
    ('Profesional', 'Clay', 'Masculino'): {'effective': _f('DIST_PRO_CLAY_M_EFF',        '40.0'), 'mpm': _f('DIST_PRO_CLAY_M_MPM',        '40.0')},
    ('Profesional', 'Clay', 'Femenino'):  {'effective': _f('DIST_PRO_CLAY_F_EFF',        '35.0'), 'mpm': _f('DIST_PRO_CLAY_F_MPM',        '37.0')},
    ('Profesional', 'Hard', 'Masculino'): {'effective': _f('DIST_PRO_HARD_M_EFF',        '27.0'), 'mpm': _f('DIST_PRO_HARD_M_MPM',        '48.5')},
    ('Profesional', 'Hard', 'Femenino'):  {'effective': _f('DIST_PRO_HARD_F_EFF',        '25.0'), 'mpm': _f('DIST_PRO_HARD_F_MPM',        '44.0')},
}
