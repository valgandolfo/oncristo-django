#!/bin/bash
# Execute este script LOCALMENTE
# Ele copia o pacote do servidor e extrai

set -e

SERVER_IP="137.184.116.197"
SERVER_USER="root"
LOCAL_DIR="/home/joaonote/oncristo.local"

echo "=========================================="
echo "🔄 COPIAR ARQUIVOS DO SERVIDOR"
echo "=========================================="
echo ""

echo "1. Primeiro, execute no servidor (via SSH):"
echo "   cd /home/oncristo"
echo "   tar --exclude='venv' --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.env*' --exclude='*.log' --exclude='staticfiles' --exclude='media' --exclude='backup_*' --exclude='*.tar.gz' -czf /tmp/oncristo_servidor.tar.gz ."
echo ""
echo "2. Depois execute este script localmente para copiar:"
echo "   ./copiar_do_servidor.sh"
echo ""
echo "Ou copie manualmente:"
echo "   scp root@137.184.116.197:/tmp/oncristo_servidor.tar.gz /tmp/"
echo "   cd /home/joaonote/oncristo.local"
echo "   tar -xzf /tmp/oncristo_servidor.tar.gz"
echo ""

# Verificar se o arquivo existe no servidor
echo "Verificando se existe pacote no servidor..."
if ssh ${SERVER_USER}@${SERVER_IP} "test -f /tmp/oncristo_servidor.tar.gz"; then
    echo "✓ Pacote encontrado no servidor"
    echo ""
    echo "Copiando pacote do servidor..."
    scp ${SERVER_USER}@${SERVER_IP}:/tmp/oncristo_servidor.tar.gz /tmp/
    
    echo "Fazendo backup local..."
    cd ${LOCAL_DIR}
    git stash push -m "Backup antes de copiar do servidor - $(date +'%Y-%m-%d %H:%M:%S')" || true
    
    echo "Extraindo arquivos..."
    tar -xzf /tmp/oncristo_servidor.tar.gz -C ${LOCAL_DIR}
    
    echo ""
    echo "✓ Arquivos copiados com sucesso!"
    echo ""
    echo "Verifique as mudanças:"
    echo "  cd ${LOCAL_DIR}"
    echo "  git status"
else
    echo "✗ Pacote não encontrado no servidor"
    echo ""
    echo "Execute primeiro no servidor:"
    echo "  cd /home/oncristo"
    echo "  tar --exclude='venv' --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.env*' --exclude='*.log' --exclude='staticfiles' --exclude='media' --exclude='backup_*' --exclude='*.tar.gz' -czf /tmp/oncristo_servidor.tar.gz ."
fi

