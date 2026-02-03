#!/bin/bash
# ============================================================
# RODAR NA SUA MÁQUINA LOCAL (com projeto atual)
# Envia o projeto para o servidor DO respeitando .gitignore.
# Requer: rsync, SSH configurado para o servidor.
# ============================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Ajuste: usuário e host do servidor DO
REMOTE_USER="${REMOTE_USER:-root}"
REMOTE_HOST="${REMOTE_HOST:-137.184.116.197}"
REMOTE_DIR="/home/oncristo"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
EXCLUDE_FILE="${SCRIPT_DIR}/rsync-exclude-from-gitignore.txt"

if [ ! -f "$EXCLUDE_FILE" ]; then
    echo -e "${RED}Arquivo de exclusões não encontrado: $EXCLUDE_FILE${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   SUBIR PROJETO PARA DO (respeitando .gitignore)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Projeto local: $PROJECT_DIR"
echo "Destino:       ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/"
echo "Exclusões:     $EXCLUDE_FILE"
echo ""

read -p "Executar no servidor backup + remoção de ${REMOTE_DIR} ANTES do rsync? (s/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[sS]$ ]]; then
    echo -e "${BLUE}[0/2]${NC} Rodando no servidor: backup (sem DB) e remoção da pasta..."
    SERVIDOR_SCRIPT="${SCRIPT_DIR}/servidor_backup_e_limpar.sh"
    if [ -f "$SERVIDOR_SCRIPT" ]; then
        ssh "${REMOTE_USER}@${REMOTE_HOST}" "bash -s" < "$SERVIDOR_SCRIPT"
    else
        echo -e "${RED}Script não encontrado: $SERVIDOR_SCRIPT${NC}"
        echo "Rode manualmente no terminal DO o script servidor_backup_e_limpar.sh e depois execute este script de novo."
        exit 1
    fi
    echo ""
fi

read -p "Continuar com rsync (upload)? (s/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[sS]$ ]]; then
    echo "Cancelado."
    exit 0
fi

echo -e "${BLUE}[1/1]${NC} Enviando arquivos com rsync..."
rsync -avz --progress \
    --exclude-from="$EXCLUDE_FILE" \
    --delete \
    "$PROJECT_DIR/" \
    "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/"

echo ""
echo -e "${GREEN}✓${NC} Upload concluído."
echo ""
echo "Próximo passo - no terminal do servidor (o script já está em ${REMOTE_DIR}/scripts/):"
echo ""
echo "  ssh ${REMOTE_USER}@${REMOTE_HOST}"
echo "  cd ${REMOTE_DIR} && bash scripts/servidor_criar_venv_em_oncristo.sh"
echo "  source venv/bin/activate"
echo "  pip install -r requirements.txt"
echo "  export DJANGO_ENV=production   # se usar"
echo "  python manage.py migrate --noinput"
echo "  python manage.py collectstatic --noinput --clear"
echo "  systemctl start gunicorn_oncristo && systemctl reload nginx"
echo ""
