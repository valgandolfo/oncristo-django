#!/bin/bash
# ============================================================
# RODAR NO TERMINAL DO SERVIDOR (DigitalOcean)
# Cria o venv DENTRO de /home/oncristo (nunca na raiz /).
# Este arquivo já está em /home/oncristo/scripts/ após o rsync.
# No servidor: cd /home/oncristo && bash scripts/servidor_criar_venv_em_oncristo.sh
# ============================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="/home/oncristo"
VENV_DIR="${PROJECT_DIR}/venv"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   CRIAR VENV EM ${PROJECT_DIR}${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}✗${NC} Pasta ${PROJECT_DIR} não existe. Crie-a antes (ou rode o rsync)."
    exit 1
fi

# Garantir que estamos com permissão de escrita no projeto (ex.: após rsync)
if [ ! -w "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}⚠${NC} Sem permissão de escrita em ${PROJECT_DIR}. Ajustando dono para $(whoami)..."
    chown -R "$(whoami):$(whoami)" "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"
echo -e "${GREEN}✓${NC} Diretório atual: $(pwd)"

if [ -d "$VENV_DIR" ]; then
    echo -e "${GREEN}✓${NC} venv já existe em ${VENV_DIR}"
else
    echo -e "${BLUE}→${NC} Criando venv em ${VENV_DIR}..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} venv criado"
fi

echo ""
echo -e "${BLUE}Próximos comandos (rode no servidor, dentro de ${PROJECT_DIR}):${NC}"
echo ""
echo "  cd ${PROJECT_DIR}"
echo "  source venv/bin/activate"
echo "  pip install -r requirements.txt"
echo "  export DJANGO_ENV=production   # se usar variável para produção"
echo "  python manage.py migrate --noinput"
echo "  python manage.py collectstatic --noinput --clear"
echo "  systemctl start gunicorn_oncristo && systemctl reload nginx"
echo ""
