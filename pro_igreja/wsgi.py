"""
WSGI config for pro_igreja project.
"""

import os
from django.core.wsgi import get_wsgi_application

# Aponta diretamente para o arquivo settings.py na raiz da pasta pro_igreja
# Não depende mais de subpastas ou variáveis de ambiente complexas
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_igreja.settings')

application = get_wsgi_application()
