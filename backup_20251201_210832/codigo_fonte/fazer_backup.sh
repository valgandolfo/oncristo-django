#!/bin/bash

# Script de Backup Completo do Projeto Oncristo
# Data: $(date +"%Y-%m-%d %H:%M:%S")

set -e  # Para em caso de erro

# Cores para output
VERDE='\033[0;32m'
AZUL='\033[0;34m'
AMARELO='\033[1;33m'
VERMELHO='\033[0;31m'
NC='\033[0m' # No Color

# Diretório do projeto
PROJETO_DIR="/home/joaonote/oncristo.local"
cd "$PROJETO_DIR"

# Timestamp para o backup
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backup_${TIMESTAMP}"
BACKUP_PATH="$PROJETO_DIR/$BACKUP_DIR"

echo -e "${AZUL}═══════════════════════════════════════════════════════════${NC}"
echo -e "${AZUL}    BACKUP COMPLETO DO PROJETO ONCRISTO${NC}"
echo -e "${AZUL}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Criar diretório de backup
echo -e "${AMARELO}[1/6]${NC} Criando diretório de backup..."
mkdir -p "$BACKUP_PATH"
mkdir -p "$BACKUP_PATH/codigo_fonte"
mkdir -p "$BACKUP_PATH/config"
mkdir -p "$BACKUP_PATH/media"
echo -e "${VERDE}✓${NC} Diretório criado: $BACKUP_DIR"
echo ""

# Backup do banco de dados
echo -e "${AMARELO}[2/6]${NC} Fazendo backup do banco de dados..."
if [ -f "db.sqlite3" ]; then
    cp db.sqlite3 "$BACKUP_PATH/db.sqlite3"
    DB_SIZE=$(du -h db.sqlite3 | cut -f1)
    echo -e "${VERDE}✓${NC} Banco de dados copiado ($DB_SIZE)"
else
    echo -e "${VERMELHO}⚠${NC} Arquivo db.sqlite3 não encontrado"
fi
echo ""

# Backup da pasta media
echo -e "${AMARELO}[3/6]${NC} Fazendo backup da pasta media..."
if [ -d "media" ] && [ "$(ls -A media 2>/dev/null)" ]; then
    tar -czf "$BACKUP_PATH/media.tar.gz" media/ 2>/dev/null || true
    if [ -f "$BACKUP_PATH/media.tar.gz" ]; then
        MEDIA_SIZE=$(du -h "$BACKUP_PATH/media.tar.gz" | cut -f1)
        echo -e "${VERDE}✓${NC} Pasta media compactada ($MEDIA_SIZE)"
    else
        echo -e "${VERMELHO}⚠${NC} Pasta media vazia ou erro ao compactar"
    fi
else
    echo -e "${VERMELHO}⚠${NC} Pasta media não encontrada ou vazia"
fi
echo ""

# Backup do código fonte (excluindo arquivos desnecessários)
echo -e "${AMARELO}[4/6]${NC} Fazendo backup do código fonte..."
rsync -av --progress \
    --exclude='venv/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='*.pyo' \
    --exclude='*.log' \
    --exclude='.git/' \
    --exclude='.vscode/' \
    --exclude='.idea/' \
    --exclude='*.swp' \
    --exclude='*.swo' \
    --exclude='*.tmp' \
    --exclude='*.cache' \
    --exclude='db.sqlite3' \
    --exclude='media/' \
    --exclude='staticfiles/' \
    --exclude='backup_*/' \
    --exclude='*.tar.gz' \
    --exclude='*.sql' \
    --exclude='logs/' \
    --exclude='.env*' \
    --exclude='cookies.txt' \
    "$PROJETO_DIR/" "$BACKUP_PATH/codigo_fonte/" > /dev/null 2>&1

CODIGO_SIZE=$(du -sh "$BACKUP_PATH/codigo_fonte" | cut -f1)
echo -e "${VERDE}✓${NC} Código fonte copiado ($CODIGO_SIZE)"
echo ""

