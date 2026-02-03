import os
import socket
from pathlib import Path
from dotenv import load_dotenv

# --- 1. CAMINHOS E AMBIENTE ---
# O BASE_DIR sobe 2 níveis (de pro_igreja/ para a raiz oncristo.local)
BASE_DIR = Path(__file__).resolve().parent.parent

# Carregar variáveis de ambiente do .env_local
load_dotenv(BASE_DIR / '.env_local')

print("--- CARREGANDO SETTINGS UNIFICADAS (ONCRISTO) ---")

# --- 2. SEGURANÇA ---
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-12345')
DEBUG = True

# Hosts e Domínios
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '192.168.0.13', '10.0.2.2', 'oncristo.com.br', '.oncristo.com.br']

# Adicionar IP da rede local automaticamente para testes mobile
try:
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    if local_ip not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(local_ip)
except:
    pass

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://10.0.2.2:8000',
    'https://oncristo.com.br',
]

# --- 3. DEFINIÇÃO DA APLICAÇÃO ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'app_igreja',
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

WSGI_APPLICATION = 'pro_igreja.wsgi.application'

# --- 4. BANCO DE DADOS (DINÂMICO) ---
# Se não houver nada no .env_local, assume SQLite
DB_ENGINE = os.getenv('DB_ENGINE', 'django.db.backends.sqlite3')
DB_NAME = os.getenv('DB_NAME', 'db.sqlite3')

DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        # Se for SQLite, usa o caminho do arquivo. Se for MySQL, usa apenas o nome da base.
        'NAME': BASE_DIR / DB_NAME if 'sqlite' in DB_ENGINE else DB_NAME,
    }
}

# Configurações extras para MySQL (apenas se DB_ENGINE for mysql)
if 'mysql' in DB_ENGINE:
    DATABASES['default']['USER'] = os.getenv('DB_USER', 'root')
    DATABASES['default']['PASSWORD'] = os.getenv('DB_PASSWORD', '')
    DATABASES['default']['HOST'] = os.getenv('DB_HOST', '127.0.0.1')
    DATABASES['default']['PORT'] = os.getenv('DB_PORT', '3306')

# --- 5. ARMAZENAMENTO (WASABI ou LOCAL) ---
# Use mídia local se USE_LOCAL_MEDIA=1 ou se credenciais S3 não estiverem definidas (evita 403 em dev).
USE_LOCAL_MEDIA = os.getenv('USE_LOCAL_MEDIA', '').lower() in ('1', 'true', 'yes')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
USE_S3 = bool(AWS_ACCESS_KEY_ID and AWS_STORAGE_BUCKET_NAME) and not USE_LOCAL_MEDIA

AWS_S3_ENDPOINT_URL = f'https://s3.{AWS_S3_REGION_NAME}.wasabisys.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
AWS_S3_FILE_OVERWRITE = False
AWS_S3_VERIFY = True
AWS_S3_USE_SSL = True
AWS_QUERYSTRING_AUTH = True
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_URL_PROTOCOL = 'https:'

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    } if USE_S3 else {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {"location": BASE_DIR / "media", "base_url": "/media/"},
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# --- 6. ARQUIVOS ESTÁTICOS E MÍDIA ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- 7. INTERNACIONALIZAÇÃO ---
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- 8. AUTENTICAÇÃO E EMAIL ---
AUTHENTICATION_BACKENDS = [
    'app_igreja.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/app_igreja/admin-area/'
LOGOUT_REDIRECT_URL = '/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# --- 9. CONFIGURAÇÕES DE DESENVOLVIMENTO ---
X_FRAME_OPTIONS = 'ALLOWALL'
SECURE_CROSS_ORIGIN_OPENER_POLICY = None
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SILENCED_SYSTEM_CHECKS = ['security.W019']