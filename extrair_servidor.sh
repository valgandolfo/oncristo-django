#!/bin/bash

# Script para extrair o pacote do servidor no ambiente local

set -e

LOCAL_DIR="/home/joaonote/oncristo.local"
PACOTE="/tmp/oncristo_servidor.tar.gz"

echo "=========================================="
echo "📦 EXTRAIR PACOTE DO SERVIDOR"
echo "=========================================="
echo ""

if [ ! -f "$PACOTE" ]; then
    echo "❌ Arquivo $PACOTE não encontrado!"
    echo ""
    echo "Primeiro, copie o arquivo do servidor:"
    echo "  scp root@137.184.116.197:/tmp/oncristo_servidor.tar.gz /tmp/"
    echo ""
    echo "Ou baixe via HTTP se configurou servidor web no DO"
    exit 1
fi

echo "✓ Arquivo encontrado: $PACOTE"
echo "  Tamanho: $(ls -lh $PACOTE | awk '{print $5}')"
echo ""

echo "Fazendo backup local..."
cd ${LOCAL_DIR}
git stash push -m "Backup antes de extrair do servidor - $(date +'%Y-%m-%d %H:%M:%S')" || true

echo ""
echo "Extraindo arquivos..."
tar -xzf ${PACOTE} -C ${LOCAL_DIR}

echo ""
echo "✓ Extração concluída!"
echo ""
echo "Verificando mudanças:"
git status --short | head -30

echo ""
echo "Para ver todas as mudanças:"
echo "  git status"
echo "  git diff"

