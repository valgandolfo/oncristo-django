#!/bin/bash

# ============================================
# Script de Deploy no Servidor - OnCristo
# Execute este script NO SERVIDOR após fazer git push
# ============================================

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

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

SERVER_DIR="/home/oncristo"
cd "$SERVER_DIR"

echo ""
echo "=========================================="
echo "🚀 DEPLOY ONCRISTO - SERVIDOR"
echo "=========================================="
echo ""

# Fazer backup antes do deploy
print_step "Criando backup do projeto atual..."
BACKUP_DIR="backup_antes_deploy_$(date +%Y%m%d_%H%M%S)"
mkdir -p "/root/$BACKUP_DIR"
cp -r app_igreja "/root/$BACKUP_DIR/" 2>/dev/null || true
cp -r pro_igreja "/root/$BACKUP_DIR/" 2>/dev/null || true
cp -r templates "/root/$BACKUP_DIR/" 2>/dev/null || true
cp -r static "/root/$BACKUP_DIR/" 2>/dev/null || true
cp manage.py "/root/$BACKUP_DIR/" 2>/dev/null || true
cp requirements.txt "/root/$BACKUP_DIR/" 2>/dev/null || true
cp .env_production "/root/$BACKUP_DIR/" 2>/dev/null || true
print_info "Backup criado em: /root/$BACKUP_DIR"

# Atualizar código do Git
print_step "Atualizando código do Git..."
if [ -d ".git" ]; then
    git fetch origin
    git reset --hard origin/main || git reset --hard origin/master
    print_info "Código atualizado do Git"
else
    print_warning "Repositório Git não encontrado. Pulando atualização."
fi

# Ativar ambiente virtual
print_step "Ativando ambiente virtual..."
if [ -d "venv" ]; then
    source venv/bin/activate
    print_info "Ambiente virtual ativado"
else
    print_warning "Ambiente virtual não encontrado. Criando..."
    python3 -m venv venv
    source venv/bin/activate
    print_info "Ambiente virtual criado"
fi

# Instalar/atualizar dependências
print_step "Instalando/atualizando dependências Python..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
print_info "Dependências instaladas"

# Aplicar migrações
print_step "Aplicando migrações do banco de dados..."
export DJANGO_ENV=production
python manage.py migrate --noinput
print_info "Migrações aplicadas"

# Coletar arquivos estáticos
print_step "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput
print_info "Arquivos estáticos coletados"

# Reiniciar Gunicorn
print_step "Reiniciando serviço Gunicorn..."
if systemctl is-active --quiet gunicorn_oncristo; then
    systemctl restart gunicorn_oncristo
    print_info "Gunicorn reiniciado"
else
    print_warning "Gunicorn não está ativo. Tentando iniciar..."
    systemctl start gunicorn_oncristo || print_error "Erro ao iniciar Gunicorn"
fi

# Verificar status do Gunicorn
sleep 2
if systemctl is-active --quiet gunicorn_oncristo; then
    print_info "Gunicorn está rodando corretamente"
else
    print_error "Gunicorn não está rodando!"
    systemctl status gunicorn_oncristo --no-pager -l
    exit 1
fi

# Verificar Nginx
print_step "Verificando Nginx..."
if systemctl is-active --quiet nginx; then
    if nginx -t 2>/dev/null; then
        systemctl reload nginx
        print_info "Nginx recarregado"
    else
        print_warning "Erro na configuração do Nginx (mas continuando...)"
    fi
else
    print_warning "Nginx não está rodando"
fi

echo ""
echo "=========================================="
print_info "✅ DEPLOY CONCLUÍDO COM SUCESSO!"
echo "=========================================="
echo ""
echo "🌐 Acesse: https://oncristo.com.br"
echo ""

