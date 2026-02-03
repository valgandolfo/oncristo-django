#!/usr/bin/env python3
"""
GERENCIADOR DE BANCO DE DADOS ONCRISTO
Foco: Pente fino e localização de tabelas (ossadas de dinossauro).
"""

import os
import sys
import django

# --- CONFIGURAÇÃO DE AMBIENTE ---
def setup_django():
    """Configura o Django apontando para pro_igreja.settings."""
    # Garante que o diretório atual está no PATH do Python
    sys.path.append(os.getcwd())
    
    # Define o portão de entrada do projeto
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_igreja.settings')
    
    try:
        django.setup()
        from django.conf import settings
        engine = settings.DATABASES['default']['ENGINE']
        print(f"✅ Django configurado com sucesso!")
        print(f"🗄️  Banco Detectado: {engine}")
        print("="*60)
    except Exception as e:
        print(f"❌ Erro ao carregar as configurações: {e}")
        print("\n💡 DICA DO MESTRE: Verifique se você está na pasta ~/oncristo.local")
        print("💡 Tente rodar: touch pro_igreja/__init__.py")
        sys.exit(1)

# Importações que dependem do django.setup()
from django.db import connection

def listar_tabelas():
    """Lista todas as tabelas reais no banco (MySQL ou SQLite)."""
    print("\n📋 LISTANDO TODAS AS TABELAS")
    print("-" * 30)
    
    with connection.cursor() as cursor:
        # Detecta se é SQLite ou MySQL
        from django.conf import settings
        is_sqlite = 'sqlite' in settings.DATABASES['default']['ENGINE'].lower()
        
        if is_sqlite:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        else:
            cursor.execute("SHOW TABLES")
        
        tables = cursor.fetchall()
        
        if not tables:
            print("⚠️  Nenhuma tabela encontrada! O banco pode estar vazio.")
            return []

        for i, table in enumerate(tables, 1):
            print(f"{i:2d}. {table[0]}")
        
        return [table[0] for table in tables]

def ver_estrutura(table_name):
    """Mostra os campos e tipos da tabela."""
    print(f"\n🏗️  ESTRUTURA DA TABELA: {table_name}")
    print("-" * 30)
    
    with connection.cursor() as cursor:
        from django.conf import settings
        is_sqlite = 'sqlite' in settings.DATABASES['default']['ENGINE'].lower()
        
        if is_sqlite:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"{'ID':<3} {'Campo':<20} {'Tipo':<15} {'PK':<5}")
            for col in columns:
                print(f"{col[0]:<3} {col[1]:<20} {col[2]:<15} {'✅' if col[5] else '':<5}")
        else:
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            print(f"{'Campo':<20} {'Tipo':<15} {'Nulo':<5}")
            for col in columns:
                print(f"{col[0]:<20} {col[1]:<15} {col[2]:<5}")

def listar_dados(table_name):
    """Mostra os 5 primeiros registros para conferência."""
    print(f"\n📄 DADOS DA TABELA: {table_name} (Top 5)")
    print("-" * 30)
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()
            if not rows:
                print("ℹ️  Tabela sem registros.")
                return
            for row in rows:
                print(row)
        except Exception as e:
            print(f"❌ Erro ao ler dados: {e}")

def menu():
    """Interface principal."""
    setup_django()
    while True:
        print("\n" + "⚔️  ONCRISTO DATABASE MANAGER " + "⚔️")
        print("1. Listar Tabelas")
        print("2. Ver Estrutura de Tabela")
        print("3. Ver Dados de Tabela")
        print("4. Sair")
        
        op = input("\nEscolha (1-4): ").strip()
        
        if op == "1":
            listar_tabelas()
        elif op in ["2", "3"]:
            tabelas = listar_tabelas()
            if tabelas:
                try:
                    idx = int(input("\nDigite o número da tabela: "))
                    nome = tabelas[idx-1]
                    if op == "2": ver_estrutura(nome)
                    else: listar_dados(nome)
                except (ValueError, IndexError):
                    print("❌ Seleção inválida.")
        elif op == "4":
            print("👋 Até logo, Mestre!")
            break

if __name__ == "__main__":
    menu()
