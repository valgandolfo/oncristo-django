#!/bin/bash

# ============================================
# Script Simples para Sincronizar do Servidor
# Execute este script localmente
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
SERVER_DIR="/home/oncristo"
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

echo ""
echo "=========================================="
echo "🔄 SINCRONIZAR DO SERVIDOR PARA LOCAL"
echo "=========================================="
echo ""

print_step "Fazendo backup local antes de sincronizar..."
cd ${LOCAL_DIR}
if [ -d .git ]; then
    git stash push -m "Backup antes de sincronizar do servidor - $(date +'%Y-%m-%d %H:%M:%S')" || true
    print_info "Backup local criado (git stash)"
fi

print_step "Sincronizando arquivos do servidor..."
print_warning "Isso irá sobrescrever arquivos locais com os do servidor!"

# Sincronizar usando rsync
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
    --exclude='db.sqlite3' \
    --exclude='.DS_Store' \
    ${SERVER_USER}@${SERVER_IP}:${SERVER_DIR}/ ${LOCAL_DIR}/

print_info "Sincronização concluída!"

print_step "Verificando status do Git..."
cd ${LOCAL_DIR}
echo ""
echo "Arquivos modificados/adicionados:"
git status --short | head -30

echo ""
print_info "Sincronização concluída com sucesso!"
print_warning "Verifique as mudanças antes de fazer commit!"
echo ""
echo "Comandos úteis:"
echo "  git status          - Ver o que mudou"
echo "  git diff            - Ver diferenças detalhadas"
echo "  git stash list      - Ver backups salvos"
echo "  git stash pop       - Restaurar último backup"

