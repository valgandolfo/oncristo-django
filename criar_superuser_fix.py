#!/usr/bin/env python
"""
Script rápido para criar/atualizar superusuário
Execute: python criar_superuser_fix.py
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_igreja.settings.local')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Configurações do superusuário
USERNAME = 'admin'
EMAIL = 'admin@oncristo.com.br'
PASSWORD = 'admin123'  # ALTERE ESTA SENHA!

print("Criando/atualizando superusuário...")

try:
    user = User.objects.get(username=USERNAME)
    print(f"Usuário '{USERNAME}' já existe. Atualizando...")
    user.email = EMAIL
    user.set_password(PASSWORD)
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()
    print(f"✓ Usuário '{USERNAME}' atualizado!")
except User.DoesNotExist:
    user = User.objects.create_user(
        username=USERNAME,
        email=EMAIL,
        password=PASSWORD,
        is_staff=True,
        is_superuser=True,
        is_active=True
    )
    print(f"✓ Usuário '{USERNAME}' criado!")

print(f"\nCredenciais:")
print(f"  Username: {USERNAME}")
print(f"  Email: {EMAIL}")
print(f"  Senha: {PASSWORD}")
print(f"\n⚠️  LEMBRE-SE DE ALTERAR A SENHA NO CÓDIGO E NO BANCO!")