# Backup de arquivos de configuração importantes
echo -e "${AMARELO}[5/6]${NC} Fazendo backup de configurações..."
if [ -f "gunicorn_config.py" ]; then
    cp gunicorn_config.py "$BACKUP_PATH/config/"
fi
if [ -f "nginx_oncristo.conf" ]; then
    cp nginx_oncristo.conf "$BACKUP_PATH/config/"
fi
if [ -f "requirements.txt" ]; then
    cp requirements.txt "$BACKUP_PATH/config/"
fi
if [ -f "deploy.sh" ]; then
    cp deploy.sh "$BACKUP_PATH/config/"
fi
if [ -f "iniciar_servidor.sh" ]; then
    cp iniciar_servidor.sh "$BACKUP_PATH/config/"
fi
echo -e "${VERDE}✓${NC} Configurações copiadas"
echo ""

# Criar arquivo de informações do backup
echo -e "${AMARELO}[6/6]${NC} Gerando informações do backup..."
cat > "$BACKUP_PATH/info_backup.txt" << EOF
═══════════════════════════════════════════════════════════
    INFORMAÇÕES DO BACKUP - PROJETO ONCRISTO
═══════════════════════════════════════════════════════════

Data/Hora do Backup: $(date +"%Y-%m-%d %H:%M:%S")
Diretório do Backup: $BACKUP_DIR

CONTEÚDO DO BACKUP:
-------------------
✓ Código fonte completo (excluindo venv, cache, etc.)
✓ Banco de dados SQLite (db.sqlite3)
✓ Pasta media (compactada em media.tar.gz)
✓ Arquivos de configuração (gunicorn, nginx, requirements, etc.)

ESTATÍSTICAS:
------------
Tamanho do código fonte: $CODIGO_SIZE
Tamanho do banco de dados: $DB_SIZE
Tamanho da pasta media: $MEDIA_SIZE

ESTRUTURA DO BACKUP:
-------------------
$BACKUP_DIR/
├── codigo_fonte/          # Todo o código do projeto
├── config/                 # Arquivos de configuração
├── media.tar.gz           # Pasta media compactada
├── db.sqlite3             # Banco de dados
└── info_backup.txt        # Este arquivo

NOTAS:
------
- O backup foi criado excluindo arquivos temporários e cache
- Para restaurar, descompacte o código e restaure o banco de dados
- Verifique as configurações antes de fazer deploy em produção

═══════════════════════════════════════════════════════════
EOF

echo -e "${VERDE}✓${NC} Informações do backup geradas"
echo ""

# Criar arquivo compactado final
echo -e "${AMARELO}[EXTRA]${NC} Criando arquivo compactado final..."
cd "$PROJETO_DIR"
tar -czf "oncristo_backup_${TIMESTAMP}.tar.gz" "$BACKUP_DIR/" 2>/dev/null
if [ -f "oncristo_backup_${TIMESTAMP}.tar.gz" ]; then
    FINAL_SIZE=$(du -h "oncristo_backup_${TIMESTAMP}.tar.gz" | cut -f1)
    echo -e "${VERDE}✓${NC} Backup compactado criado: oncristo_backup_${TIMESTAMP}.tar.gz ($FINAL_SIZE)"
else
    echo -e "${VERMELHO}⚠${NC} Erro ao criar arquivo compactado"
fi
echo ""

# Resumo final
echo -e "${AZUL}═══════════════════════════════════════════════════════════${NC}"
echo -e "${VERDE}✓ BACKUP CONCLUÍDO COM SUCESSO!${NC}"
echo -e "${AZUL}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Diretório do backup: ${AMARELO}$BACKUP_DIR${NC}"
echo -e "Arquivo compactado: ${AMARELO}oncristo_backup_${TIMESTAMP}.tar.gz${NC}"
echo -e "Tamanho total: ${AMARELO}$FINAL_SIZE${NC}"
echo ""
echo -e "${AZUL}Pronto para deploy! 🚀${NC}"
echo ""

