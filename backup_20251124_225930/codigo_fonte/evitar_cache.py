#!/usr/bin/env python3
"""
Script Python para evitar cache em desenvolvimento
Adiciona timestamp aos arquivos estáticos
"""

import os
import time
from pathlib import Path

def adicionar_timestamp_js():
    """Adiciona timestamp aos arquivos JavaScript para evitar cache"""
    static_dir = Path('static/js')
    
    if not static_dir.exists():
        print("❌ Diretório static/js não encontrado")
        return
    
    timestamp = int(time.time())
    
    for js_file in static_dir.glob('*.js'):
        # Ler conteúdo atual
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se já tem timestamp
        if f'// Cache bust: {timestamp}' in content:
            print(f"⏭️  {js_file.name} já tem timestamp atual")
            continue
        
        # Remover timestamps antigos
        lines = content.split('\n')
        filtered_lines = [line for line in lines if not line.startswith('// Cache bust:')]
        
        # Adicionar novo timestamp
        filtered_lines.append(f'// Cache bust: {timestamp}')
        
        # Salvar arquivo
        with open(js_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(filtered_lines))
        
        print(f"✅ Timestamp adicionado a {js_file.name}")

def limpar_cache_django():
    """Limpa cache do Django"""
    try:
        import django
        from django.conf import settings
        from django.core.cache import cache
        
        # Configurar Django se não estiver configurado
        if not settings.configured:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oncristo.settings')
            django.setup()
        
        cache.clear()
        print("✅ Cache do Django limpo")
    except Exception as e:
        print(f"❌ Erro ao limpar cache Django: {e}")

def main():
    print("🧹 Iniciando limpeza de cache...")
    
    # Limpar cache Django
    limpar_cache_django()
    
    # Adicionar timestamp aos JS
    adicionar_timestamp_js()
    
    print("✅ Limpeza concluída!")
    print("💡 Use Ctrl+Shift+R no navegador para hard refresh")

if __name__ == "__main__":
    main()
