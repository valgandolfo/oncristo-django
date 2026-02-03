# Produção: carrega .env_production e sobrescreve o necessário.
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / '.env_production')

from .base import *

import os

DEBUG = False

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError('Em produção defina SECRET_KEY no .env_production')

ALLOWED_HOSTS = [
    'localhost', '127.0.0.1',
    'oncristo.com.br', 'www.oncristo.com.br', '.oncristo.com.br',
]
_hosts = os.getenv('ALLOWED_HOSTS', '').strip()
if _hosts:
    ALLOWED_HOSTS = [h.strip() for h in _hosts.split(',') if h.strip()]

CSRF_TRUSTED_ORIGINS = [
    'https://oncristo.com.br',
    'https://www.oncristo.com.br',
]
_origins = os.getenv('CSRF_TRUSTED_ORIGINS', '').strip()
if _origins:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in _origins.split(',') if o.strip()]

# Banco: produção usa apenas MySQL (variáveis do .env_production)
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.mysql'),
        'NAME': os.getenv('DB_NAME', ''),
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

# Segurança para HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
