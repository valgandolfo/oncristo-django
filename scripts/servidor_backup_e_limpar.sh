#!/bin/bash
# ============================================================
# RODAR NO TERMINAL DO SERVIDOR (DigitalOcean)
# Faz backup do projeto atual (sem banco) e remove /home/oncristo
# para depois subir a versão local via rsync.
# ============================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="/home/oncristo"
BACKUP_BASE="/root/backups"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   BACKUP (sem DB) e REMOÇÃO de ${PROJECT_DIR}${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}⚠${NC} Pasta $PROJECT_DIR não existe. Nada a fazer."
    exit 0
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_BASE}/oncristo_pre_subida_${TIMESTAMP}"
mkdir -p "$BACKUP_BASE"

echo -e "${BLUE}[1/4]${NC} Parando serviços (gunicorn)..."
systemctl stop gunicorn_oncristo 2>/dev/null || true
sleep 1
echo -e "${GREEN}✓${NC} Serviços parados"
echo ""

echo -e "${BLUE}[2/4]${NC} Fazendo backup do projeto (código + media, SEM banco)..."
mkdir -p "$BACKUP_DIR"
tar -czf "${BACKUP_DIR}/codigo_fonte.tar.gz" \
    -C /home \
    --exclude='oncristo/venv' \
    --exclude='oncristo/.git' \
    --exclude='oncristo/__pycache__' \
    --exclude='oncristo/*/__pycache__' \
    --exclude='oncristo/*/*/__pycache__' \
    --exclude='oncristo/*/*/*/__pycache__' \
    --exclude='oncristo/*.pyc' \
    --exclude='oncristo/db.sqlite3' \
    --exclude='oncristo/db.sqlite3-journal' \
    --exclude='oncristo/staticfiles' \
    oncristo 2>/dev/null || true

if [ -d "${PROJECT_DIR}/media" ] && [ -n "$(ls -A ${PROJECT_DIR}/media 2>/dev/null)" ]; then
    tar -czf "${BACKUP_DIR}/media.tar.gz" -C "$PROJECT_DIR" media
    echo -e "${GREEN}✓${NC} media incluída no backup"
fi

echo -e "${GREEN}✓${NC} Backup salvo em: ${BACKUP_DIR}"
echo ""

echo -e "${BLUE}[3/4]${NC} Removendo pasta ${PROJECT_DIR}..."
rm -rf "$PROJECT_DIR"
echo -e "${GREEN}✓${NC} Pasta removida"
echo ""

echo -e "${BLUE}[4/4]${NC} Recriando pasta vazia para receber o upload..."
mkdir -p "$PROJECT_DIR"
chown "$(whoami):$(whoami)" "$PROJECT_DIR" 2>/dev/null || true
echo -e "${GREEN}✓${NC} Pasta criada"
echo ""

echo -e "${GREEN}Concluído.${NC}"
echo "Próximo passo: na sua máquina local, rode o script de subida (rsync)."
echo "Backup disponível em: ${BACKUP_DIR}"
echo ""
