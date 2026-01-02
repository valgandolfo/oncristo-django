#!/bin/bash

# ============================================
# Script para Resetar Migrações do Django
# ============================================
# Este script remove todas as migrações antigas
# e cria uma nova migração inicial limpa
# ============================================

echo "============================================"
echo "  RESETANDO MIGRAÇÕES DO DJANGO"
echo "============================================"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se está no diretório correto
if [ ! -f "manage.py" ]; then
    echo -e "${RED}ERRO: Este script deve ser executado na raiz do projeto Django${NC}"
    exit 1
fi

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    echo -e "${YELLOW}Ativando ambiente virtual...${NC}"
    source venv/bin/activate
fi

# 1. Fazer backup do banco de dados atual (caso exista)
if [ -f "db.sqlite3" ]; then
    echo -e "${YELLOW}Fazendo backup do banco de dados atual...${NC}"
    BACKUP_NAME="db_backup_$(date +%Y%m%d_%H%M%S).sqlite3"
    cp db.sqlite3 "$BACKUP_NAME"
    echo -e "${GREEN}Backup criado: $BACKUP_NAME${NC}"
fi

# 2. Deletar banco de dados atual
echo -e "${YELLOW}Removendo banco de dados atual...${NC}"
rm -f db.sqlite3
echo -e "${GREEN}Banco de dados removido${NC}"

# 3. Remover todas as migrações (exceto __init__.py)
echo -e "${YELLOW}Removendo migrações antigas...${NC}"
find app_igreja/migrations -type f -name "*.py" ! -name "__init__.py" -delete
find app_igreja/migrations -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo -e "${GREEN}Migrações antigas removidas${NC}"

# 4. Limpar cache de migrações do Django
echo -e "${YELLOW}Limpando cache de migrações...${NC}"
python manage.py migrate --fake-initial 2>/dev/null || true
rm -rf app_igreja/migrations/__pycache__ 2>/dev/null || true
echo -e "${GREEN}Cache limpo${NC}"

# 5. Criar nova migração inicial
echo -e "${YELLOW}Criando nova migração inicial...${NC}"
python manage.py makemigrations app_igreja

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Migração inicial criada com sucesso!${NC}"
else
    echo -e "${RED}ERRO ao criar migração inicial${NC}"
    exit 1
fi

# 6. Aplicar a migração inicial
echo -e "${YELLOW}Aplicando migração inicial...${NC}"
python manage.py migrate

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Migração aplicada com sucesso!${NC}"
else
    echo -e "${RED}ERRO ao aplicar migração${NC}"
    exit 1
fi

# 7. Criar superusuário (opcional)
echo ""
echo -e "${YELLOW}Deseja criar um superusuário agora? (s/n)${NC}"
read -r resposta
if [ "$resposta" = "s" ] || [ "$resposta" = "S" ]; then
    python manage.py createsuperuser
fi

echo ""
echo "============================================"
echo -e "${GREEN}  PROCESSO CONCLUÍDO COM SUCESSO!${NC}"
echo "============================================"
echo ""
echo "Próximos passos:"
echo "1. Seu banco de dados está limpo e pronto"
echo "2. Todas as migrações foram resetadas"
echo "3. Uma nova migração inicial foi criada"
echo ""
echo "Para produção na Digital Ocean:"
echo "- Configure o banco de dados PostgreSQL no settings.py"
echo "- Execute: python manage.py migrate"
echo "- Execute: python manage.py createsuperuser"
echo ""

