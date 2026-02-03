#!/bin/bash
# Backup local antes de subir o deploy. Execute na raiz do projeto.

set -e
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DIR_BACKUP="backups"
NOME_ARCHIVE="oncristo_backup_${TIMESTAMP}.tar.gz"

cd "$(dirname "$0")"
mkdir -p "$DIR_BACKUP"

echo "Fazendo backup antes do deploy (só código, sem venv/media/backups)..."
tar --exclude='venv' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='staticfiles' \
    --exclude='media' \
    --exclude='backups' \
    --exclude='*.tar.gz' \
    --exclude='*.tgz' \
    --exclude='db.sqlite3' \
    --exclude='db.sqlite3-journal' \
    --exclude='.env_production' \
    --exclude='.env_local' \
    --exclude='*.log' \
    --exclude='node_modules' \
    --exclude='.cursor' \
    --exclude='mobile/.dart_tool' \
    --exclude='mobile/build' \
    --exclude='mobile/*/build' \
    --exclude='mobile/*/.dart_tool' \
    -czf "${DIR_BACKUP}/${NOME_ARCHIVE}" .

echo "Backup salvo: ${DIR_BACKUP}/${NOME_ARCHIVE}"
ls -lh "${DIR_BACKUP}/${NOME_ARCHIVE}"
