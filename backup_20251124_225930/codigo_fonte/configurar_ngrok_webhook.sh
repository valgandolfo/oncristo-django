#!/bin/bash

# 🚀 Script para configurar ngrok para o webhook do WhatsApp
# Uso: ./configurar_ngrok_webhook.sh

echo "🌐 CONFIGURANDO NGROK PARA WEBHOOK"
echo "=================================="
echo ""

# Verificar se o servidor Django está rodando
if ! pgrep -f "manage.py runserver.*8000" > /dev/null; then
    echo "⚠️  Servidor Django não está rodando na porta 8000!"
    echo ""
    echo "Para iniciar o servidor, execute:"
    echo "  cd /home/joaonote/oncristo.local"
    echo "  ./iniciar_servidor.sh"
    echo ""
    exit 1
fi

echo "✅ Servidor Django está rodando na porta 8000"
echo ""

# Verificar se ngrok está instalado
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok não está instalado!"
    echo ""
    echo "Para instalar:"
    echo "  sudo snap install ngrok"
    echo "  # Ou baixar de: https://ngrok.com/download"
    echo ""
    exit 1
fi

echo "✅ ngrok está instalado"
echo ""

# Verificar se já existe um ngrok rodando
if pgrep -f "ngrok" > /dev/null; then
    echo "⚠️  Já existe um ngrok rodando!"
    echo "   Parando processos ngrok existentes..."
    pkill -f ngrok
    sleep 2
fi

echo "🚀 Iniciando ngrok na porta 8000..."
echo ""
echo "📋 URL do webhook será:"
echo "   https://SUA_URL_NGROK/app_igreja/api/whatsapp/webhook/"
echo ""
echo "📋 URL de teste será:"
echo "   https://SUA_URL_NGROK/app_igreja/api/whatsapp/test/"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   1. Copie a URL do ngrok que aparecerá abaixo"
echo "   2. Configure na Whapi Cloud:"
echo "      - Acesse: https://panel.whapi.cloud/"
echo "      - Vá em Webhooks"
echo "      - Configure: https://SUA_URL_NGROK/app_igreja/api/whatsapp/webhook/"
echo ""
echo "🔄 Iniciando ngrok..."
echo ""

# Iniciar ngrok na porta 8000 em background
ngrok http 8000 > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!

# Aguardar ngrok iniciar
sleep 5

# Tentar obter URL do ngrok
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o '"public_url":"https://[^"]*"' | head -1 | cut -d'"' -f4)

if [ -n "$NGROK_URL" ]; then
    echo "✅ ngrok iniciado com sucesso!"
    echo ""
    echo "📋 URL DO WEBHOOK:"
    echo "   ${NGROK_URL}/app_igreja/api/whatsapp/webhook/"
    echo ""
    echo "📋 URL DE TESTE:"
    echo "   ${NGROK_URL}/app_igreja/api/whatsapp/test/"
    echo ""
    echo "⚠️  IMPORTANTE:"
    echo "   1. Configure esta URL na Whapi Cloud:"
    echo "      - Acesse: https://panel.whapi.cloud/"
    echo "      - Vá em Webhooks"
    echo "      - Configure: ${NGROK_URL}/app_igreja/api/whatsapp/webhook/"
    echo ""
    echo "📊 Para ver logs do ngrok: tail -f /tmp/ngrok.log"
    echo "🛑 Para parar o ngrok: pkill -f ngrok"
    echo ""
else
    echo "⚠️  ngrok iniciado, mas não foi possível obter a URL automaticamente."
    echo "   Acesse: http://localhost:4040 para ver a URL do ngrok"
    echo ""
fi

# Manter script rodando
echo "Pressione Ctrl+C para parar o ngrok..."
wait $NGROK_PID


