from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables based on environment
DJANGO_ENV = os.getenv('DJANGO_ENV', 'development')
if DJANGO_ENV == 'production':
    load_dotenv('.env_production')
else:
    load_dotenv('.env_local')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-p^jvx3o%fns*))l(5bmtn^3+=_w5iz!dd^-6+pdhog__p23+d9')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# ALLOWED_HOSTS - Configuração baseada no ambiente
if DJANGO_ENV == 'production':
    # Produção: usar variável de ambiente ou lista específica
    allowed_hosts_str = os.getenv('ALLOWED_HOSTS', '')
    if allowed_hosts_str:
        ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',')]
    else:
        ALLOWED_HOSTS = []  # Deve ser configurado no .env_production
else:
    # Desenvolvimento: aceita conexões da rede local
    ALLOWED_HOSTS = [
        'localhost',
        '127.0.0.1',
        '0.0.0.0',        # Bind address
        '192.168.0.12',   # IP servidor anterior
        '192.168.0.13',   # IP servidor atual
        '192.168.0.111',  # IP servidor alternativo
        '192.168.0.10',   # IP celular atual
        '192.168.0.102',  # IP celular anterior
        '*',              # Permite qualquer host em desenvolvimento (DEBUG=True)
        '.local',
    ]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',  # Para customização de widgets de formulário
    'app_igreja',  # App principal
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

ROOT_URLCONF = 'pro_igreja.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Configurar pasta templates
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

WSGI_APPLICATION = 'pro_igreja.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', ''),
    }
}

# Configurar SSL para MySQL (Digital Ocean requer SSL)
if DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
    DATABASES['default']['OPTIONS'] = {
        'ssl': {
            'ca': None,  # Digital Ocean usa certificado padrão
            'check_hostname': False,  # Desabilitar verificação de hostname
        },
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        'charset': 'utf8mb4',
    }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

# Autenticação customizada - permite login por email ou username
AUTHENTICATION_BACKENDS = [
    'app_igreja.backends.EmailBackend',  # Backend customizado (permite login por email)
    'django.contrib.auth.backends.ModelBackend',  # Backend padrão (fallback)
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', '')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_DEFAULT_ACL = None  # Removido para evitar erro de ACL
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_S3_FILE_OVERWRITE = False
AWS_S3_VERIFY = True

# Use S3 for media files
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Configurações adicionais para S3
AWS_S3_USE_SSL = True
AWS_S3_USE_SSE = True
AWS_S3_ENCRYPTION = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login/Logout URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/app_igreja/admin-area/'
LOGOUT_REDIRECT_URL = '/'
# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
