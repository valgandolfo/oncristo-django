#!/bin/bash

# Script para reiniciar serviços após mudanças no .env_production
# Execute este script NO SERVIDOR

echo "🔄 Reiniciando serviços..."

# Reiniciar Gunicorn (importante para recarregar variáveis de ambiente)
echo "→ Reiniciando Gunicorn..."
systemctl restart gunicorn_oncristo

# Aguardar um pouco
sleep 2

# Verificar status
if systemctl is-active --quiet gunicorn_oncristo; then
    echo "✅ Gunicorn reiniciado com sucesso"
else
    echo "❌ Erro ao reiniciar Gunicorn"
    systemctl status gunicorn_oncristo --no-pager -l
    exit 1
fi

# Recarregar Nginx (não precisa reiniciar, só recarregar)
echo "→ Recarregando Nginx..."
systemctl reload nginx

echo "✅ Serviços reiniciados!"
echo ""
echo "📧 Teste a recuperação de senha agora:"
echo "   https://oncristo.com.br/password_reset/"

