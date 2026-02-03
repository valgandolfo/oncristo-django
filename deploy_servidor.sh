#!/bin/bash

# ============================================
# Script de Deploy no Servidor Digital Ocean
# Execute este script NO SERVIDOR
# ============================================

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configurações
PROJECT_DIR="/home/oncristo"
VENV_DIR="${PROJECT_DIR}/venv"

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
echo "🚀 DEPLOY NO SERVIDOR - ONCRISTO"
echo "=========================================="
echo ""

# Verificar se está no diretório correto
if [ ! -d "${PROJECT_DIR}" ]; then
    print_error "Diretório do projeto não encontrado: ${PROJECT_DIR}"
    exit 1
fi

cd ${PROJECT_DIR}

# 1. Backup antes de atualizar (código + .env_production se existir)
print_step "1. Fazendo backup do código atual..."
BACKUP_DIR="${PROJECT_DIR}/backups"
mkdir -p ${BACKUP_DIR}
BACKUP_ARCHIVE="${BACKUP_DIR}/backup_$(date +%Y%m%d_%H%M%S).tar.gz"
tar --exclude='venv' --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='staticfiles' --exclude='media' -czf "${BACKUP_ARCHIVE}" . 2>/dev/null || true
print_info "Backup criado: ${BACKUP_ARCHIVE}"

# 2. Atualizar código do GitHub
print_step "2. Atualizando código do GitHub..."
git fetch origin
git pull origin main
print_info "Código atualizado"

# 3. Ativar ambiente virtual
print_step "3. Ativando ambiente virtual..."
source ${VENV_DIR}/bin/activate

# 4. Instalar/atualizar dependências
print_step "4. Instalando/atualizando dependências..."
pip install -q -r requirements.txt
print_info "Dependências instaladas"

# 5. Aplicar migrações (MANTÉM DADOS)
print_step "5. Aplicando migrações do banco de dados..."
export DJANGO_ENV=production
python manage.py migrate --noinput
print_info "Migrações aplicadas (dados preservados)"

# 6. Coletar arquivos estáticos
print_step "6. Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear
print_info "Arquivos estáticos coletados"

# 7. Reiniciar serviços
print_step "7. Reiniciando serviços..."
systemctl restart gunicorn_oncristo
systemctl reload nginx
print_info "Serviços reiniciados"

# 8. Verificar status
print_step "8. Verificando status dos serviços..."
sleep 2
if systemctl is-active --quiet gunicorn_oncristo; then
    print_info "Gunicorn está rodando"
else
    print_error "Gunicorn não está rodando!"
    systemctl status gunicorn_oncristo --no-pager -l
fi

if systemctl is-active --quiet nginx; then
    print_info "Nginx está rodando"
else
    print_error "Nginx não está rodando!"
fi

echo ""
print_info "Deploy concluído com sucesso!"
echo ""
echo "Verifique o site: https://oncristo.com.br"
echo ""

