#!/usr/bin/env python3
"""
Script para testar e configurar o webhook do ngrok com a API Whapi Cloud
"""

import requests
import json
import os
import sys

def obter_url_ngrok():
    """Obtém a URL do ngrok via API local"""
    try:
        response = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=2)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            if tunnels:
                # Priorizar HTTPS
                https_tunnel = next((t for t in tunnels if t.get('proto') == 'https'), None)
                http_tunnel = next((t for t in tunnels if t.get('proto') == 'http'), None)
                tunnel = https_tunnel or http_tunnel
                if tunnel:
                    public_url = tunnel.get('public_url', '').rstrip('/')
                    return public_url
    except Exception as e:
        print(f"❌ Erro ao obter URL do ngrok: {e}")
    return None

def testar_webhook(url_webhook):
    """Testa se o webhook está acessível"""
    try:
        print(f"\n🧪 Testando webhook: {url_webhook}")
        response = requests.get(url_webhook, timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print("   ✅ Webhook está respondendo!")
            return True
        else:
            print(f"   ⚠️ Webhook retornou status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Erro ao testar webhook: {e}")
        return False

def main():
    print("=" * 60)
    print("🔧 CONFIGURAÇÃO DO WEBHOOK NGROK - WHAPI CLOUD")
    print("=" * 60)
    
    # 1. Obter URL do ngrok
    print("\n1️⃣ Obtendo URL do ngrok...")
    ngrok_url = obter_url_ngrok()
    
    if not ngrok_url:
        print("❌ ngrok não está rodando ou não está acessível!")
        print("   Execute: ngrok http 8000")
        sys.exit(1)
    
    print(f"   ✅ URL do ngrok: {ngrok_url}")
    
    # 2. Montar URL completa do webhook
    webhook_path = "/app_igreja/api/whatsapp/webhook/"
    url_webhook_completa = f"{ngrok_url}{webhook_path}"
    
    print(f"\n2️⃣ URL completa do webhook:")
    print(f"   {url_webhook_completa}")
    
    # 3. Testar webhook
    print(f"\n3️⃣ Testando acessibilidade do webhook...")
    webhook_ok = testar_webhook(url_webhook_completa)
    
    # 4. Verificar CSRF_TRUSTED_ORIGINS
    print(f"\n4️⃣ Verificando configurações...")
    print(f"   ⚠️ IMPORTANTE: Certifique-se de que a URL do ngrok está em CSRF_TRUSTED_ORIGINS")
    print(f"   No arquivo pro_igreja/settings.py, adicione:")
    print(f"   '{ngrok_url}',")
    
    # 5. Instruções para configurar na API
    print(f"\n5️⃣ CONFIGURE NA API WHAPI CLOUD:")
    print(f"   📋 URL do Webhook:")
    print(f"   {url_webhook_completa}")
    print(f"\n   📋 Método: POST")
    print(f"   📋 Headers: Content-Type: application/json")
    
    # 6. Verificar se Django está rodando
    print(f"\n6️⃣ Verificando se Django está rodando...")
    try:
        response = requests.get(f"{ngrok_url}/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Django está acessível via ngrok!")
        else:
            print(f"   ⚠️ Django retornou status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Django não está acessível via ngrok: {e}")
        print(f"   Verifique se o servidor está rodando: python manage.py runserver 0.0.0.0:8000")
    
    # 7. Resumo
    print(f"\n" + "=" * 60)
    print("📋 RESUMO:")
    print("=" * 60)
    print(f"✅ URL do ngrok: {ngrok_url}")
    print(f"✅ URL do webhook: {url_webhook_completa}")
    print(f"✅ Status do webhook: {'OK' if webhook_ok else 'ERRO'}")
    print(f"\n⚠️  PRÓXIMOS PASSOS:")
    print(f"   1. Configure a URL acima no painel da Whapi Cloud")
    print(f"   2. Certifique-se de que CSRF_TRUSTED_ORIGINS inclui: '{ngrok_url}'")
    print(f"   3. Teste enviando uma mensagem para o WhatsApp")
    print("=" * 60)

if __name__ == "__main__":
    main()

