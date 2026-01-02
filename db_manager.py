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

def get_database_type():
    """Detecta o tipo de banco de dados (sqlite ou mysql)"""
    engine = settings.DATABASES['default']['ENGINE']
    if 'sqlite' in engine.lower():
        return 'sqlite'
    elif 'mysql' in engine.lower():
        return 'mysql'
    else:
        return 'unknown'

def listar_tabelas():
    """Lista todas as tabelas do banco de dados"""
    print("\n" + "="*60)
    print("📋 LISTANDO TODAS AS TABELAS DO BANCO DE DADOS")
    print("="*60)
    
    db_type = get_database_type()
    
    with connection.cursor() as cursor:
        if db_type == 'sqlite':
            # SQLite usa sqlite_master para listar tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        elif db_type == 'mysql':
            # MySQL usa INFORMATION_SCHEMA
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = DATABASE()")
        else:
            # Fallback genérico
            cursor.execute("SHOW TABLES")
        
        tables = cursor.fetchall()
        
        print(f"📊 Total de tabelas: {len(tables)}")
        print(f"🗄️  Tipo de banco: {db_type.upper()}")
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
    
    db_type = get_database_type()
    
    with connection.cursor() as cursor:
        if db_type == 'sqlite':
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
        elif db_type == 'mysql':
            # MySQL usa DESCRIBE ou SHOW COLUMNS
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            
            print(f"📊 Total de campos: {len(columns)}")
            print("\n📋 Campos da tabela:")
            print(f"{'Campo':<20} {'Tipo':<25} {'Null':<10} {'Key':<10} {'Default':<15}")
            print("-" * 80)
            
            for column in columns:
                field_name = column[0]
                field_type = column[1]
                null = column[2]
                key = column[3]
                default = str(column[4]) if column[4] is not None else 'NULL'
                
                print(f"{field_name:<20} {field_type:<25} {null:<10} {key:<10} {default:<15}")
        else:
            print("⚠️  Tipo de banco não suportado para esta operação.")

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
        
        # Obter nomes das colunas
        db_type = get_database_type()
        if db_type == 'sqlite':
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
        elif db_type == 'mysql':
            cursor.execute(f"DESCRIBE {table_name}")
            columns = [col[0] for col in cursor.fetchall()]
        else:
            # Fallback: usar description do cursor
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
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

def excluir_registros_tabela(table_name):
    """Exclui todos os registros de uma tabela específica (com confirmação)"""
    print(f"\n" + "="*60)
    print(f"⚠️  EXCLUIR TODOS OS REGISTROS DA TABELA: {table_name}")
    print("="*60)
    
    with connection.cursor() as cursor:
        # Primeiro, contar total de registros
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = cursor.fetchone()[0]
        
        if total == 0:
            print("ℹ️  A tabela já está vazia. Nenhum registro para excluir.")
            return
        
        print(f"📊 Total de registros na tabela: {total}")
        print(f"⚠️  ATENÇÃO: Esta operação é IRREVERSÍVEL!")
        print(f"⚠️  Todos os {total} registros serão PERMANENTEMENTE excluídos!")
        
        # Primeira confirmação
        print("\n" + "="*60)
        confirmacao1 = input(f"⚠️  Digite 'SIM' para confirmar a exclusão de TODOS os registros: ").strip()
        
        if confirmacao1.upper() != 'SIM':
            print("❌ Operação cancelada. Nenhum registro foi excluído.")
            return
        
        # Segunda confirmação (dupla verificação)
        print("\n" + "="*60)
        print(f"⚠️  ÚLTIMA CHANCE! Esta ação não pode ser desfeita!")
        confirmacao2 = input(f"⚠️  Digite o nome da tabela '{table_name}' para confirmar: ").strip()
        
        if confirmacao2 != table_name:
            print("❌ Nome da tabela não confere. Operação cancelada.")
            return
        
        # Terceira confirmação final
        print("\n" + "="*60)
        print(f"⚠️  CONFIRMAÇÃO FINAL!")
        print(f"⚠️  Você está prestes a excluir {total} registros da tabela '{table_name}'")
        confirmacao3 = input(f"⚠️  Digite 'CONFIRMAR' para prosseguir: ").strip()
        
        if confirmacao3.upper() != 'CONFIRMAR':
            print("❌ Operação cancelada. Nenhum registro foi excluído.")
            return
        
        # Executar exclusão
        try:
            print(f"\n🔄 Excluindo {total} registros...")
            cursor.execute(f"DELETE FROM {table_name}")
            registros_excluidos = cursor.rowcount
            
            # Verificar se realmente foi excluído
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            registros_restantes = cursor.fetchone()[0]
            
            print("="*60)
            print(f"✅ Operação concluída com sucesso!")
            print(f"📊 Registros excluídos: {registros_excluidos}")
            print(f"📊 Registros restantes: {registros_restantes}")
            print("="*60)
            
        except Exception as e:
            print("="*60)
            print(f"❌ Erro ao excluir registros: {e}")
            print("="*60)
            raise

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
        print("5. 🗑️  Excluir todos os registros de uma tabela")
        print("6. ❌ Sair")
        print("="*60)
        
        opcao = input("\nEscolha uma opção (1-6): ").strip()
        
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
            
            db_type = get_database_type()
            with connection.cursor() as cursor:
                if db_type == 'sqlite':
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?", [f'%{termo}%'])
                elif db_type == 'mysql':
                    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME LIKE %s", [f'%{termo}%'])
                else:
                    cursor.execute(f"SHOW TABLES LIKE '%{termo}%'")
                
                tables = cursor.fetchall()
                
                if tables:
                    for i, table in enumerate(tables, 1):
                        print(f"{i}. {table[0]}")
                else:
                    print("❌ Nenhuma tabela encontrada!")
                    
        elif opcao == "5":
            tabelas = listar_tabelas()
            if tabelas:
                table_name = escolher_tabela_por_numero(tabelas)
                if table_name:
                    excluir_registros_tabela(table_name)
                    
        elif opcao == "6":
            print("\n👋 Saindo do gerenciador de banco de dados...")
            break
            
        else:
            print("❌ Opção inválida! Escolha de 1 a 6.")

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
