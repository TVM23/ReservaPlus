"""
Django settings for ReservaPlus project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os
from pathlib import Path
from django.core.validators import RegexValidator
from dotenv import load_dotenv

load_dotenv()  # carga el env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Para poner la llave de la api
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-2v-s%z%3)d!-ced-z+lott!cr6*y2^t9gedpldr$*vdl@@&*d&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

LOGIN_URL = '/Usuarios/login/'

INSTALLED_APPS = [
    'HotelApp',
    'Usuarios',
    'Reservas',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ReservaPlus.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'HotelApp', 'templates'),  # Ruta a las plantillas de HotelApp
            os.path.join(BASE_DIR, 'ReservaPlus', 'static/Template-Padre'),
            os.path.join(BASE_DIR, 'Usuarios', 'templates'),
            os.path.join(BASE_DIR, 'Reservas', 'templates'),

        ]
        ,
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

WSGI_APPLICATION = 'ReservaPlus.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        "NAME": "Reserva_Plus",
        "USER": "postgres",
        "PASSWORD": "ADMIN",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',  # Para autenticación con sesión (basada en cookies)
    ],

}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'Usuarios.validators.UppercaseValidator',
    },
    {
        'NAME': 'Usuarios.validators.NumberValidator',
    },
    {
        'NAME': 'Usuarios.validators.SpecialCharacterValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True
APPEND_SLASH = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "ReservaPlus/static",  # Ajusta esto si tu carpeta está en otro lugar
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STRIPE_PUBLIC_KEY = "pk_test_51QFkMPKvS0f4VleL59dUP9Bj2769IfA3Y8F0cRmfKEBT6fKNiFhh6E9AoIlPSugznThUhC4wF1skFMEAwyZTShkf006dIcIPlN"
STRIPE_SECRET_KEY = "sk_test_51QFkMPKvS0f4VleLfLkDvKSS7xuZtzAlnKwT9lufWFKDhfoydKofsxK2JytCHtSfXHXf8HJqk1bxfsdJnurgpmWc00OUNzmsq8"
STRIPE_WEBHOOK_KEY = "whsec_12520e83f7b59ea52b6148c288e1c13707a65a47c96586036ba4c6ec02ad0b16"

DOMAIN = 'http://127.0.0.1:8000/'
