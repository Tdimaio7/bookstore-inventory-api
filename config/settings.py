import os
from pathlib import Path
from decimal import Decimal
from dotenv import load_dotenv
import json
from rest_framework.parsers import BaseParser

# Raíz del proyecto y carga de variables de entorno locales (.env)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# Configuración básica
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'insecure-secret-key')
DEBUG = True
ALLOWED_HOSTS = ['*']

# Apps instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'inventory',
]

# Middleware de Django
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URLs y WSGI
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# Plantillas
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

# Base de datos (SQLite para desarrollo)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Validadores de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Localización y zona horaria
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Archivos estáticos (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# DRF: paginación y parsers (incluye parser tolerante para text/plain)
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        'config.settings.PlainTextJSONParser',
    ],
}

# Parámetros de negocio
CURRENCY_DEFAULT = os.getenv('CURRENCY_DEFAULT', 'EUR').upper()
try:
    EXCHANGE_RATE_FALLBACK = Decimal(os.getenv('EXCHANGE_RATE_FALLBACK', '1.0'))
except Exception:
    EXCHANGE_RATE_FALLBACK = Decimal('1.0')
MARGIN_PERCENTAGE = Decimal('40')  # margen de ganancia 40%

class PlainTextJSONParser(BaseParser):
    # Parser para 'text/plain' que intenta decodificar JSON si el cuerpo lo es
    media_type = 'text/plain'
    def parse(self, stream, media_type=None, parser_context=None):
        raw = stream.read()
        try:
            text = raw.decode('utf-8')
        except Exception:
            return raw
        try:
            return json.loads(text)
        except Exception:
            return text

APPEND_SLASH = False
