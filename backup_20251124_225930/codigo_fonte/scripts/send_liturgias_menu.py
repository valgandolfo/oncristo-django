#!/usr/bin/env python3
"""
Script utilitário para enviar, manualmente, o menu interativo (Sim/Não)
para um destinatário via Whapi Cloud.

Uso:
    export WHAPI_KEY="seu_token"
    export WHAPI_CHANNEL_ID="seu_channel_id"
    export WHAPI_BASE_URL="https://gate.whapi.cloud"  # opcional
    python scripts/send_liturgias_menu.py 5511999999999 https://seusite.com/app_igreja/liturgias/
"""
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv


def send_liturgias_menu(phone_number: str, liturgias_url: str) -> dict:
    # Carregar variáveis do .env (se houver)
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")
    load_dotenv(project_root / ".env_local")
    load_dotenv(project_root / ".env_production")

    base_url = os.getenv("WHAPI_BASE_URL", "https://gate.whapi.cloud").rstrip("/")
    api_key = os.getenv("WHAPI_KEY") or os.getenv("WHATSAPP_API_KEY")

    if not api_key:
        raise RuntimeError("A variável WHAPI_KEY ou WHATSAPP_API_KEY precisa estar definida.")

    payload = {
        "header": {"text": "Obrigado por interagir conosco."},
        "body": {"text": "Posso redirecioná-lo para nosso Site ?"},
        "footer": {"text": "Escolha sua Opção"},
        "action": {
            "buttons": [
                {
                    "type": "url",
                    "title": "Sim",
                    "id": "liturgias_sim",
                    "url": liturgias_url
                },
                {
                    "type": "url",
                    "title": "Não",
                    "id": "liturgias_nao",
                    "url": "#"  # URL temporária - será processado no webhook
                }
            ]
        },
        "type": "button",
        "to": phone_number
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
    }

    response = requests.post(
        f"{base_url}/messages/interactive",
        headers=headers,
        json=payload,
        timeout=30,
    )

    try:
        data = response.json()
    except ValueError:
        data = {"raw_response": response.text}

    if response.status_code != 200:
        raise RuntimeError(f"Erro {response.status_code}: {json.dumps(data, ensure_ascii=False)}")

    return data


def main() -> None:
    if len(sys.argv) == 3:
        phone = sys.argv[1]
        url = sys.argv[2]
    else:
        print("Informe os dados para enviar o menu interativo:")
        phone = input("Telefone destino (ex: 5511999999999): ").strip()
        url = input("URL da página de liturgias: ").strip()
        if not phone or not url:
            print("Telefone e URL são obrigatórios.")
            sys.exit(1)

    result = send_liturgias_menu(phone, url)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

