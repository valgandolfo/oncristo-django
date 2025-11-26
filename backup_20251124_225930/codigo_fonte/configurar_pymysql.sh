#!/bin/bash

# Script para configurar PyMySQL no servidor

cd /home/oncristo

# 1. Remover mysqlclient do requirements.txt
echo "Removendo mysqlclient do requirements.txt..."
sed -i '/mysqlclient==/d' requirements.txt

# 2. Criar arquivo __init__.py para PyMySQL
echo "Configurando PyMySQL no Django..."
cat > pro_igreja/__init__.py << 'EOF'
import pymysql
pymysql.install_as_MySQLdb()
EOF

echo "✅ Configuração concluída!"
echo ""
echo "Agora execute:"
echo "  source venv/bin/activate"
echo "  pip install -r requirements.txt"

