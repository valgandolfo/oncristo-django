#!/bin/bash

# ============================================
# Script de Diagnóstico do Servidor OnCristo
# Gera relatório completo de saúde do sistema
# ============================================

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}========== $1 ==========${NC}"
    echo ""
}

print_ok() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# ============================================
# 1. INFORMAÇÕES DO SISTEMA
# ============================================

print_header "INFORMAÇÕES DO SISTEMA"

echo "Hostname: $(hostname)"
echo "Data/Hora: $(date '+%Y-%m-%d %H:%M:%S UTC')"
echo "Uptime: $(uptime -p)"
echo "Sistema: $(lsb_release -d | cut -f2)"
echo "Kernel: $(uname -r)"
echo "Processadores: $(nproc)"

# ============================================
# 2. ESPAÇO EM DISCO
# ============================================

print_header "ESPAÇO EM DISCO"

df -h | grep -E '^/dev/|Filesystem'

echo ""
echo "Espaço disponível na raiz:"
AVAILABLE=$(df / | tail -1 | awk '{print $4}')
TOTAL=$(df / | tail -1 | awk '{print $2}')
PERCENT=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')

if [ "$PERCENT" -lt 80 ]; then
    print_ok "Uso: $PERCENT% - Margem adequada"
elif [ "$PERCENT" -lt 90 ]; then
    print_warning "Uso: $PERCENT% - Considere limpeza"
else
    print_error "Uso: $PERCENT% - CRÍTICO! Limpe espaço imediatamente"
fi

# ============================================
# 3. TAMANHO DO MYSQL
# ============================================

print_header "BANCO DE DADOS MySQL"

MYSQL_SIZE=$(du -sh /var/lib/mysql 2>/dev/null || echo "Erro ao calcular")
echo "Tamanho total: $MYSQL_SIZE"

if systemctl is-active --quiet mysql; then
    print_ok "MySQL: ATIVO"
    
    # Listar tamanho das databases
    echo ""
    echo "Tamanho por database:"
    mysql -u root -e "SELECT table_schema, ROUND(SUM(data_length+index_length)/1024/1024, 2) AS 'Size (MB)' FROM information_schema.tables GROUP BY table_schema ORDER BY SUM(data_length+index_length) DESC;" 2>/dev/null || echo "Não foi possível conectar ao MySQL"
else
    print_error "MySQL: INATIVO"
fi

# ============================================
# 4. MEMÓRIA
# ============================================

print_header "MEMÓRIA"

free -h

echo ""
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100)}')
echo "Uso de memória: $MEMORY_USAGE%"

if [ "$MEMORY_USAGE" -lt 80 ]; then
    print_ok "Memória adequada"
elif [ "$MEMORY_USAGE" -lt 90 ]; then
    print_warning "Memória sob pressão"
else
    print_error "MEMÓRIA CRÍTICA!"
fi

# ============================================
# 5. SERVIÇOS CRÍTICOS
# ============================================

print_header "SERVIÇOS CRÍTICOS"

services=("mysql" "nginx" "gunicorn_oncristo")

for service in "${services[@]}"; do
    if systemctl is-active --quiet "$service"; then
        print_ok "$service: ATIVO"
    else
        print_error "$service: INATIVO"
    fi
done

# ============================================
# 6. VOLUMES MONTADOS
# ============================================

print_header "VOLUMES E BLOCK DEVICES"

lsblk

# ============================================
# 7. CONECTIVIDADE
# ============================================

print_header "CONECTIVIDADE"

echo "IP do servidor:"
hostname -I

echo ""
echo "Portas em escuta:"
netstat -tlnp 2>/dev/null | grep -E ':80|:443|:3306|:8000' || ss -tlnp | grep -E ':80|:443|:3306|:8000'

# ============================================
# 8. LOGS DE ERRO RECENTES
# ============================================

print_header "LOGS RECENTES"

echo "Django/Gunicorn (últimos 10 erros):"
journalctl -u gunicorn_oncristo -n 10 --no-pager 2>/dev/null || echo "Sem logs de erro"

echo ""
echo "MySQL (últimos 5 avisos):"
tail -5 /var/log/mysql/error.log 2>/dev/null || echo "Sem acesso aos logs"

# ============================================
# 9. CONEXÃO DE REDE
# ============================================

print_header "REDE"

echo "Testes de conectividade:"

if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
    print_ok "Internet: ATIVA"
else
    print_error "Internet: INATIVA"
fi

if ping -c 1 digitaloceanspaces.com >/dev/null 2>&1; then
    print_ok "DigitalOcean Spaces: ALCANÇÁVEL"
else
    print_warning "DigitalOcean Spaces: NÃO ALCANÇÁVEL"
fi

# ============================================
# 10. RESUMO FINAL
# ============================================

print_header "RESUMO"

echo "Servidor: $(hostname) ($(hostname -I))"
echo "Sistema: Ubuntu 25.04 | Kernel $(uname -r)"
echo "Django: Rodando via Gunicorn + Nginx"
echo "Banco: MySQL ($(du -sh /var/lib/mysql 2>/dev/null))"
echo "Disco: $AVAILABLE de $TOTAL disponível"
echo "Data do relatório: $(date '+%Y-%m-%d %H:%M:%S UTC')"

echo ""
print_ok "Diagnóstico concluído!"
echo ""
