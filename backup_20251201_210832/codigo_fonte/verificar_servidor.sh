#!/bin/bash

# Script para verificar se os arquivos foram transferidos corretamente
# Execute este script NO SERVIDOR (via SSH)

echo "🔍 Verificando arquivos no servidor..."
echo ""

cd /home/oncristo

# Verificar se backends.py existe
echo "1️⃣ Verificando app_igreja/backends.py..."
if [ -f "app_igreja/backends.py" ]; then
    echo "   ✅ Arquivo existe!"
    echo "   📄 Conteúdo (primeiras 10 linhas):"
    head -10 app_igreja/backends.py | sed 's/^/      /'
else
    echo "   ❌ Arquivo NÃO existe!"
fi

echo ""
echo "2️⃣ Verificando pro_igreja/settings.py..."
if [ -f "pro_igreja/settings.py" ]; then
    echo "   ✅ Arquivo existe!"
    echo "   🔍 Verificando AUTHENTICATION_BACKENDS..."
    if grep -q "AUTHENTICATION_BACKENDS" pro_igreja/settings.py; then
        echo "   ✅ AUTHENTICATION_BACKENDS encontrado!"
        echo "   📄 Configuração:"
        grep -A 3 "AUTHENTICATION_BACKENDS" pro_igreja/settings.py | sed 's/^/      /'
    else
        echo "   ❌ AUTHENTICATION_BACKENDS NÃO encontrado!"
    fi
else
    echo "   ❌ Arquivo NÃO existe!"
fi

echo ""
echo "3️⃣ Verificando usuários no banco..."
source venv/bin/activate
export DJANGO_ENV=production

python manage.py shell << 'EOF'
from django.contrib.auth.models import User
users = User.objects.all()
if users.exists():
    print("   ✅ Usuários encontrados:")
    for user in users:
        print(f"      - Username: {user.username}")
        print(f"        Email: {user.email}")
        print(f"        Superuser: {user.is_superuser}")
        print(f"        Staff: {user.is_staff}")
        print("")
else:
    print("   ⚠️  Nenhum usuário encontrado no banco!")
EOF

echo ""
echo "4️⃣ Verificando status do Gunicorn..."
sudo systemctl status gunicorn_oncristo --no-pager | head -15

echo ""
echo "✅ Verificação concluída!"

