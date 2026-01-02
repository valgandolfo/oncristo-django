#!/bin/bash

# ============================================================
# 🚀 SCRIPT DE BACKUP COMPLETO - PROJETO ONCRISTO
# ============================================================
# Este script faz backup completo do projeto Django
# Execute: bash backup_completo.sh

echo "🚀 Iniciando backup completo do projeto OnCristo..."

# Criar diretório de backup com timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backup_oncristo_${TIMESTAMP}"
mkdir -p "$BACKUP_DIR"

echo "📁 Criando diretório de backup: $BACKUP_DIR"

# 1. BACKUP DO BANCO DE DADOS
echo "💾 Fazendo backup do banco de dados..."
python3 manage.py dumpdata --indent=2 --natural-foreign --natural-primary > "$BACKUP_DIR/database_backup.json"
echo "✅ Banco de dados salvo em: $BACKUP_DIR/database_backup.json"

# 2. BACKUP DOS ARQUIVOS DE MÍDIA
echo "📸 Fazendo backup dos arquivos de mídia..."
if [ -d "media" ]; then
    cp -r media "$BACKUP_DIR/"
    echo "✅ Arquivos de mídia salvos em: $BACKUP_DIR/media/"
else
    echo "⚠️  Diretório 'media' não encontrado"
fi

# 3. BACKUP DOS ARQUIVOS ESTÁTICOS
echo "🎨 Fazendo backup dos arquivos estáticos..."
if [ -d "static" ]; then
    cp -r static "$BACKUP_DIR/"
    echo "✅ Arquivos estáticos salvos em: $BACKUP_DIR/static/"
else
    echo "⚠️  Diretório 'static' não encontrado"
fi

# 4. BACKUP DO CÓDIGO FONTE
echo "📝 Fazendo backup do código fonte..."
# Copiar arquivos Python
find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" -not -path "./__pycache__/*" | while read file; do
    mkdir -p "$BACKUP_DIR/codigo_fonte/$(dirname "$file")"
    cp "$file" "$BACKUP_DIR/codigo_fonte/$file"
done

# Copiar templates
if [ -d "templates" ]; then
    cp -r templates "$BACKUP_DIR/"
    echo "✅ Templates salvos em: $BACKUP_DIR/templates/"
fi

# Copiar arquivos de configuração
cp manage.py "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  manage.py não encontrado"
cp requirements.txt "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  requirements.txt não encontrado"
cp .env* "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  Arquivos .env não encontrados"

echo "✅ Código fonte salvo em: $BACKUP_DIR/codigo_fonte/"

# 5. BACKUP DAS MIGRAÇÕES
echo "🔄 Fazendo backup das migrações..."
find . -name "migrations" -type d -not -path "./venv/*" -not -path "./.git/*" | while read dir; do
    mkdir -p "$BACKUP_DIR/migrations/$(dirname "$dir")"
    cp -r "$dir" "$BACKUP_DIR/migrations/$(dirname "$dir")/"
done
echo "✅ Migrações salvas em: $BACKUP_DIR/migrations/"

# 6. CRIAR ARQUIVO DE INFORMAÇÕES
echo "📋 Criando arquivo de informações..."
cat > "$BACKUP_DIR/INFO_BACKUP.txt" << EOF
============================================================
🚀 BACKUP COMPLETO - PROJETO ONCRISTO
============================================================
📅 Data do backup: $(date)
🖥️  Sistema: $(uname -a)
🐍 Python: $(python3 --version)
📦 Django: $(python3 -c "import django; print(django.get_version())" 2>/dev/null || echo "Não instalado")

📁 ESTRUTURA DO BACKUP:
├── database_backup.json     # Backup completo do banco de dados
├── media/                   # Arquivos de mídia (uploads)
├── static/                  # Arquivos estáticos (CSS, JS, imagens)
├── templates/               # Templates HTML
├── codigo_fonte/            # Código Python (.py)
├── migrations/              # Migrações do Django
├── manage.py               # Arquivo principal do Django
├── requirements.txt        # Dependências Python
├── .env*                   # Arquivos de configuração
└── INFO_BACKUP.txt         # Este arquivo

🔄 COMO RESTAURAR:
1. Instalar Python e Django
2. Criar ambiente virtual: python3 -m venv venv
3. Ativar: source venv/bin/activate
4. Instalar dependências: pip install -r requirements.txt
5. Restaurar banco: python3 manage.py loaddata database_backup.json
6. Copiar arquivos: cp -r media/ static/ templates/ ./
7. Executar: python3 manage.py runserver

⚠️  IMPORTANTE:
- Verifique as configurações de banco de dados
- Ajuste os caminhos conforme necessário
- Execute as migrações se necessário: python3 manage.py migrate

============================================================
EOF

echo "✅ Arquivo de informações criado: $BACKUP_DIR/INFO_BACKUP.txt"

# 7. COMPRIMIR BACKUP
echo "📦 Comprimindo backup..."
tar -czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"
echo "✅ Backup comprimido: ${BACKUP_DIR}.tar.gz"

# 8. CRIAR CHECKSUM
echo "🔐 Criando checksum..."
sha256sum "${BACKUP_DIR}.tar.gz" > "${BACKUP_DIR}.tar.gz.sha256"
echo "✅ Checksum criado: ${BACKUP_DIR}.tar.gz.sha256"

# 9. INFORMAÇÕES FINAIS
echo ""
echo "============================================================="
echo "🎉 BACKUP COMPLETO FINALIZADO!"
echo "============================================================="
echo "📁 Diretório: $BACKUP_DIR"
echo "📦 Arquivo: ${BACKUP_DIR}.tar.gz"
echo "🔐 Checksum: ${BACKUP_DIR}.tar.gz.sha256"
echo "📊 Tamanho: $(du -h "${BACKUP_DIR}.tar.gz" | cut -f1)"
echo ""
echo "🚀 PRÓXIMOS PASSOS:"
echo "1. Baixe o arquivo: ${BACKUP_DIR}.tar.gz"
echo "2. Baixe o checksum: ${BACKUP_DIR}.tar.gz.sha256"
echo "3. Verifique a integridade: sha256sum -c ${BACKUP_DIR}.tar.gz.sha256"
echo "4. Extraia: tar -xzf ${BACKUP_DIR}.tar.gz"
echo ""
echo "📋 Leia o arquivo INFO_BACKUP.txt para instruções de restauração"
echo "============================================================="

# 10. LIMPEZA (opcional)
read -p "🗑️  Deseja remover o diretório temporário? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$BACKUP_DIR"
    echo "✅ Diretório temporário removido"
else
    echo "📁 Diretório mantido: $BACKUP_DIR"
fi

echo "🎯 Backup finalizado com sucesso!"
