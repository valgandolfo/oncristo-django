#!/usr/bin/env python3
"""
Script para gerenciar o banco de dados do projeto Django
Execute: python db_manager.py
"""

import os
import sys
import django
from django.db import connection
from django.conf import settings

def setup_django():
    """Configura o Django para usar as configurações do projeto"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_igreja.settings')
    django.setup()

def listar_tabelas():
    """Lista todas as tabelas do banco de dados"""
    print("\n" + "="*60)
    print("📋 LISTANDO TODAS AS TABELAS DO BANCO DE DADOS")
    print("="*60)
    
    with connection.cursor() as cursor:
        # SQLite usa sqlite_master para listar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"📊 Total de tabelas: {len(tables)}")
        print("\n📋 Tabelas encontradas:")
        for i, table in enumerate(tables, 1):
            table_name = table[0]
            print(f"{i:2d}. {table_name}")
    
    return [table[0] for table in tables]

def mostrar_estrutura_tabela(table_name):
    """Mostra a estrutura de uma tabela específica"""
    print(f"\n" + "="*60)
    print(f"🏗️  ESTRUTURA DA TABELA: {table_name}")
    print("="*60)
    
    with connection.cursor() as cursor:
        # SQLite usa PRAGMA table_info para mostrar estrutura
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"📊 Total de campos: {len(columns)}")
        print("\n📋 Campos da tabela:")
        print(f"{'Campo':<20} {'Tipo':<20} {'Not Null':<10} {'Primary Key':<12} {'Default':<15}")
        print("-" * 80)
        
        for column in columns:
            field_name = column[1]
            field_type = column[2]
            not_null = "YES" if column[3] else "NO"
            primary_key = "YES" if column[5] else "NO"
            default = str(column[4]) if column[4] is not None else 'NULL'
            
            print(f"{field_name:<20} {field_type:<20} {not_null:<10} {primary_key:<12} {default:<15}")

def listar_registros_tabela(table_name, limit=10):
    """Lista os registros de uma tabela específica"""
    print(f"\n" + "="*60)
    print(f"📄 REGISTROS DA TABELA: {table_name}")
    print("="*60)
    
    with connection.cursor() as cursor:
        # Primeiro, contar total de registros
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = cursor.fetchone()[0]
        print(f"📊 Total de registros: {total}")
        
        if total == 0:
            print("❌ Nenhum registro encontrado!")
            return
        
        # Listar registros
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        records = cursor.fetchall()
        
        # Obter nomes das colunas usando PRAGMA
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"\n📋 Primeiros {len(records)} registros:")
        print("-" * 80)
        
        # Cabeçalho
        header = " | ".join(f"{col:<15}" for col in columns)
        print(header)
        print("-" * 80)
        
        # Registros
        for record in records:
            row = " | ".join(f"{str(val):<15}" for val in record)
            print(row)

def escolher_tabela_por_numero(tabelas):
    """Permite escolher uma tabela pelo número"""
    if not tabelas:
        print("❌ Nenhuma tabela encontrada!")
        return None
    
    print("\n📋 Escolha uma tabela pelo número:")
    for i, table_name in enumerate(tabelas, 1):
        print(f"{i:2d}. {table_name}")
    
    while True:
        try:
            escolha = input(f"\nDigite o número da tabela (1-{len(tabelas)}): ").strip()
            numero = int(escolha)
            
            if 1 <= numero <= len(tabelas):
                return tabelas[numero - 1]
            else:
                print(f"❌ Número inválido! Escolha entre 1 e {len(tabelas)}")
        except ValueError:
            print("❌ Digite um número válido!")

def menu_principal():
    """Menu principal do script"""
    while True:
        print("\n" + "="*60)
        print("🗄️  GERENCIADOR DE BANCO DE DADOS - PROJETO ON CRISTO")
        print("="*60)
        print("1. 📋 Listar todas as tabelas")
        print("2. 🏗️  Ver estrutura de uma tabela")
        print("3. 📄 Listar registros de uma tabela")
        print("4. 🔍 Buscar tabelas por nome")
        print("5. ❌ Sair")
        print("="*60)
        
        opcao = input("\nEscolha uma opção (1-5): ").strip()
        
        if opcao == "1":
            listar_tabelas()
            
        elif opcao == "2":
            tabelas = listar_tabelas()
            if tabelas:
                table_name = escolher_tabela_por_numero(tabelas)
                if table_name:
                    mostrar_estrutura_tabela(table_name)
                    
        elif opcao == "3":
            tabelas = listar_tabelas()
            if tabelas:
                table_name = escolher_tabela_por_numero(tabelas)
                if table_name:
                    try:
                        limit_input = input("Quantos registros mostrar? (padrão: 10): ").strip()
                        limit = int(limit_input) if limit_input else 10
                        listar_registros_tabela(table_name, limit)
                    except ValueError:
                        print("❌ Valor inválido! Usando padrão de 10 registros.")
                        listar_registros_tabela(table_name)
                    
        elif opcao == "4":
            termo = input("\nDigite o termo para buscar: ").strip()
            print(f"\n🔍 Buscando tabelas que contêm '{termo}':")
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?", [f'%{termo}%'])
                tables = cursor.fetchall()
                
                if tables:
                    for i, table in enumerate(tables, 1):
                        print(f"{i}. {table[0]}")
                else:
                    print("❌ Nenhuma tabela encontrada!")
                    
        elif opcao == "5":
            print("\n👋 Saindo do gerenciador de banco de dados...")
            break
            
        else:
            print("❌ Opção inválida! Escolha de 1 a 5.")

def main():
    """Função principal"""
    try:
        print("🚀 Iniciando gerenciador de banco de dados...")
        setup_django()
        print("✅ Django configurado com sucesso!")
        
        menu_principal()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("💡 Certifique-se de estar no diretório do projeto Django")
        sys.exit(1)

if __name__ == "__main__":
    main()
