"""
ASGI config for pro_igreja project.
"""

import os
from django.core.asgi import get_asgi_application

# Aponta para o settings.py unificado na raiz da pasta pro_igreja
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_igreja.settings')

application = get_asgi_application()
