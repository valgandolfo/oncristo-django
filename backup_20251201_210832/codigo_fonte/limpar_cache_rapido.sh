#!/bin/bash

# Script de limpeza rápida de cache
# Uso: ./limpar_cache_rapido.sh

echo "🚀 Limpeza rápida de cache..."

# Limpar cache do Django
python manage.py shell -c "
from django.core.cache import cache
cache.clear()
print('Cache do Django limpo!')
" 2>/dev/null

# Limpar arquivos .pyc
find . -name "*.pyc" -delete 2>/dev/null
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# Recolher arquivos estáticos
python manage.py collectstatic --noinput --clear

echo "✅ Cache limpo!"
echo "💡 Use Ctrl+Shift+R no navegador para hard refresh"
