#!/bin/bash
# Script para iniciar o servidor Django com VPN ativa

echo "======================================"
echo "  INICIANDO SERVIDOR ONCRISTO"
echo "======================================"

cd /home/joaonote/oncristo.local

# Ativa o ambiente virtual
source venv/bin/activate

# Verifica se o servidor já está rodando
if pgrep -f "manage.py runserver" > /dev/null; then
    echo "⚠️  Servidor já está rodando!"
    echo "Para parar: pkill -f 'manage.py runserver'"
    exit 1
fi

# Inicia o servidor
echo "🚀 Iniciando servidor Django..."
python manage.py runserver 0.0.0.0:8000 > /tmp/django_server.log 2>&1 &

# Aguarda 2 segundos
sleep 2

# Verifica se iniciou corretamente
if curl -s http://localhost:8000 > /dev/null; then
    echo "✅ Servidor iniciado com SUCESSO!"
    echo ""
    echo "======================================"
    echo "  ACESSO DO CELULAR (VPN ATIVA)"
    echo "======================================"
    echo ""
    echo "No celular, acesse:"
    echo "👉 http://192.168.0.111:8000/"
    echo ""
    echo "Seu celular: 192.168.0.102"
    echo "Servidor:    192.168.0.111"
    echo ""
    echo "======================================"
    echo ""
    echo "Para ver logs: tail -f /tmp/django_server.log"
    echo "Para parar:    pkill -f 'manage.py runserver'"
    echo ""
else
    echo "❌ Erro ao iniciar servidor!"
    echo "Verifique os logs: cat /tmp/django_server.log"
fi

