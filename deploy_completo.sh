#!/bin/bash

# ============================================
# Script de Deploy Completo - OnCristo
# Digital Ocean: root@137.184.116.197
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
GIT_REPO="https://github.com/valgandolfo/oncristo-django.git"
DOMAIN="oncristo.com.br"

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

# ============================================
# ETAPA 1: Preparar código local
# ============================================

echo ""
echo "=========================================="
echo "🚀 DEPLOY ONCRISTO - DIGITAL OCEAN"
echo "=========================================="
echo ""

print_step "ETAPA 1: Preparando código local..."

# Verificar se está no diretório do projeto
if [ ! -f "manage.py" ]; then
    print_error "Execute este script no diretório raiz do projeto"
    exit 1
fi

# Verificar se há mudanças não commitadas
if [ -n "$(git status --porcelain)" ]; then
    print_warning "Há mudanças não commitadas. Deseja fazer commit? (s/n)"
    read -r resposta
    if [ "$resposta" = "s" ] || [ "$resposta" = "S" ]; then
        print_step "Fazendo commit das mudanças..."
        git add .
        git commit -m "Deploy: $(date +'%Y-%m-%d %H:%M:%S')" || {
            print_error "Erro ao fazer commit. Verifique as mudanças."
            exit 1
        }
        print_info "Commit realizado com sucesso"
    else
        print_warning "Pulando commit. As mudanças locais não serão enviadas."
    fi
fi

# Fazer push para o repositório
print_step "Enviando código para o GitHub..."
if git push origin main 2>&1; then
    print_info "Código enviado para o GitHub"
else
    print_error "Erro ao enviar código para o GitHub"
    print_warning "Deseja continuar mesmo assim? (s/n)"
    read -r resposta
    if [ "$resposta" != "s" ] && [ "$resposta" != "S" ]; then
        exit 1
    fi
fi

# ============================================
# ETAPA 2: Conectar ao servidor e fazer deploy
# ============================================

echo ""
print_step "ETAPA 2: Conectando ao servidor e fazendo deploy..."

# Verificar se consegue conectar ao servidor
print_step "Verificando conexão com o servidor..."
if ssh -o ConnectTimeout=5 -o BatchMode=yes "${SERVER_USER}@${SERVER_IP}" exit 2>/dev/null; then
    print_info "Conexão com servidor OK"
else
    print_error "Não foi possível conectar ao servidor ${SERVER_USER}@${SERVER_IP}"
    print_warning "Certifique-se de que:"
    echo "  1. Você tem acesso SSH configurado"
    echo "  2. A chave SSH está adicionada ao servidor"
    echo "  3. O servidor está acessível"
    exit 1
fi

# Executar deploy no servidor
print_step "Executando deploy no servidor..."

ssh "${SERVER_USER}@${SERVER_IP}" << 'ENDSSH'
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

print_info "✅ Deploy no servidor concluído!"

ENDSSH

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    print_info "✅ DEPLOY CONCLUÍDO COM SUCESSO!"
    echo "=========================================="
    echo ""
    echo "🌐 Acesse: https://${DOMAIN}"
    echo ""
    print_info "Verifique o site para confirmar que está funcionando corretamente."
    echo ""
else
    echo ""
    print_error "❌ Erro durante o deploy no servidor"
    echo ""
    exit 1
fi

