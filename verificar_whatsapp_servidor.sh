#!/bin/bash

# ============================================
# Script para Verificar Configuração WhatsApp
# Execute no servidor: ssh root@137.184.116.197
# ============================================

set -e

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

echo ""
echo "=========================================="
echo "🔍 VERIFICAÇÃO CONFIGURAÇÃO WHATSAPP"
echo "=========================================="
echo ""

PROJECT_DIR="/home/oncristo"
ENV_FILE="${PROJECT_DIR}/.env_production"

# Verificar se está no servidor
if [ ! -d "${PROJECT_DIR}" ]; then
    print_error "Este script deve ser executado no servidor!"
    print_info "Conecte-se primeiro: ssh root@137.184.116.197"
    exit 1
fi

cd "${PROJECT_DIR}"

# 1. Verificar arquivo .env_production
print_step "1. Verificando arquivo .env_production..."
if [ -f "${ENV_FILE}" ]; then
    print_info "Arquivo .env_production encontrado"
else
    print_error "Arquivo .env_production NÃO encontrado!"
    exit 1
fi

# 2. Verificar variáveis do WhatsApp
print_step "2. Verificando variáveis do WhatsApp..."

WHATSAPP_API_KEY=$(grep "^WHATSAPP_API_KEY=" "${ENV_FILE}" | cut -d'=' -f2 | tr -d '"' | tr -d "'" || echo "")
WHATSAPP_CHANNEL_ID=$(grep "^WHATSAPP_CHANNEL_ID=" "${ENV_FILE}" | cut -d'=' -f2 | tr -d '"' | tr -d "'" || echo "")
WHATSAPP_BASE_URL=$(grep "^WHATSAPP_BASE_URL=" "${ENV_FILE}" | cut -d'=' -f2 | tr -d '"' | tr -d "'" || echo "")
SITE_URL=$(grep "^SITE_URL=" "${ENV_FILE}" | cut -d'=' -f2 | tr -d '"' | tr -d "'" || echo "")

if [ -n "${WHATSAPP_API_KEY}" ] && [ "${WHATSAPP_API_KEY}" != "" ]; then
    print_info "WHATSAPP_API_KEY: ${WHATSAPP_API_KEY:0:10}... (${#WHATSAPP_API_KEY} caracteres)"
else
    print_error "WHATSAPP_API_KEY NÃO encontrada ou vazia!"
fi

if [ -n "${WHATSAPP_CHANNEL_ID}" ] && [ "${WHATSAPP_CHANNEL_ID}" != "" ]; then
    print_info "WHATSAPP_CHANNEL_ID: ${WHATSAPP_CHANNEL_ID}"
else
    print_error "WHATSAPP_CHANNEL_ID NÃO encontrada ou vazia!"
fi

if [ -n "${WHATSAPP_BASE_URL}" ] && [ "${WHATSAPP_BASE_URL}" != "" ]; then
    print_info "WHATSAPP_BASE_URL: ${WHATSAPP_BASE_URL}"
else
    print_warning "WHATSAPP_BASE_URL não encontrada (usando padrão)"
fi

if [ -n "${SITE_URL}" ] && [ "${SITE_URL}" != "" ]; then
    print_info "SITE_URL: ${SITE_URL}"
else
    print_warning "SITE_URL não encontrada"
fi

# 3. Verificar código do webhook
print_step "3. Verificando código do webhook..."
WEBHOOK_FILE="${PROJECT_DIR}/app_igreja/views/area_publica/views_whatsapp_api.py"

if [ -f "${WEBHOOK_FILE}" ]; then
    if grep -q "def get_api_config():" "${WEBHOOK_FILE}"; then
        print_info "Função get_api_config() encontrada (código atualizado)"
    else
        print_warning "Função get_api_config() NÃO encontrada (código pode estar desatualizado)"
    fi
else
    print_error "Arquivo views_whatsapp_api.py não encontrado!"
fi

# 4. Verificar status do Gunicorn
print_step "4. Verificando status do Gunicorn..."
if systemctl is-active --quiet gunicorn_oncristo; then
    print_info "Gunicorn está rodando"
    
    # Verificar última reinicialização
    LAST_RESTART=$(systemctl show gunicorn_oncristo -p ActiveEnterTimestamp --value)
    print_info "Última reinicialização: ${LAST_RESTART}"
else
    print_error "Gunicorn NÃO está rodando!"
    print_warning "Execute: systemctl start gunicorn_oncristo"
fi

# 5. Testar carregamento das variáveis no Python
print_step "5. Testando carregamento das variáveis no Python..."
cd "${PROJECT_DIR}"

if [ -d "venv" ]; then
    source venv/bin/activate
    
    PYTHON_TEST=$(python3 << EOF
import os
import sys
sys.path.insert(0, '${PROJECT_DIR}')

# Carregar .env_production
from dotenv import load_dotenv
load_dotenv('${ENV_FILE}')

api_key = os.getenv('WHATSAPP_API_KEY', '')
channel_id = os.getenv('WHATSAPP_CHANNEL_ID', '')

if api_key and channel_id:
    print("OK")
else:
    print("ERRO")
    sys.exit(1)
EOF
)
    
    if [ "${PYTHON_TEST}" = "OK" ]; then
        print_info "Variáveis carregadas corretamente no Python"
    else
        print_error "Erro ao carregar variáveis no Python"
    fi
else
    print_warning "Ambiente virtual não encontrado"
fi

# 6. Verificar endpoint do webhook
print_step "6. Verificando endpoint do webhook..."
WEBHOOK_URL="${SITE_URL}/app_igreja/api/whatsapp/webhook/"

if [ -n "${SITE_URL}" ]; then
    print_info "URL do webhook: ${WEBHOOK_URL}"
    print_info "Configure esta URL no dashboard da Whapi Cloud"
else
    print_warning "SITE_URL não configurada, não é possível determinar a URL do webhook"
fi

# Resumo
echo ""
echo "=========================================="
if [ -n "${WHATSAPP_API_KEY}" ] && [ -n "${WHATSAPP_CHANNEL_ID}" ] && systemctl is-active --quiet gunicorn_oncristo; then
    print_info "✅ Configuração WhatsApp: OK"
    print_info "✅ Gunicorn: Rodando"
    echo ""
    print_info "Próximos passos:"
    echo "  1. Configure o webhook no Whapi Cloud: ${WEBHOOK_URL}"
    echo "  2. Teste enviando uma mensagem"
    echo "  3. Verifique os logs: journalctl -u gunicorn_oncristo -n 50 | grep whatsapp"
else
    print_error "❌ Configuração incompleta!"
    echo ""
    if [ -z "${WHATSAPP_API_KEY}" ] || [ -z "${WHATSAPP_CHANNEL_ID}" ]; then
        print_error "Adicione as variáveis WHATSAPP_API_KEY e WHATSAPP_CHANNEL_ID no .env_production"
    fi
    if ! systemctl is-active --quiet gunicorn_oncristo; then
        print_error "Inicie o Gunicorn: systemctl start gunicorn_oncristo"
    fi
fi
echo "=========================================="
echo ""
