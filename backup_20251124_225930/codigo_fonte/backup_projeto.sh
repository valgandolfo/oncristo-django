#!/bin/bash
# Script de Backup Completo do Projeto OnCristo
# Data: $(date +%Y%m%d_%H%M%S)

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Data e hora para nome do backup
DATA_BACKUP=$(date +%Y%m%d_%H%M%S)
DIR_BACKUP="backup_${DATA_BACKUP}"
NOME_ARQUIVO="oncristo_backup_${DATA_BACKUP}.tar.gz"

echo -e "${BLUE}📦 INICIANDO BACKUP DO PROJETO ONCRISTO${NC}"
echo "=========================================="
echo ""

# Criar diretório de backup
mkdir -p "$DIR_BACKUP"
echo -e "${GREEN}✅ Diretório de backup criado: $DIR_BACKUP${NC}"

# 1. Backup do código fonte
echo -e "${BLUE}📁 Fazendo backup do código fonte...${NC}"
tar -czf "$DIR_BACKUP/codigo_fonte.tar.gz" \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='*.log' \
    --exclude='db.sqlite3' \
    --exclude='media' \
    --exclude='staticfiles' \
    --exclude='static' \
    --exclude='backup_*' \
    --exclude='*.tar.gz' \
    app_igreja/ \
    pro_igreja/ \
    templates/ \
    static/ \
    manage.py \
    requirements.txt \
    .env_production.example \
    .gitignore \
    deploy.sh \
    DEPLOY_GIT.md \
    2>/dev/null || true

echo -e "${GREEN}✅ Código fonte backup criado${NC}"

# 2. Backup do banco de dados SQLite (se existir)
if [ -f "db.sqlite3" ]; then
    echo -e "${BLUE}💾 Fazendo backup do banco de dados SQLite...${NC}"
    cp db.sqlite3 "$DIR_BACKUP/db.sqlite3"
    echo -e "${GREEN}✅ Banco de dados backup criado${NC}"
else
    echo -e "${YELLOW}⚠️  Banco de dados SQLite não encontrado (pode estar usando MySQL)${NC}"
fi

# 3. Backup de arquivos de configuração
echo -e "${BLUE}⚙️  Fazendo backup de arquivos de configuração...${NC}"
mkdir -p "$DIR_BACKUP/config"

# Backup de .env se existir (sem senhas em produção)
if [ -f ".env_local" ]; then
    cp .env_local "$DIR_BACKUP/config/.env_local.backup"
    echo -e "${GREEN}✅ .env_local backup criado${NC}"
fi

if [ -f ".env_production" ]; then
    # Criar versão sem senhas para backup
    sed 's/=.*/=REDACTED/g' .env_production > "$DIR_BACKUP/config/.env_production.backup" 2>/dev/null || true
    echo -e "${GREEN}✅ .env_production backup criado (senhas removidas)${NC}"
fi

# Backup de outros arquivos de config se existirem
[ -f "gunicorn_config.py" ] && cp gunicorn_config.py "$DIR_BACKUP/config/" 2>/dev/null || true
[ -f "nginx_oncristo.conf" ] && cp nginx_oncristo.conf "$DIR_BACKUP/config/" 2>/dev/null || true

echo -e "${GREEN}✅ Configurações backup criadas${NC}"

# 4. Backup de arquivos de mídia (se existirem localmente)
if [ -d "media" ]; then
    echo -e "${BLUE}🖼️  Fazendo backup de arquivos de mídia...${NC}"
    tar -czf "$DIR_BACKUP/media.tar.gz" media/ 2>/dev/null || true
    echo -e "${GREEN}✅ Arquivos de mídia backup criados${NC}"
else
    echo -e "${YELLOW}⚠️  Diretório media não encontrado (pode estar no S3)${NC}"
fi

# 5. Criar arquivo de informações do backup
echo -e "${BLUE}📝 Criando arquivo de informações do backup...${NC}"
cat > "$DIR_BACKUP/info_backup.txt" << EOF
BACKUP DO PROJETO ONCRISTO
==========================

Data/Hora: $(date '+%d/%m/%Y %H:%M:%S')
Sistema: $(uname -a)
Python: $(python3 --version 2>/dev/null || echo "Não encontrado")
Django: $(python3 -c "import django; print(django.get_version())" 2>/dev/null || echo "Não encontrado")

CONTEÚDO DO BACKUP:
- Código fonte completo (app_igreja, pro_igreja, templates, static)
- Banco de dados SQLite (se existir)
- Arquivos de configuração (.env, gunicorn, nginx)
- Arquivos de mídia (se existirem localmente)

OBSERVAÇÕES:
- Arquivos sensíveis (.env_production) tiveram senhas removidas
- Ambiente virtual (venv) não foi incluído
- Arquivos de cache e logs não foram incluídos
- Banco de dados MySQL deve ser feito separadamente no servidor

RESTAURAÇÃO:
1. Extrair código_fonte.tar.gz
2. Restaurar db.sqlite3 (se aplicável)
3. Configurar .env_production com senhas reais
4. Instalar dependências: pip install -r requirements.txt
5. Aplicar migrações: python manage.py migrate
EOF

echo -e "${GREEN}✅ Arquivo de informações criado${NC}"

# 6. Criar arquivo compactado final
echo -e "${BLUE}📦 Compactando backup completo...${NC}"
tar -czf "$NOME_ARQUIVO" "$DIR_BACKUP/"
echo -e "${GREEN}✅ Backup compactado criado: $NOME_ARQUIVO${NC}"

# 7. Calcular tamanho
TAMANHO=$(du -h "$NOME_ARQUIVO" | cut -f1)
echo ""
echo -e "${GREEN}✅ BACKUP CONCLUÍDO COM SUCESSO!${NC}"
echo "=========================================="
echo -e "📦 Arquivo: ${BLUE}$NOME_ARQUIVO${NC}"
echo -e "📊 Tamanho: ${BLUE}$TAMANHO${NC}"
echo -e "📁 Localização: ${BLUE}$(pwd)/$NOME_ARQUIVO${NC}"
echo ""
echo -e "${YELLOW}💡 DICA: Guarde este arquivo em local seguro!${NC}"

# Opcional: remover diretório temporário
read -p "Deseja remover o diretório temporário de backup? (s/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    rm -rf "$DIR_BACKUP"
    echo -e "${GREEN}✅ Diretório temporário removido${NC}"
else
    echo -e "${YELLOW}⚠️  Diretório temporário mantido: $DIR_BACKUP${NC}"
fi

