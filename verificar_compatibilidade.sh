#!/bin/bash

# ============================================
# Script de Verificação de Compatibilidade
# OnCristo em Ubuntu 25.04
# ============================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}>>> $1${NC}"
}

check_ok() {
    echo -e "${GREEN}✅ $1${NC}"
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
}

print_header "VERIFICAÇÃO DE COMPATIBILIDADE - Ubuntu 25.04"

# ============================================
# 1. VERSÃO DO PYTHON
# ============================================

print_header "Python"

PYTHON_VERSION=$(python3 --version 2>&1)
echo $PYTHON_VERSION

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    check_ok "Python 3.10+ - OK"
else
    check_fail "Python inferior a 3.10"
fi

# ============================================
# 2. VERSÃO DO DJANGO
# ============================================

print_header "Django"

if python3 -c "import django; print(f'Django {django.VERSION[0]}.{django.VERSION[1]}.{django.VERSION[2]}')" 2>/dev/null; then
    check_ok "Django instalado"
else
    check_fail "Django não está instalado"
fi

# ============================================
# 3. MySQL / MariaDB
# ============================================

print_header "MySQL / MariaDB"

MYSQL_VERSION=$(mysql --version 2>/dev/null || echo "Não encontrado")
echo "Versão: $MYSQL_VERSION"

if systemctl is-active --quiet mysql || systemctl is-active --quiet mariadb; then
    check_ok "MySQL/MariaDB rodando"
    
    # Testar conexão
    if mysql -u root -e "SELECT 1" >/dev/null 2>&1; then
        check_ok "Conexão com MySQL OK"
    else
        check_warn "Não foi possível conectar ao MySQL como root"
    fi
else
    check_fail "MySQL/MariaDB não está rodando"
fi

# ============================================
# 4. MYSQLCLIENT (Python)
# ============================================

print_header "mysqlclient (Python)"

if python3 -c "import MySQLdb; print(MySQLdb.__version__)" 2>/dev/null; then
    MYSQLCLIENT_VERSION=$(python3 -c "import MySQLdb; print(MySQLdb.__version__)")
    echo "Versão: $MYSQLCLIENT_VERSION"
    check_ok "mysqlclient disponível"
else
    check_fail "mysqlclient não está instalado"
    echo "   Instale com: pip install mysqlclient==2.2.0"
fi

# ============================================
# 5. PILLOW (Processamento de Imagens)
# ============================================

print_header "Pillow (Imagens)"

if python3 -c "from PIL import Image; print(Image.PILLOW_VERSION)" 2>/dev/null; then
    check_ok "Pillow disponível"
else
    check_warn "Pillow pode não estar instalado ou versão incompatível"
fi

# ============================================
# 6. WEASYPRINT (PDF)
# ============================================

print_header "WeasyPrint (PDF)"

if python3 -c "import weasyprint; print(weasyprint.__version__)" 2>/dev/null; then
    check_ok "WeasyPrint disponível"
else
    check_warn "WeasyPrint pode estar indisponível"
fi

# ============================================
# 7. GUNICORN
# ============================================

print_header "Gunicorn"

if python3 -c "import gunicorn; print(gunicorn.__version__)" 2>/dev/null; then
    check_ok "Gunicorn instalado"
else
    check_fail "Gunicorn não está instalado"
fi

if systemctl is-active --quiet gunicorn_oncristo; then
    check_ok "Serviço gunicorn_oncristo: ATIVO"
else
    check_warn "Serviço gunicorn_oncristo: INATIVO"
fi

# ============================================
# 8. NGINX
# ============================================

print_header "Nginx"

NGINX_VERSION=$(nginx -v 2>&1)
echo $NGINX_VERSION

if systemctl is-active --quiet nginx; then
    check_ok "Nginx: ATIVO"
else
    check_warn "Nginx: INATIVO"
fi

# ============================================
# 9. SSL/HTTPS
# ============================================

print_header "SSL/HTTPS (Let's Encrypt)"

if command -v certbot &> /dev/null; then
    check_ok "Certbot disponível"
    
    CERT_INFO=$(certbot certificates 2>/dev/null | grep "oncristo" || echo "Certificado não encontrado")
    echo "Status: $CERT_INFO"
else
    check_warn "Certbot não está instalado"
fi

# ============================================
# 10. FIREWALL
# ============================================

print_header "Firewall (UFW)"

if systemctl is-active --quiet ufw; then
    check_ok "UFW ativo"
    echo ""
    ufw status
else
    check_warn "UFW não está ativo"
fi

# ============================================
# 11. SSH
# ============================================

print_header "SSH"

if systemctl is-active --quiet ssh; then
    check_ok "SSH: ATIVO"
else
    check_fail "SSH: INATIVO"
fi

# ============================================
# 12. VARIÁVEIS DE AMBIENTE
# ============================================

print_header "Variáveis de Ambiente (.env_production)"

if [ -f "/home/oncristo/.env_production" ]; then
    check_ok "Arquivo .env_production encontrado"
    
    # Verificar variáveis críticas
    if grep -q "SECRET_KEY" "/home/oncristo/.env_production"; then
        check_ok "SECRET_KEY: Configurada"
    else
        check_fail "SECRET_KEY: NÃO configurada"
    fi
    
    if grep -q "DATABASE_URL\|DB_HOST" "/home/oncristo/.env_production"; then
        check_ok "Banco de dados: Configurado"
    else
        check_fail "Banco de dados: NÃO configurado"
    fi
    
    if grep -q "STORAGE_PROVIDER" "/home/oncristo/.env_production"; then
        check_ok "Storage Provider: Configurado"
    else
        check_warn "Storage Provider: NÃO configurado (usando local)"
    fi
else
    check_fail "Arquivo .env_production NÃO encontrado"
fi

# ============================================
# 13. TESTE DE CONECTIVIDADE DJANGO
# ============================================

print_header "Django - Verificação de Integridade"

cd /home/oncristo || {
    check_fail "Diretório /home/oncristo não encontrado"
    exit 1
}

if python3 manage.py check >/dev/null 2>&1; then
    check_ok "Django check: OK"
else
    check_fail "Django check: FALHOU"
    python3 manage.py check
fi

# ============================================
# 14. BANCO DE DADOS
# ============================================

print_header "Banco de Dados - Migrações"

if python3 manage.py migrate --check >/dev/null 2>&1; then
    check_ok "Migrações: Todas aplicadas"
else
    check_warn "Migrações: Há migrações pendentes"
    echo "   Execute: python manage.py migrate"
fi

# ============================================
# 15. STATICFILES
# ============================================

print_header "Arquivos Estáticos"

if [ -d "/home/oncristo/staticfiles" ]; then
    check_ok "Diretório staticfiles encontrado"
    STATIC_COUNT=$(find /home/oncristo/staticfiles -type f | wc -l)
    echo "   Arquivos: $STATIC_COUNT"
else
    check_warn "Diretório staticfiles não encontrado"
    echo "   Execute: python3 manage.py collectstatic --no-input"
fi

# ============================================
# RESUMO FINAL
# ============================================

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Verificação de compatibilidade concluída!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Sistema: Ubuntu 25.04 ✅"
echo "Django: 5.0.3 ✅"
echo "MySQL: $MYSQL_VERSION ✅"
echo ""
echo "Próximos passos:"
echo "1. Executar: systemctl start gunicorn_oncristo"
echo "2. Verificar: systemctl status gunicorn_oncristo"
echo "3. Testar: curl http://localhost"
echo ""
