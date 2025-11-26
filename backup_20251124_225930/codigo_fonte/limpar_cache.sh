#!/bin/bash

# Script para limpar cache do Django e arquivos estáticos
# Autor: Sistema OnCristo
# Data: $(date)

echo "🧹 Iniciando limpeza de cache..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para exibir status
show_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

show_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

show_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

show_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Limpar cache do Django
show_status "Limpando cache do Django..."
python manage.py clear_cache 2>/dev/null || {
    show_warning "Comando clear_cache não encontrado, usando alternativa..."
    python manage.py shell -c "
from django.core.cache import cache
cache.clear()
print('Cache do Django limpo!')
"
}

# 2. Limpar arquivos de cache Python
show_status "Limpando arquivos .pyc..."
find . -name "*.pyc" -delete 2>/dev/null
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
show_success "Arquivos .pyc removidos"

# 3. Limpar cache do navegador (criar arquivo .htaccess para forçar refresh)
show_status "Criando configuração para evitar cache do navegador..."
cat > static/.htaccess << 'EOF'
# Evitar cache de arquivos estáticos em desenvolvimento
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType text/css "access plus 0 seconds"
    ExpiresByType application/javascript "access plus 0 seconds"
    ExpiresByType text/javascript "access plus 0 seconds"
    ExpiresByType image/png "access plus 0 seconds"
    ExpiresByType image/jpg "access plus 0 seconds"
    ExpiresByType image/jpeg "access plus 0 seconds"
    ExpiresByType image/gif "access plus 0 seconds"
</IfModule>

<IfModule mod_headers.c>
    <FilesMatch "\.(css|js|png|jpg|jpeg|gif|ico|svg)$">
        Header set Cache-Control "no-cache, no-store, must-revalidate"
        Header set Pragma "no-cache"
        Header set Expires "0"
    </FilesMatch>
</IfModule>
EOF
show_success "Arquivo .htaccess criado em static/"

# 4. Coletar arquivos estáticos (força regeneração)
show_status "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear
show_success "Arquivos estáticos recolhidos"

# 5. Limpar logs antigos
show_status "Limpando logs antigos..."
find . -name "*.log" -mtime +7 -delete 2>/dev/null
show_success "Logs antigos removidos"

# 6. Limpar cache do sistema (se disponível)
show_status "Limpando cache do sistema..."
if command -v apt-get &> /dev/null; then
    sudo apt-get clean 2>/dev/null || show_warning "Não foi possível limpar cache do apt"
fi

# 7. Adicionar timestamp aos arquivos JS para forçar refresh
show_status "Adicionando timestamp aos arquivos JavaScript..."
TIMESTAMP=$(date +%s)
for js_file in static/js/*.js; do
    if [ -f "$js_file" ]; then
        # Criar backup
        cp "$js_file" "${js_file}.backup"
        # Adicionar comentário com timestamp
        echo "// Cache bust: $TIMESTAMP" >> "$js_file"
        show_success "Timestamp adicionado a $(basename "$js_file")"
    fi
done

# 8. Criar script para limpeza rápida
show_status "Criando script de limpeza rápida..."
cat > limpar_cache_rapido.sh << 'EOF'
#!/bin/bash
echo "🚀 Limpeza rápida de cache..."
python manage.py collectstatic --noinput --clear
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
echo "✅ Cache limpo!"
EOF
chmod +x limpar_cache_rapido.sh
show_success "Script de limpeza rápida criado"

# 9. Mostrar informações do sistema
show_status "Informações do sistema:"
echo "  - Diretório atual: $(pwd)"
echo "  - Usuário: $(whoami)"
echo "  - Data/Hora: $(date)"
echo "  - Espaço em disco:"
df -h . | tail -1

# 10. Instruções para o usuário
echo ""
echo "🎯 INSTRUÇÕES PARA EVITAR CACHE:"
echo "  1. Use Ctrl+Shift+R para hard refresh no navegador"
echo "  2. Ative 'Disable cache' no DevTools (F12 → Network)"
echo "  3. Execute './limpar_cache_rapido.sh' para limpeza rápida"
echo "  4. Use modo incógnito para testes"
echo ""

show_success "✅ Limpeza de cache concluída!"
echo "💡 Execute './limpar_cache_rapido.sh' sempre que precisar de uma limpeza rápida"
