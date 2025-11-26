#!/usr/bin/env python3
"""
Script para gerar PDF do documento de comunicação Django
Execute: python gerar_pdf.py
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    try:
        import markdown2
        print("✅ markdown2 encontrado")
    except ImportError:
        print("❌ markdown2 não encontrado")
        print("💡 Instalando markdown2...")
        subprocess.run([sys.executable, "-m", "pip", "install", "markdown2"])
    
    try:
        import weasyprint
        print("✅ weasyprint encontrado")
    except ImportError:
        print("❌ weasyprint não encontrado")
        print("💡 Instalando weasyprint...")
        subprocess.run([sys.executable, "-m", "pip", "install", "weasyprint"])

def create_html_from_markdown():
    """Converte markdown para HTML"""
    try:
        import markdown2
        
        # Lê o arquivo markdown
        with open('FLUXO_COMUNICACAO_DJANGO.md', 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Converte para HTML
        html_content = markdown2.markdown(
            markdown_content,
            extras=[
                'tables',
                'fenced-code-blocks',
                'code-friendly',
                'cuddled-lists',
                'markdown-in-html',
                'toc'
            ]
        )
        
        # Cria HTML completo com CSS
        full_html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comunicação Cliente-Servidor Django</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        
        .container {{
            background-color: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            font-size: 2.5em;
        }}
        
        h2 {{
            color: #34495e;
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-top: 30px;
            font-size: 2em;
        }}
        
        h3 {{
            color: #2c3e50;
            font-size: 1.5em;
            margin-top: 25px;
        }}
        
        h4 {{
            color: #34495e;
            font-size: 1.2em;
            margin-top: 20px;
        }}
        
        p {{
            margin-bottom: 15px;
            text-align: justify;
        }}
        
        code {{
            background-color: #f8f9fa;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            color: #e74c3c;
        }}
        
        pre {{
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 20px 0;
        }}
        
        pre code {{
            background-color: transparent;
            color: inherit;
            padding: 0;
        }}
        
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding: 10px 20px;
            background-color: #ecf0f1;
            font-style: italic;
        }}
        
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin-bottom: 8px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        
        .highlight {{
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #ffc107;
            margin: 15px 0;
        }}
        
        .success {{
            background-color: #d4edda;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #28a745;
            margin: 15px 0;
        }}
        
        .error {{
            background-color: #f8d7da;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #dc3545;
            margin: 15px 0;
        }}
        
        .info {{
            background-color: #d1ecf1;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #17a2b8;
            margin: 15px 0;
        }}
        
        .diagram {{
            text-align: center;
            margin: 20px 0;
            font-family: monospace;
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
        }}
        
        .debug {{
            background-color: #e8f5e8;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 0.9em;
            margin: 10px 0;
            border-left: 4px solid #28a745;
        }}
        
        .toc {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        
        .toc ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        
        .toc li {{
            margin: 5px 0;
        }}
        
        .toc a {{
            text-decoration: none;
            color: #3498db;
        }}
        
        .toc a:hover {{
            text-decoration: underline;
        }}
        
        @media print {{
            body {{
                background-color: white;
                margin: 0;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
                padding: 0;
            }}
            
            h1, h2, h3, h4 {{
                page-break-after: avoid;
            }}
            
            pre, blockquote {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
    </div>
</body>
</html>
"""
        
        # Salva o HTML
        with open('FLUXO_COMUNICACAO_DJANGO.html', 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print("✅ HTML gerado com sucesso: FLUXO_COMUNICACAO_DJANGO.html")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar HTML: {e}")
        return False

def create_pdf_from_html():
    """Converte HTML para PDF"""
    try:
        from weasyprint import HTML
        
        # Gera PDF
        HTML('FLUXO_COMUNICACAO_DJANGO.html').write_pdf('FLUXO_COMUNICACAO_DJANGO.pdf')
        
        print("✅ PDF gerado com sucesso: FLUXO_COMUNICACAO_DJANGO.pdf")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando geração do PDF...")
    print("=" * 50)
    
    # Verifica dependências
    print("📦 Verificando dependências...")
    check_dependencies()
    print()
    
    # Verifica se o arquivo markdown existe
    if not os.path.exists('FLUXO_COMUNICACAO_DJANGO.md'):
        print("❌ Arquivo FLUXO_COMUNICACAO_DJANGO.md não encontrado!")
        return
    
    # Converte markdown para HTML
    print("📄 Convertendo Markdown para HTML...")
    if not create_html_from_markdown():
        return
    print()
    
    # Converte HTML para PDF
    print("📖 Convertendo HTML para PDF...")
    if not create_pdf_from_html():
        return
    print()
    
    # Verifica se o PDF foi criado
    if os.path.exists('FLUXO_COMUNICACAO_DJANGO.pdf'):
        file_size = os.path.getsize('FLUXO_COMUNICACAO_DJANGO.pdf') / 1024  # KB
        print("🎉 PDF gerado com sucesso!")
        print(f"📁 Arquivo: FLUXO_COMUNICACAO_DJANGO.pdf")
        print(f"📏 Tamanho: {file_size:.1f} KB")
        print()
        print("💡 Você pode agora:")
        print("   - Abrir o PDF no seu celular")
        print("   - Compartilhar com outros desenvolvedores")
        print("   - Usar como referência de estudo")
    else:
        print("❌ Erro: PDF não foi gerado!")

if __name__ == "__main__":
    main()
