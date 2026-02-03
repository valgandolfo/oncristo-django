#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_igreja.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Resetar senha do admin
username = 'admin'
new_password = 'admin123'  # ALTERE ESTA SENHA APÓS O LOGIN!

try:
    user = User.objects.get(username=username)
    user.set_password(new_password)
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()
    print(f"✓ Senha do usuário '{username}' resetada com sucesso!")
    print(f"  Username: {username}")
    print(f"  Email: {user.email}")
    print(f"  Nova senha: {new_password}")
    print(f"\n⚠️  ALTERE A SENHA APÓS FAZER LOGIN!")
except User.DoesNotExist:
    # Criar se não existir
    user = User.objects.create_user(
        username=username,
        email='admin@oncristo.com.br',
        password=new_password,
        is_staff=True,
        is_superuser=True,
        is_active=True
    )
    print(f"✓ Superusuário '{username}' criado!")
    print(f"  Username: {username}")
    print(f"  Email: {user.email}")
    print(f"  Senha: {new_password}")
