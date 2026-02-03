#!/bin/bash
# Script para verificar e configurar firewall

echo "======================================"
echo "  VERIFICANDO FIREWALL"
echo "======================================"

# Verifica status do ufw
if command -v ufw &> /dev/null; then
    echo "Status do Firewall:"
    sudo ufw status
    
    echo ""
    echo "Adicionando regra para porta 8000..."
    sudo ufw allow 8000/tcp
    echo "✅ Porta 8000 liberada!"
else
    echo "ufw não encontrado. Verificando iptables..."
fi

# Verifica se a porta está aberta
echo ""
echo "Portas escutando na 8000:"
sudo netstat -tlnp | grep :8000 || sudo ss -tlnp | grep :8000 || echo "Porta 8000 não está aberta"

echo ""
echo "IPs disponíveis:"
ip addr show | grep "inet " | grep -v "127.0.0.1"

