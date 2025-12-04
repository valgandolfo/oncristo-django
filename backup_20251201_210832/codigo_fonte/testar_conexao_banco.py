#!/usr/bin/env python3
"""
Script para testar conexão com o banco de dados MySQL
Execute: python testar_conexao_banco.py
"""

import os
import sys
import django
from django.conf import settings
from django.db import connection

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_igreja.settings')
os.environ['DJANGO_ENV'] = 'production'

django.setup()

def testar_conexao():
    """Testa a conexão com o banco de dados"""
    print("🔍 Testando conexão com o banco de dados...")
    print("=" * 50)
    
    try:
        # Tentar conectar
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        if result:
            print("✅ Conexão com o banco de dados estabelecida com sucesso!")
            print(f"✅ Banco: {settings.DATABASES['default']['NAME']}")
            print(f"✅ Host: {settings.DATABASES['default']['HOST']}")
            print(f"✅ Porta: {settings.DATABASES['default']['PORT']}")
            
            # Verificar versão do MySQL
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                print(f"✅ Versão MySQL: {version}")
            
            return True
        else:
            print("❌ Erro: Não foi possível conectar ao banco")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados:")
        print(f"   {type(e).__name__}: {str(e)}")
        return False

if __name__ == '__main__':
    sucesso = testar_conexao()
    sys.exit(0 if sucesso else 1)

