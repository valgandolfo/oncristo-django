#!/bin/bash

# ============================================
# Script para Sincronizar do Servidor para Local
# ============================================

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configurações
SERVER_IP="137.184.116.197"
SERVER_USER="root"
LOCAL_DIR="/home/joaonote/oncristo.local"

print_info() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_step() {
    echo -e "${BLUE}→${NC} $1"
}

# Diretório no servidor
SERVER_DIR="/home/oncristo"

echo ""
echo "=========================================="
echo "🔄 SINCRONIZAR DO SERVIDOR PARA LOCAL"
echo "=========================================="
echo ""

print_step "Verificando conexão com servidor..."
if ssh -o ConnectTimeout=5 ${SERVER_USER}@${SERVER_IP} "[ -d ${SERVER_DIR} ]" 2>/dev/null; then
    print_info "Diretório encontrado: ${SERVER_DIR}"
else
    print_error "Não foi possível conectar ao servidor ou diretório não encontrado!"
    print_error "Verifique se está conectado via SSH ou se o diretório existe."
    exit 1
fi

print_step "Fazendo backup local antes de sincronizar..."
cd ${LOCAL_DIR}
if [ -d .git ]; then
    git stash push -m "Backup antes de sincronizar do servidor - $(date +'%Y-%m-%d %H:%M:%S')" || true
    print_info "Backup local criado"
fi

print_step "Sincronizando arquivos do servidor..."
print_warning "Isso irá sobrescrever arquivos locais!"

# Excluir arquivos que não devem ser sincronizados
rsync -avz --progress \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env*' \
    --exclude='*.log' \
    --exclude='staticfiles' \
    --exclude='media' \
    --exclude='backup_*' \
    --exclude='*.tar.gz' \
    ${SERVER_USER}@${SERVER_IP}:${SERVER_DIR}/ ${LOCAL_DIR}/

print_info "Sincronização concluída!"

print_step "Verificando status do Git..."
cd ${LOCAL_DIR}
git status --short | head -20

echo ""
print_info "Sincronização concluída com sucesso!"
print_warning "Verifique as mudanças antes de fazer commit!"
echo ""
echo "Para ver o que mudou:"
echo "  git status"
echo "  git diff"
echo ""
echo "Para restaurar o backup local:"
echo "  git stash list"
echo "  git stash pop"

