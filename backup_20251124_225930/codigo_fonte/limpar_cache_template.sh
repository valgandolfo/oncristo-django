#!/bin/bash
# Script para forçar atualização de templates no Django

echo "🔄 Limpando cache do Django..."

# Limpar cache Python
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# Limpar cache de templates (se existir)
find . -type d -name ".django_cache" -exec rm -rf {} + 2>/dev/null

echo "✅ Cache limpo!"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Pare o servidor Django (Ctrl+C)"
echo "2. Reinicie o servidor: python manage.py runserver"
echo "3. No navegador: Pressione Ctrl+Shift+R (ou Cmd+Shift+R no Mac)"
echo "   Isso força o navegador a recarregar sem usar cache"
echo ""
echo "💡 DICA: Se ainda não funcionar, abra o navegador em modo anônimo/privado"

