"""
==================== API WHATSAPP - CHATBOT ====================
API para receber webhooks do WhatsApp (Whapi Cloud) e processar comandos do chatbot
Integra com módulos existentes: Dizimistas, Liturgias, Celebrações, Orações, etc.
Baseado no app_chatbot.py (Flask) migrado para Django
"""

import os
import json
import logging
import time
import requests
from datetime import date, datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
from dotenv import load_dotenv

from ...models.area_admin.models_dizimistas import TBDIZIMISTAS
from ...models.area_publica.models_liturgias import TBLITURGIA
from ...models.area_admin.models_celebracoes import TBCELEBRACOES
from ...models.area_admin.models_oracoes import TBORACOES
from ...models.area_admin.models_paroquias import TBPAROQUIA
from ...models.area_admin.models_visual import TBVISUAL
from ...forms.area_publica.forms_dizimistas import DizimistaPublicoForm

logger = logging.getLogger(__name__)

# Nota: As variáveis de ambiente já são carregadas pelo Django settings.py
# que carrega automaticamente o .env_local em desenvolvimento
# Não precisamos chamar load_dotenv() novamente aqui

# Configuração da API Whapi Cloud
API_KEY = os.getenv('WHAPI_KEY', os.getenv('WHATSAPP_API_KEY', ''))
API_BASE_URL = os.getenv('WHATSAPP_BASE_URL', 'https://gate.whapi.cloud')
CHANNEL_ID = os.getenv('CHANNEL_ID', os.getenv('WHATSAPP_CHANNEL_ID', ''))

# Versão atual do webhook
CURRENT_VERSION = "v2.0.0-django"

# Set para armazenar IDs de mensagens já processadas (em produção, usar Redis ou DB)
processed_messages = set()

# Set para armazenar números que já receberam o menu (para detectar primeiro contato)
numbers_with_menu = set()


def limpar_telefone(telefone):
    """Remove caracteres não numéricos e o código do país (55) do número do telefone"""
    if not telefone:
        return telefone
    
    # Remove caracteres não numéricos
    import re
    telefone_limpo = re.sub(r'[^\d]', '', str(telefone))
    
    # Remove código do país (55) se existir
    if telefone_limpo and telefone_limpo.startswith('55'):
        telefone_limpo = telefone_limpo[2:]  # Remove os primeiros 2 dígitos (55)
    
    return telefone_limpo


def get_ngrok_url():
    """
    Tenta obter a URL do ngrok automaticamente via API local
    O ngrok expõe uma API em http://127.0.0.1:4040/api/tunnels
    """
    try:
        response = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=1)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            if tunnels:
                # Pega o primeiro túnel HTTPS (ou HTTP se não houver HTTPS)
                https_tunnel = next((t for t in tunnels if t.get('proto') == 'https'), None)
                http_tunnel = next((t for t in tunnels if t.get('proto') == 'http'), None)
                
                tunnel = https_tunnel or http_tunnel
                if tunnel:
                    public_url = tunnel.get('public_url', '').rstrip('/')
                    if public_url:
                        logger.info(f"🌐 URL do ngrok detectada automaticamente: {public_url}")
                        return public_url
    except (requests.exceptions.RequestException, Exception) as e:
        # ngrok não está rodando ou API não está acessível
        logger.debug(f"Ngrok API não acessível: {e}")
    return None


def get_site_url():
    """
    Obtém a URL do site para uso na API do WhatsApp
    Ordem de prioridade (para API externa, ngrok tem prioridade):
    1. URL do ngrok detectada automaticamente (se ngrok estiver rodando) - PRIORIDADE MÁXIMA
    2. NGROK_URL do .env (ex: https://xxxx.ngrok-free.app)
    3. SITE_URL do .env (ex: https://oncristo.com.br)
    4. SITE_URL_LOCAL do .env (ex: http://0.0.0.0:8000) - apenas se ngrok não estiver disponível
    5. URL padrão de produção
    """
    # 1. PRIORIDADE MÁXIMA: Tentar obter URL do ngrok automaticamente
    ngrok_url = get_ngrok_url()
    if ngrok_url:
        logger.info(f"✅ URL do ngrok detectada automaticamente: {ngrok_url}")
        return ngrok_url
    
    # 2. Tentar NGROK_URL do .env
    site_url = os.getenv('NGROK_URL')
    if site_url:
        site_url = site_url.rstrip('/')
        if not site_url.startswith('http://') and not site_url.startswith('https://'):
            site_url = f'https://{site_url}'
        logger.info(f"✅ URL do site configurada (NGROK_URL do .env): {site_url}")
        return site_url
    
    # 3. Tentar SITE_URL do .env (produção)
    site_url = os.getenv('SITE_URL')
    if site_url:
        site_url = site_url.rstrip('/')
        if not site_url.startswith('http://') and not site_url.startswith('https://'):
            site_url = f'https://{site_url}'
        logger.info(f"✅ URL do site configurada (SITE_URL do .env): {site_url}")
        return site_url
    
    # 4. SITE_URL_LOCAL do .env (apenas se ngrok não estiver disponível)
    site_url = os.getenv('SITE_URL_LOCAL')
    if site_url:
        site_url = site_url.rstrip('/')
        if not site_url.startswith('http://') and not site_url.startswith('https://'):
            site_url = f'http://{site_url}'
        logger.warning(f"⚠️ Usando SITE_URL_LOCAL (ngrok não detectado): {site_url}")
        return site_url
    
    # 5. URL padrão de produção
    site_url = 'https://oncristo.com.br'
    logger.warning(f"⚠️ Usando URL padrão: {site_url}")
    return site_url


def get_local_time():
    """Retorna o horário local formatado"""
    try:
        tz = timezone.get_current_timezone()
        return timezone.now().astimezone(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def send_whatsapp_message(phone, message):
    """Envia mensagem de texto via API Whapi Cloud"""
    try:
        url = f"{API_BASE_URL}/messages/text"
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {API_KEY}",
            "channel-id": CHANNEL_ID
        }
        
        message_data = {
            "to": phone,
            "body": message
        }
        
        logger.info(f"📱 Enviando mensagem para {phone}")
        logger.debug(f"Payload: {json.dumps(message_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, headers=headers, json=message_data, timeout=30)
        
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("sent", False) or result.get("success", False):
                message_id = result.get('message', {}).get('id', 'N/A')
                logger.info(f"✅ Mensagem enviada com sucesso para {phone}. ID: {message_id}")
                logger.debug(f"Resposta completa: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return result
            else:
                error_msg = f"Erro ao enviar: {result}"
                logger.error(f"❌ {error_msg}")
                logger.error(f"   Telefone: {phone}")
                logger.error(f"   Resposta completa: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return {"error": error_msg}
        else:
            error_msg = f"Erro {response.status_code}: {response.text}"
            logger.error(f"❌ {error_msg}")
            logger.error(f"   Telefone: {phone}")
            return {"error": error_msg}
            
    except Exception as e:
        logger.error(f"Erro de conexão ao enviar mensagem: {str(e)}")
        return {"error": f"Erro de conexão: {str(e)}"}


def get_imagem_capa_url(optimized=True):
    """
    Busca a URL da foto da capa (VIS_FOTO_CAPA) do projeto
    Retorna URL completa da imagem (deve ser acessível publicamente)
    
    Args:
        optimized: Se True, retorna URL do endpoint otimizado para WhatsApp (menor tamanho)
    
    Prioridade:
    1. Foto da capa configurada no TBVISUAL (VIS_FOTO_CAPA)
    2. Imagem principal (VIS_FOTO_PRINCIPAL) como fallback
    3. Imagem padrão (oncristo2.png)
    
    A URL é construída usando SITE_URL do .env ou padrão de produção
    Para WhatsApp, usa endpoint otimizado (800x800, qualidade 75) para economizar bytes
    """
    try:
        base_url = get_site_url()
        base_url = base_url.rstrip('/')
        
        # Tentar buscar foto da capa do banco
        visual = TBVISUAL.objects.first()
        if visual and visual.VIS_FOTO_CAPA:
            # Verificar se a URL já é completa (S3) ou relativa
            foto_url = visual.VIS_FOTO_CAPA.url
            if foto_url.startswith('http://') or foto_url.startswith('https://'):
                # URL completa (S3), usar diretamente
                image_url = foto_url
            else:
                # URL relativa, concatenar com base_url
                image_url = f"{base_url}{foto_url}"
            logger.info(f"✅ Foto da capa encontrada: {image_url}")
            return image_url
        elif visual and visual.VIS_FOTO_PRINCIPAL:
            # Fallback: usar imagem principal se não houver capa
            if optimized:
                image_url = f"{base_url}/app_igreja/api/whatsapp/imagem-principal/"
            else:
                # Verificar se a URL já é completa (S3) ou relativa
                foto_url = visual.VIS_FOTO_PRINCIPAL.url
                if foto_url.startswith('http://') or foto_url.startswith('https://'):
                    image_url = foto_url
                else:
                    image_url = f"{base_url}{foto_url}"
            logger.info(f"ℹ️  Usando imagem principal como fallback: {image_url}")
            return image_url
        else:
            # Usar imagem padrão se não houver nenhuma configurada
            default_image = f"{base_url}/static/img/oncristo2.png"
            logger.info(f"ℹ️  Usando imagem padrão: {default_image}")
            return default_image
    except Exception as e:
        logger.warning(f"⚠️  Erro ao buscar foto da capa: {str(e)}")
        # Fallback para imagem padrão
        base_url = get_site_url()
        base_url = base_url.rstrip('/')
        return f"{base_url}/static/img/oncristo2.png"


def get_imagem_principal_url(optimized=True):
    """
    Busca a URL da imagem principal do projeto
    Retorna URL completa da imagem (deve ser acessível publicamente)
    
    Args:
        optimized: Se True, retorna URL do endpoint otimizado para WhatsApp (menor tamanho)
    
    Prioridade:
    1. Imagem principal configurada no TBVISUAL
    2. Imagem padrão (oncristo2.png)
    
    A URL é construída usando SITE_URL do .env ou padrão de produção
    Para WhatsApp, usa endpoint otimizado (800x800, qualidade 75) para economizar bytes
    """
    try:
        base_url = get_site_url()
        base_url = base_url.rstrip('/')
        
        # Tentar buscar imagem principal do banco
        visual = TBVISUAL.objects.first()
        if visual and visual.VIS_FOTO_PRINCIPAL:
            if optimized:
                # Usar endpoint otimizado para WhatsApp (menor consumo de bytes)
                # O endpoint /api/whatsapp/imagem-principal/ serve a imagem otimizada
                image_url = f"{base_url}/app_igreja/api/whatsapp/imagem-principal/"
                logger.info(f"✅ Imagem principal otimizada para WhatsApp: {image_url}")
            else:
                # URL original da imagem
                image_url = f"{base_url}{visual.VIS_FOTO_PRINCIPAL.url}"
                logger.info(f"✅ Imagem principal encontrada: {image_url}")
            return image_url
        else:
            # Usar imagem padrão se não houver imagem principal configurada
            default_image = f"{base_url}/static/img/oncristo2.png"
            logger.info(f"ℹ️  Usando imagem padrão: {default_image}")
            return default_image
    except Exception as e:
        logger.warning(f"⚠️  Erro ao buscar imagem principal: {str(e)}")
        # Fallback para imagem padrão
        base_url = get_site_url()
        base_url = base_url.rstrip('/')
        return f"{base_url}/static/img/oncristo2.png"


def send_whatsapp_image(phone, image_url, caption=None):
    """
    Envia imagem via API Whapi Cloud
    
    Args:
        phone: Número do telefone destinatário
        image_url: URL da imagem (deve ser acessível publicamente)
        caption: Legenda opcional da imagem
    
    Formato da API Whapi Cloud:
    {
        "to": "5518997366866",
        "media": "https://url-da-imagem.com/image.jpg"
    }
    """
    try:
        url = f"{API_BASE_URL}/messages/image"
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {API_KEY}",
            "channel-id": CHANNEL_ID
        }
        
        # Formato correto da API Whapi Cloud
        message_data = {
            "to": phone,
            "media": image_url  # URL direta da imagem
        }
        
        # Adicionar caption se fornecido (algumas APIs suportam)
        if caption:
            message_data["caption"] = caption
        
        logger.info(f"📸 Enviando imagem para {phone}: {image_url}")
        logger.debug(f"Payload: {json.dumps(message_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, headers=headers, json=message_data, timeout=30)
        
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("sent", False) or result.get("success", False):
                message_id = result.get('message', {}).get('id', 'N/A')
                logger.info(f"✅ Imagem enviada com sucesso para {phone}. ID: {message_id}")
                logger.debug(f"Resposta completa: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return result
            else:
                error_msg = f"Erro ao enviar imagem: {result}"
                logger.error(f"❌ {error_msg}")
                logger.error(f"   Telefone: {phone}")
                logger.error(f"   Resposta completa: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return {"error": error_msg}
        else:
            error_msg = f"Erro {response.status_code}: {response.text}"
            logger.error(f"❌ {error_msg}")
            logger.error(f"   Telefone: {phone}")
            return {"error": error_msg}
            
    except Exception as e:
        logger.error(f"❌ Erro de conexão ao enviar imagem: {str(e)}", exc_info=True)
        return {"error": f"Erro de conexão: {str(e)}"}


def reject_whatsapp_call(phone, call_id=None):
    """
    Rejeita chamada de voz recebida via API Whapi Cloud
    
    Nota: A API Whapi Cloud pode não ter endpoint específico para rejeitar chamadas.
    Neste caso, a chamada será apenas ignorada e logada.
    """
    try:
        logger.warning(f"📞 CHAMADA RECUSADA - De: {phone} | ID: {call_id} | Horário: {get_local_time()}")
        
        # Tentar usar endpoint de chamadas se disponível (pode não existir na Whapi Cloud)
        url = f"{API_BASE_URL}/calls/reject"
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {API_KEY}",
            "channel-id": CHANNEL_ID
        }
        
        call_data = {
            "to": phone,
        }
        
        if call_id:
            call_data["call_id"] = call_id
        
        response = requests.post(url, headers=headers, json=call_data, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"✅ Chamada rejeitada via API para {phone}")
            return {"success": True, "message": "Chamada rejeitada"}
        elif response.status_code == 404:
            # Endpoint não existe - apenas ignorar (comportamento esperado)
            logger.info(f"ℹ️  Endpoint de rejeição não disponível - Chamada será ignorada automaticamente para {phone}")
            return {"success": True, "message": "Chamada ignorada (endpoint não disponível)"}
        else:
            # Outro erro - logar mas não falhar
            logger.warning(f"⚠️  Erro ao rejeitar chamada ({response.status_code}): {response.text}")
            return {"success": True, "message": "Chamada ignorada"}
            
    except requests.exceptions.RequestException as e:
        # Se der erro de conexão, apenas logar (não é crítico - a chamada será ignorada mesmo)
        logger.info(f"ℹ️  Chamada de {phone} será ignorada (erro de conexão na API: {str(e)})")
        return {"success": True, "message": "Chamada ignorada"}
    except Exception as e:
        logger.warning(f"⚠️  Erro ao processar rejeição de chamada: {str(e)}")
        return {"success": True, "message": "Chamada ignorada"}


def get_nome_paroquia():
    """
    Busca o nome da paróquia cadastrada
    Retorna o nome da paróquia ou "Paróquia" como padrão
    """
    try:
        paroquia = TBPAROQUIA.objects.first()
        if paroquia and paroquia.PAR_nome_paroquia:
            return paroquia.PAR_nome_paroquia.strip()
        return "Paróquia"
    except Exception as e:
        logger.warning(f"⚠️  Erro ao buscar nome da paróquia: {str(e)}")
        return "Paróquia"


def send_whatsapp_menu(phone, send_image_first=True, use_capa=False):
    """
    Envia menu interativo via API Whapi Cloud
    Opcionalmente envia a imagem antes do menu
    
    Args:
        phone: Número do telefone destinatário
        send_image_first: Se True, envia imagem antes do menu
        use_capa: Se True, usa a foto da capa (VIS_FOTO_CAPA), senão usa imagem principal
    """
    try:
        # Buscar nome da paróquia para o cabeçalho
        nome_paroquia = get_nome_paroquia()
        header_text = f"Bem vindo a Paroquia {nome_paroquia} - Menu Principal"
        
        # Primeiro, enviar a imagem se solicitado
        if send_image_first:
            # Se use_capa=True, usar foto da capa, senão usar imagem principal
            if use_capa:
                image_url = get_imagem_capa_url(optimized=False)  # Foto da capa usa URL direta
                logger.info(f"📸 Preparando para enviar FOTO DA CAPA antes do menu para {phone}")
            else:
                image_url = get_imagem_principal_url(optimized=True)
                logger.info(f"📸 Preparando para enviar imagem principal antes do menu para {phone}")
            
            if image_url:
                logger.info(f"📸 URL da imagem: {image_url}")
                
                # Verificar se a URL é acessível (teste rápido)
                try:
                    test_response = requests.head(image_url, timeout=5, allow_redirects=True)
                    if test_response.status_code == 200:
                        logger.info(f"✅ URL da imagem é acessível (Status: {test_response.status_code})")
                    else:
                        logger.warning(f"⚠️  URL da imagem retornou status {test_response.status_code}")
                except Exception as e:
                    logger.warning(f"⚠️  Não foi possível verificar acessibilidade da URL: {str(e)}")
                
                image_result = send_whatsapp_image(
                    phone, 
                    image_url, 
                    caption="📖 Projeto On Cristo - Sua paróquia sempre com você"
                )
                # Não falhar se a imagem não for enviada, apenas logar
                if image_result.get("error"):
                    logger.warning(f"⚠️  Erro ao enviar imagem, mas continuando com menu: {image_result.get('error')}")
                else:
                    logger.info(f"✅ Imagem enviada com sucesso, aguardando antes de enviar menu...")
                    # Aguardar um pouco para a imagem ser processada antes de enviar o menu
                    time.sleep(1.5)
            else:
                logger.warning(f"⚠️  URL da imagem não encontrada, pulando envio de imagem")
        
        # Agora enviar o menu interativo
        url = f"{API_BASE_URL}/messages/interactive"
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {API_KEY}",
            "channel-id": CHANNEL_ID
        }
        
        message_data = {
            "to": phone,
            "type": "list",
            "header": {"text": header_text},
            "body": {"text": "Escolha uma opção para continuar:"},
            "footer": {"text": "Sua paróquia sempre com você"},
            "action": {
                "list": {
                    "label": "Menu Principal",
                    "sections": [
                        {
                            "title": "Opções Disponíveis",
                            "rows": [
                                {
                                    "title": "📖 Liturgias",
                                    "id": "liturgias",
                                    "description": "Selecione a liturgia do dia desejado"
                                },
                                {
                                    "title": "👥 Quero ser Colaborador",
                                    "id": "cadastro_membro",
                                    "description": "Cadastro de colaborador para celebração das missas e eventos"                                },
                                {
                                    "title": "⏰ Escalas de Missas",
                                    "id": "Escala_Missas",
                                    "description": "Para Colaboradores cadastrados escalar celebrações como colaborador"
                                },
                                {
                                    "title": "💰 Dízimo, ofertas e donativos",
                                    "id": "dizimo_ofertas",
                                    "description": "Veja como ajudar em nosso trabalho de evangelização"
                                },
                                {
                                    "title": "🕯️ Agendar Celebrações",
                                    "id": "Agendar_Celebracoes",
                                    "description": "Missa de 7º dia, agradecimentos, Louvor, etc."
                                },
                                {
                                    "title": "🙏 Pedido de Oração",
                                    "id": "pedido_oracao",
                                    "description": "Orações, agradecimentos, Louvores..."
                                }
                            ]
                        }
                    ]
                }
            }
        }
        
        logger.info(f"Enviando menu para {phone}")
        
        response = requests.post(url, headers=headers, json=message_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("sent", False):
                logger.info(f"Menu enviado com sucesso. ID: {result.get('message', {}).get('id')}")
                return result
            else:
                logger.error(f"Erro ao enviar menu: {result}")
                return {"error": f"Erro ao enviar menu: {result}"}
        else:
            logger.error(f"Erro ao enviar menu: {response.status_code} - {response.text}")
            return {"error": f"Erro {response.status_code}: {response.text}"}
            
    except Exception as e:
        logger.error(f"Erro de conexão ao enviar menu: {str(e)}")
        return {"error": f"Erro de conexão: {str(e)}"}


def get_liturgia_por_data(data_lit):
    """Busca liturgia por data usando Django ORM"""
    try:
        liturgias = TBLITURGIA.objects.filter(
            LIT_DATALIT=data_lit,
            LIT_STATUSLIT=True
        ).order_by(
            'LIT_TIPOLIT'  # Ordenar por tipo (Primeira Leitura, Salmo, etc.)
        )
        
        if not liturgias.exists():
            return None
        
        liturgia_dict = {
            'data': data_lit.strftime('%d/%m/%Y'),
            'leituras': {}
        }
        
        for lit in liturgias:
            liturgia_dict['leituras'][lit.LIT_TIPOLIT] = lit.LIT_TEXTO
        
        return liturgia_dict
        
    except Exception as e:
        logger.error(f"Erro ao buscar liturgia: {e}")
        return None


def get_liturgia_hoje():
    """Busca liturgia do dia atual"""
    return get_liturgia_por_data(date.today())


def send_whatsapp_menu_liturgias(phone):
    """
    Envia menu interativo com botões para liturgias
    Pergunta se o usuário quer ser redirecionado para o site
    """
    try:
        url = f"{API_BASE_URL}/messages/interactive"
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {API_KEY}",
            "channel-id": CHANNEL_ID
        }
        
        site_url = get_site_url()
        liturgias_url = f"{site_url}/app_igreja/liturgias/"
        logger.info(f"🔗 Link de liturgias gerado: {liturgias_url}")
        
        # Payload oficial da Whapi para mensagens interativas (type: button)
        # Formato baseado no exemplo que funciona na API
        message_data = {
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
                        "url": "#"  # URL temporária - será processado no webhook quando clicar em "Não"
                    }
                ]
            },
            "type": "button",
            "to": phone
        }
        
        logger.info(f"📖 Enviando menu de liturgias para {phone}")
        logger.debug(f"Payload: {json.dumps(message_data, indent=2)}")
        
        response = requests.post(url, headers=headers, json=message_data, timeout=30)
        
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("sent", False) or result.get("success", False):
                logger.info(f"✅ Menu de liturgias enviado com sucesso. ID: {result.get('message', {}).get('id', 'N/A')}")
                return result
            else:
                logger.error(f"❌ Erro ao enviar menu de liturgias: {result}")
                return {"error": f"Erro ao enviar: {result}"}
        else:
            logger.error(f"❌ Erro ao enviar menu de liturgias: {response.status_code} - {response.text}")
            return {"error": f"Erro {response.status_code}: {response.text}"}
            
    except Exception as e:
        logger.error(f"❌ Erro de conexão ao enviar menu de liturgias: {str(e)}", exc_info=True)
        return {"error": f"Erro de conexão: {str(e)}"}


def send_whatsapp_menu_dizimista(phone):
    """
    Envia menu interativo com botões para cadastro de dizimista
    Pergunta se o usuário quer ser redirecionado para o site de cadastro
    """
    try:
        url = f"{API_BASE_URL}/messages/interactive"
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {API_KEY}",
            "channel-id": CHANNEL_ID
        }
        
        # Obter URL do site (prioriza local/ngrok)
        site_url = get_site_url()
        
        # Limpar telefone para URL (remover código do país se existir)
        telefone_limpo = limpar_telefone(phone)
        if telefone_limpo and telefone_limpo.startswith('55'):
            telefone_limpo = telefone_limpo[2:]
        
        dizimista_url = f"{site_url}/app_igreja/quero-ser-dizimista/?telefone={telefone_limpo}"
        
        logger.info(f"🌐 URL do dizimista: {dizimista_url}")
        
        # Payload oficial da Whapi para mensagens interativas (type: button)
        message_data = {
            "header": {"text": "Obrigado por interagir conosco."},
            "body": {"text": "Posso redirecioná-lo para nosso Site de Cadastro ?"},
            "footer": {"text": "Escolha sua Opção"},
            "action": {
                "buttons": [
                    {
                        "type": "url",
                        "title": "Sim",
                        "id": "dizimista_sim",
                        "url": dizimista_url
                    },
                    {
                        "type": "url",
                        "title": "Não",
                        "id": "dizimista_nao",
                        "url": "#"  # URL temporária - será processado no webhook quando clicar em "Não"
                    }
                ]
            },
            "type": "button",
            "to": phone
        }
        
        logger.info(f"💰 Enviando menu de dizimista para {phone}")
        logger.debug(f"Payload: {json.dumps(message_data, indent=2)}")
        
        response = requests.post(url, headers=headers, json=message_data, timeout=30)
        
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("sent", False) or result.get("success", False):
                logger.info(f"✅ Menu de dizimista enviado com sucesso. ID: {result.get('message', {}).get('id', 'N/A')}")
                return result
            else:
                logger.error(f"❌ Erro ao enviar menu de dizimista: {result}")
                return {"error": f"Erro ao enviar: {result}"}
        else:
            logger.error(f"❌ Erro ao enviar menu de dizimista: {response.status_code} - {response.text}")
            return {"error": f"Erro {response.status_code}: {response.text}"}
            
    except Exception as e:
        logger.error(f"❌ Erro de conexão ao enviar menu de dizimista: {str(e)}", exc_info=True)
        return {"error": f"Erro de conexão: {str(e)}"}


def send_whatsapp_menu_colaborador(phone):
    """
    Envia menu interativo com botões para cadastro de colaborador
    Pergunta se o usuário quer ser redirecionado para o site de cadastro
    """
    try:
        url = f"{API_BASE_URL}/messages/interactive"
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {API_KEY}",
            "channel-id": CHANNEL_ID
        }
        
        # Obter URL do site (prioriza local/ngrok)
        site_url = get_site_url()
        
        # Limpar telefone para URL (remover código do país se existir)
        telefone_limpo = limpar_telefone(phone)
        if telefone_limpo and telefone_limpo.startswith('55'):
            telefone_limpo = telefone_limpo[2:]
        
        colaborador_url = f"{site_url}/app_igreja/quero-ser-colaborador/?telefone={telefone_limpo}"
        
        logger.info(f"🌐 URL do colaborador: {colaborador_url}")
        
        # Payload oficial da Whapi para mensagens interativas (type: button)
        message_data = {
            "header": {"text": "Obrigado por interagir conosco."},
            "body": {"text": "Posso redirecioná-lo para nosso Site de Cadastro de Colaborador ?"},
            "footer": {"text": "Escolha sua Opção"},
            "action": {
                "buttons": [
                    {
                        "type": "url",
                        "title": "Sim",
                        "id": "colaborador_sim",
                        "url": colaborador_url
                    },
                    {
                        "type": "url",
                        "title": "Não",
                        "id": "colaborador_nao",
                        "url": "#"  # URL temporária - será processado no webhook quando clicar em "Não"
                    }
                ]
            },
            "type": "button",
            "to": phone
        }
        
        logger.info(f"👥 Enviando menu de colaborador para {phone}")
        logger.debug(f"Payload: {json.dumps(message_data, indent=2)}")
        
        response = requests.post(url, headers=headers, json=message_data, timeout=30)
        
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("sent", False) or result.get("success", False):
                logger.info(f"✅ Menu de colaborador enviado com sucesso. ID: {result.get('message', {}).get('id', 'N/A')}")
                return result
            else:
                logger.error(f"❌ Erro ao enviar menu de colaborador: {result}")
                return {"error": f"Erro ao enviar: {result}"}
        else:
            logger.error(f"❌ Erro ao enviar menu de colaborador: {response.status_code} - {response.text}")
            return {"error": f"Erro {response.status_code}: {response.text}"}
            
    except Exception as e:
        logger.error(f"❌ Erro de conexão ao enviar menu de colaborador: {str(e)}", exc_info=True)
        return {"error": f"Erro de conexão: {str(e)}"}


def send_whatsapp_menu_escalas(phone):
    """
    Envia menu interativo com botões para escalas de missas
    Pergunta se o usuário quer ser redirecionado para o site
    """
    try:
        url = f"{API_BASE_URL}/messages/interactive"
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {API_KEY}",
            "channel-id": CHANNEL_ID
        }
        
        site_url = get_site_url()
        
        # Formatar telefone para URL (remover código do país se necessário)
        telefone_limpo = limpar_telefone(phone)
        telefone_url = telefone_limpo.replace(' ', '').replace('(', '').replace(')', '').replace('-', '')
        escalas_url = f"{site_url}/app_igreja/escala-missas/?telefone={telefone_url}"
        
        logger.info(f"🌐 URL das escalas: {escalas_url}")
        
        # Payload oficial da Whapi para mensagens interativas (type: button)
        message_data = {
            "header": {"text": "Obrigado por interagir conosco."},
            "body": {"text": "Posso redirecioná-lo para nosso Site para ver as Escalas de Missas?"},
            "footer": {"text": "Escolha sua Opção"},
            "action": {
                "buttons": [
                    {
                        "type": "url",
                        "title": "Sim",
                        "id": "escalas_sim",
                        "url": escalas_url
                    },
                    {
                        "type": "url",
                        "title": "Não",
                        "id": "escalas_nao",
                        "url": "#"
                    }
                ]
            },
            "type": "button",
            "to": phone
        }
        
        response = requests.post(url, headers=headers, json=message_data, timeout=30)
        
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("sent", False) or result.get("success", False):
                logger.info(f"✅ Menu de escalas enviado com sucesso. ID: {result.get('message', {}).get('id', 'N/A')}")
                return result
            else:
                logger.error(f"❌ Erro ao enviar menu de escalas: {result}")
                return {"error": f"Erro ao enviar: {result}"}
        else:
            logger.error(f"❌ Erro ao enviar menu de escalas: {response.status_code} - {response.text}")
            return {"error": f"Erro {response.status_code}: {response.text}"}
            
    except Exception as e:
        logger.error(f"❌ Erro de conexão ao enviar menu de escalas: {str(e)}", exc_info=True)
        return {"error": f"Erro de conexão: {str(e)}"}


def send_whatsapp_menu_agendar_celebracao(phone):
    """
    Envia menu interativo com botões para agendar celebrações
    Pergunta se o usuário quer ser redirecionado para o site
    """
    try:
        url = f"{API_BASE_URL}/messages/interactive"
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {API_KEY}",
            "channel-id": CHANNEL_ID
        }
        
        site_url = get_site_url()
        
        # Limpar telefone para URL (remover código do país se existir)
        telefone_limpo = limpar_telefone(phone)
        if telefone_limpo and telefone_limpo.startswith('55'):
            telefone_limpo = telefone_limpo[2:]
        
        agendar_url = f"{site_url}/app_igreja/agendar-celebracao/?telefone={telefone_limpo}"
        
        logger.info(f"🌐 URL de agendamento: {agendar_url}")
        
        # Payload oficial da Whapi para mensagens interativas (type: button)
        message_data = {
            "header": {"text": "Obrigado por interagir conosco."},
            "body": {"text": "Posso redirecioná-lo para nosso Site para Agendar uma Celebração?"},
            "footer": {"text": "Escolha sua Opção"},
            "action": {
                "buttons": [
                    {
                        "type": "url",
                        "title": "Sim",
                        "id": "agendar_sim",
                        "url": agendar_url
                    },
                    {
                        "type": "url",
                        "title": "Não",
                        "id": "agendar_nao",
                        "url": "#"
                    }
                ]
            },
            "type": "button",
            "to": phone
        }
        
        response = requests.post(url, headers=headers, json=message_data, timeout=30)
        
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("sent", False) or result.get("success", False):
                logger.info(f"✅ Menu de agendar celebração enviado com sucesso. ID: {result.get('message', {}).get('id', 'N/A')}")
                return result
            else:
                logger.error(f"❌ Erro ao enviar menu de agendar celebração: {result}")
                return {"error": f"Erro ao enviar: {result}"}
        else:
            logger.error(f"❌ Erro ao enviar menu de agendar celebração: {response.status_code} - {response.text}")
            return {"error": f"Erro {response.status_code}: {response.text}"}
            
    except Exception as e:
        logger.error(f"❌ Erro de conexão ao enviar menu de agendar celebração: {str(e)}", exc_info=True)
        return {"error": f"Erro de conexão: {str(e)}"}


def send_whatsapp_menu_oracoes(phone):
    """
    Envia menu interativo com botões para pedido de oração
    Redireciona diretamente para a página de novo pedido
    """
    try:
        url = f"{API_BASE_URL}/messages/interactive"
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {API_KEY}",
            "channel-id": CHANNEL_ID
        }
        
        # Obter URL do site (prioriza local/ngrok)
        site_url = get_site_url()
        
        # Limpar telefone para URL (remover código do país se existir)
        telefone_limpo = limpar_telefone(phone)
        if telefone_limpo and telefone_limpo.startswith('55'):
            telefone_limpo = telefone_limpo[2:]
        
        # URL direta para criar novo pedido de oração com telefone
        oracoes_url = f"{site_url}/app_igreja/meus-pedidos-oracoes/novo/?telefone={telefone_limpo}"
        
        logger.info(f"🙏 URL do pedido de oração: {oracoes_url}")
        
        # Payload oficial da Whapi para mensagens interativas (type: button)
        message_data = {
            "header": {"text": "Obrigado por interagir conosco."},
            "body": {"text": "Posso redirecioná-lo para nosso Site de Pedidos de Oração ?"},
            "footer": {"text": "Escolha sua Opção"},
            "action": {
                "buttons": [
                    {
                        "type": "url",
                        "title": "Sim",
                        "id": "oracoes_sim",
                        "url": oracoes_url
                    },
                    {
                        "type": "url",
                        "title": "Não",
                        "id": "oracoes_nao",
                        "url": "#"  # URL temporária - será processado no webhook quando clicar em "Não"
                    }
                ]
            },
            "type": "button",
            "to": phone
        }
        
        logger.info(f"🙏 Enviando menu de orações para {phone}")
        logger.debug(f"Payload: {json.dumps(message_data, indent=2)}")
        
        response = requests.post(url, headers=headers, json=message_data, timeout=30)
        
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("sent", False) or result.get("success", False):
                logger.info(f"✅ Menu de orações enviado com sucesso. ID: {result.get('message', {}).get('id', 'N/A')}")
                return result
            else:
                logger.error(f"❌ Erro ao enviar menu de orações: {result}")
                return {"error": f"Erro ao enviar: {result}"}
        else:
            logger.error(f"❌ Erro ao enviar menu de orações: {response.status_code} - {response.text}")
            return {"error": f"Erro {response.status_code}: {response.text}"}
            
    except Exception as e:
        logger.error(f"❌ Erro de conexão ao enviar menu de orações: {str(e)}", exc_info=True)
        return {"error": f"Erro de conexão: {str(e)}"}


def processar_botao_menu(button_id, sender_number):
    """
    Processa cliques em botões do menu interativo
    """
    logger.info(f"🔘 Processando botão: {button_id} de {sender_number}")
    
    if button_id == "liturgias_nao":
        # Usuário escolheu "Não" no menu de liturgias
        return send_whatsapp_message(
            sender_number,
            "📖 **LITURGIAS**\n\n"
            "Entendido! Se precisar acessar as liturgias depois, é só digitar qualquer mensagem para ver o menu novamente.\n\n"
            "Ou acesse diretamente:\n"
            "https://oncristo.com.br/app_igreja/liturgias/"
        )
    
    elif button_id == "dizimista_nao":
        # Usuário escolheu "Não" no menu de dizimista
        site_url = get_site_url()
        url_cadastro = f"{site_url}/app_igreja/quero-ser-dizimista/"
        return send_whatsapp_message(
            sender_number,
            "💰 **CADASTRO DE DIZIMISTA**\n\n"
            "Entendido! Se precisar se cadastrar depois, é só digitar qualquer mensagem para ver o menu novamente.\n\n"
            f"Ou acesse diretamente:\n{url_cadastro}"
        )
    
    elif button_id == "colaborador_nao":
        # Usuário escolheu "Não" no menu de colaborador
        site_url = get_site_url()
        url_cadastro = f"{site_url}/app_igreja/quero-ser-colaborador/"
        return send_whatsapp_message(
            sender_number,
            "👥 **CADASTRO DE COLABORADOR**\n\n"
            "Entendido! Se precisar se cadastrar depois, é só digitar qualquer mensagem para ver o menu novamente.\n\n"
            f"Ou acesse diretamente:\n{url_cadastro}"
        )
    
    elif button_id == "escalas_nao":
        # Usuário escolheu "Não" no menu de escalas
        site_url = get_site_url()
        url_escalas = f"{site_url}/app_igreja/escala-missas/"
        return send_whatsapp_message(
            sender_number,
            "⏰ **ESCALAS DE MISSAS**\n\n"
            "Entendido! Se precisar acessar as escalas depois, é só digitar qualquer mensagem para ver o menu novamente.\n\n"
            f"Ou acesse diretamente:\n{url_escalas}"
        )
    
    elif button_id == "agendar_nao":
        # Usuário escolheu "Não" no menu de agendar celebração
        site_url = get_site_url()
        url_agendar = f"{site_url}/app_igreja/agendar-celebracao/"
        return send_whatsapp_message(
            sender_number,
            "🕯️ **AGENDAR CELEBRAÇÕES**\n\n"
            "Entendido! Se precisar agendar depois, é só digitar qualquer mensagem para ver o menu novamente.\n\n"
            f"Ou acesse diretamente:\n{url_agendar}"
        )
    
    elif button_id == "oracoes_nao":
        # Usuário escolheu "Não" no menu de orações
        site_url = get_site_url()
        url_oracoes = f"{site_url}/app_igreja/meus-pedidos-oracoes/novo/"
        return send_whatsapp_message(
            sender_number,
            "🙏 **PEDIDO DE ORAÇÃO**\n\n"
            "Entendido! Se precisar fazer um pedido depois, é só digitar qualquer mensagem para ver o menu novamente.\n\n"
            f"Ou acesse diretamente:\n{url_oracoes}"
        )
    
    # Se não for um botão conhecido, retornar menu principal
    logger.warning(f"⚠️  Botão desconhecido: {button_id}")
    return send_whatsapp_menu(sender_number, send_image_first=False)


def processar_item_menu(item_id, item_title, sender_number):
    """Processa item selecionado do menu interativo"""
    telefone_limpo = limpar_telefone(sender_number)
    item_title_lower = (item_title or '').lower().strip()
    
    logger.info(f"🔍 Processando item do menu - ID: {item_id}, Título: {item_title}, De: {sender_number}")
    
    # Processar por título (mais confiável)
    if item_title:
        if "liturgias" in item_title_lower or "opcao 1" in item_title_lower:
            logger.info(f"📖 Liturgias detectado por título - Enviando menu de botões...")
            # Enviar menu interativo com botões (Sim/Não)
            return send_whatsapp_menu_liturgias(sender_number)
        
        elif "membro" in item_title_lower or "colaborador" in item_title_lower or "opcao 2" in item_title_lower:
            logger.info(f"👥 Colaborador detectado por título - Enviando menu de botões...")
            # Enviar menu interativo com botões (Sim/Não)
            return send_whatsapp_menu_colaborador(sender_number)
        
        elif "escalas" in item_title_lower or "opcao 3" in item_title_lower:
            # Enviar menu interativo com botões (Sim/Não) para escalas
            logger.info(f"⏰ Escalas detectado por título - Enviando menu de botões...")
            return send_whatsapp_menu_escalas(sender_number)
        
        elif "dizimo" in item_title_lower or "dízimo" in item_title_lower or "opcao 4" in item_title_lower:
            # Cadastro de dizimista - enviar menu interativo
            logger.info(f"💰 Dizimista detectado por título - Enviando menu de botões...")
            return send_whatsapp_menu_dizimista(sender_number)
        
        elif "agendar" in item_title_lower or "opcao 5" in item_title_lower:
            # Enviar menu interativo com botões (Sim/Não) para agendar celebrações
            logger.info(f"🕯️ Agendar Celebrações detectado por título - Enviando menu de botões...")
            return send_whatsapp_menu_agendar_celebracao(sender_number)
        
        elif "oracao" in item_title_lower or "oração" in item_title_lower or "pedido" in item_title_lower or "opcao 6" in item_title_lower:
            # Enviar menu interativo com botões (Sim/Não) para pedido de oração
            logger.info(f"🙏 Pedido de Oração detectado por título - Enviando menu de botões...")
            return send_whatsapp_menu_oracoes(sender_number)
    
    # Processar por ID (fallback)
    if item_id == "liturgias":
        logger.info(f"📖 Liturgias detectado por ID - Enviando menu de botões...")
        # Enviar menu interativo com botões (Sim/Não)
        return send_whatsapp_menu_liturgias(sender_number)
    
    elif item_id == "dizimo_ofertas":
        # Cadastro de dizimista - enviar menu interativo
        logger.info(f"💰 Dizimista detectado por ID - Enviando menu de botões...")
        return send_whatsapp_menu_dizimista(sender_number)
    
    elif item_id == "Agendar_Celebracoes":
        # Enviar menu interativo com botões (Sim/Não) para agendar celebrações
        logger.info(f"🕯️ Agendar Celebrações detectado por ID - Enviando menu de botões...")
        return send_whatsapp_menu_agendar_celebracao(sender_number)
    
    elif item_id == "pedido_oracao":
        # Enviar menu interativo com botões (Sim/Não) para pedido de oração
        logger.info(f"🙏 Pedido de Oração detectado por ID - Enviando menu de botões...")
        return send_whatsapp_menu_oracoes(sender_number)
    
    # Opção não reconhecida
    return send_whatsapp_message(
        sender_number,
        "Opção não reconhecida. Digite qualquer coisa para ver o menu novamente."
    )


@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "PATCH", "DELETE"])
def whatsapp_webhook(request):
    """
    Webhook para receber mensagens do WhatsApp (Whapi Cloud)
    Compatível com o formato do app_chatbot.py (Flask)
    """
    try:
        logger.info(f"Webhook recebido - Método: {request.method}")
        logger.info(f"Headers: {dict(request.headers)}")
        
        if request.method == 'GET':
            # Verificação do webhook (algumas APIs requerem)
            verify_token = request.GET.get('verify_token') or request.GET.get('hub.verify_token')
            challenge = request.GET.get('challenge') or request.GET.get('hub.challenge')
            mode = request.GET.get('hub.mode')
            
            if mode == 'subscribe' and verify_token:
                logger.info("Webhook verificado com sucesso!")
                return JsonResponse(int(challenge) if challenge else {}, safe=False)
            
            return JsonResponse({'status': 'webhook_ready', 'version': CURRENT_VERSION})
        
        # Processar mensagem POST
        try:
            data = json.loads(request.body.decode('utf-8')) if request.body else {}
        except:
            data = {}
        
        logger.info(f"Dados recebidos: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # Se não houver dados, retornar sucesso (pode ser verificação)
        if not data:
            logger.info("Webhook recebido sem dados (pode ser verificação)")
            return JsonResponse({
                "status": "success",
                "message": "Webhook recebido",
                "version": CURRENT_VERSION
            }, status=200)
        
        # Processar formato "messages" (formato padrão Whapi Cloud)
        if data.get("messages") and data.get("event", {}).get("type") == "messages":
            for message in data.get("messages", []):
                # Verificar se é mensagem recebida (não enviada por nós)
                if message.get("from_me", True):
                    logger.info("Mensagem enviada por nós, ignorando...")
                    continue
                
                # Verificar se já foi processada
                message_id = message.get("id")
                if message_id and message_id in processed_messages:
                    logger.info(f"Mensagem {message_id} já foi processada, ignorando...")
                    continue
                
                # Extrair telefone de várias formas possíveis (ANTES de verificar tipo)
                sender_number = (
                    message.get("from") or 
                    message.get("chat_id") or 
                    message.get("wa_id") or
                    message.get("sender") or
                    data.get("from")
                )
                
                # Verificar tipo de mensagem
                message_type = message.get("type")
                
                # Rejeitar chamadas automaticamente (ptt é áudio, não chamada)
                if message_type in ["call", "audio_call", "video_call"]:
                    logger.info(f"Chamada detectada de {sender_number} - Tipo: {message_type} - Rejeitando automaticamente...")
                    call_id = message.get("id") or message.get("call_id")
                    if sender_number:
                        reject_whatsapp_call(sender_number, call_id)
                    # Adicionar ao conjunto de processadas para não processar novamente
                    if message_id:
                        processed_messages.add(message_id)
                    continue
                
                if message_type == "unknown":
                    logger.info("Mensagem tipo unknown, ignorando...")
                    continue
                
                # Adicionar ao conjunto de processadas
                if message_id:
                    processed_messages.add(message_id)
                
                chat_name = message.get("chat_name", "") or message.get("from_name", "")
                
                logger.info(f"Processando mensagem - Tipo: {message_type}, De: {sender_number}, ID: {message_id}")
                
                if not sender_number:
                    logger.warning(f"Telefone não encontrado na mensagem: {json.dumps(message, indent=2)}")
                    # Tentar enviar menu mesmo sem telefone (pode estar em outro lugar)
                    continue
                
                try:
                    # Processar mensagens de texto
                    if message_type == "text":
                        # Extrair texto de várias formas
                        text_data = message.get("text", {})
                        if isinstance(text_data, dict):
                            message_text = text_data.get("body", "")
                        else:
                            message_text = str(text_data) if text_data else ""
                        
                        message_text = message_text.lower().strip() if message_text else ""
                        logger.info(f"Processando mensagem de texto: '{message_text[:50]}...' para {sender_number}")
                        
                        # Verificar se é o primeiro contato (enviar foto da capa)
                        is_first_contact = sender_number not in numbers_with_menu
                        if is_first_contact:
                            logger.info(f"🎉 Primeiro contato detectado para {sender_number} - Enviando foto da capa")
                            numbers_with_menu.add(sender_number)
                            # Enviar menu com foto da capa no primeiro contato
                            result = send_whatsapp_menu(sender_number, send_image_first=True, use_capa=True)
                        else:
                            # Contatos subsequentes: enviar menu sem imagem
                            result = send_whatsapp_menu(sender_number, send_image_first=False)
                    
                    # Processar mídias (áudio, imagem, vídeo) - enviar menu automaticamente
                    elif message_type in ["audio", "voice", "ptt", "image", "video", "document", "sticker"]:
                        logger.info(f"📎 Mídia recebida - Tipo: {message_type} de {sender_number} - Enviando menu automaticamente...")
                        
                        # Verificar se é o primeiro contato (enviar foto da capa)
                        is_first_contact = sender_number not in numbers_with_menu
                        if is_first_contact:
                            logger.info(f"🎉 Primeiro contato detectado para {sender_number} - Enviando foto da capa")
                            numbers_with_menu.add(sender_number)
                            # Enviar menu com foto da capa no primeiro contato
                            result = send_whatsapp_menu(sender_number, send_image_first=True, use_capa=True)
                        else:
                            # Contatos subsequentes: enviar menu sem imagem
                            result = send_whatsapp_menu(sender_number, send_image_first=False)
                    
                    # Processar mensagens interativas (cliques no menu)
                    elif message_type in ["interactive", "list", "reply"]:
                        logger.info(f"Processando interação do menu: {message_type} para {sender_number}")
                        
                        # Verificar se é clique em botão (button_reply)
                        button_id = None
                        item_id = None
                        item_title = None
                        
                        # Formato 1: interactive -> button_reply (botões)
                        if message.get("interactive"):
                            interactive = message.get("interactive", {})
                            if interactive.get("type") == "button_reply":
                                button_reply = interactive.get("button_reply", {})
                                button_id = button_reply.get("id")
                                logger.info(f"🔘 Botão clicado: {button_id}")
                                # Processar botão
                                result = processar_botao_menu(button_id, sender_number)
                                continue
                            elif interactive.get("type") == "list_reply":
                                list_reply = interactive.get("list_reply", {})
                                item_id = list_reply.get("id")
                                item_title = list_reply.get("title")
                        
                        # Formato 2: list -> id (menu de lista)
                        elif message.get("list"):
                            list_data = message.get("list", {})
                            item_id = list_data.get("id")
                            item_title = list_data.get("title")
                        
                        # Formato 3: reply -> list_reply ou button_reply
                        elif message.get("reply"):
                            reply_data = message.get("reply", {})
                            if reply_data.get("type") == "button_reply":
                                button_id = reply_data.get("button_reply", {}).get("id")
                                logger.info(f"🔘 Botão clicado (formato reply): {button_id}")
                                result = processar_botao_menu(button_id, sender_number)
                                continue
                            elif reply_data.get("type") == "list_reply":
                                list_reply = reply_data.get("list_reply", {})
                                item_id = list_reply.get("id")
                                item_title = list_reply.get("title")
                        
                        # Remover prefixo "ListV3:" se presente
                        if item_id and item_id.startswith("ListV3:"):
                            item_id = item_id.replace("ListV3:", "")
                        
                        logger.info(f"Item selecionado: {item_id}, Título: {item_title}")
                        
                        # Processar item do menu (lista)
                        result = processar_item_menu(item_id, item_title, sender_number)
                    
                    if result and "error" in result:
                        logger.error(f"Erro ao enviar resposta: {result['error']}")
                    
                except Exception as e:
                    logger.error(f"Erro ao processar mensagem: {str(e)}", exc_info=True)
        
        # Processar eventos de chamada diretamente (formato alternativo)
        if data.get("event", {}).get("type") == "call" or data.get("type") == "call":
            logger.info("Evento de chamada detectado - Rejeitando automaticamente...")
            call_data = data.get("event", {}) or data
            sender_number = (
                call_data.get("from") or 
                call_data.get("chat_id") or 
                call_data.get("wa_id") or
                data.get("from")
            )
            call_id = call_data.get("id") or call_data.get("call_id")
            
            if sender_number:
                reject_whatsapp_call(sender_number, call_id)
            
            return JsonResponse({
                "status": "success",
                "message": "Chamada rejeitada",
                "version": CURRENT_VERSION
            }, status=200)
        
        # Processar formato "chats_updates" (formato alternativo Whapi Cloud)
        elif data.get("chats_updates"):
            logger.info("Processando formato chats_updates")
            for chat_update in data.get("chats_updates", []):
                before_update = chat_update.get("before_update", {})
                last_message = before_update.get("last_message", {})
                
                if last_message.get("from_me", True):
                    continue
                
                message_id = last_message.get("id")
                if message_id in processed_messages:
                    continue
                
                processed_messages.add(message_id)
                
                sender_number = before_update.get("id")
                message_type = last_message.get("type")
                
                # Rejeitar chamadas no formato chats_updates também (ptt é áudio, não chamada)
                if message_type in ["call", "audio_call", "video_call"]:
                    logger.info(f"Chamada detectada no formato chats_updates de {sender_number} - Rejeitando...")
                    call_id = last_message.get("id") or last_message.get("call_id")
                    reject_whatsapp_call(sender_number, call_id)
                    continue
                
                if sender_number:
                    try:
                        # Verificar se é o primeiro contato (enviar foto da capa)
                        is_first_contact = sender_number not in numbers_with_menu
                        if is_first_contact:
                            logger.info(f"🎉 Primeiro contato detectado para {sender_number} - Enviando foto da capa")
                            numbers_with_menu.add(sender_number)
                        
                        # Processar mensagens de texto
                        if message_type == "text":
                            if is_first_contact:
                                # Primeiro contato: enviar menu com foto da capa
                                result = send_whatsapp_menu(sender_number, send_image_first=True, use_capa=True)
                            else:
                                # Contatos subsequentes: enviar menu sem imagem
                                result = send_whatsapp_menu(sender_number, send_image_first=False)
                        
                        # Processar mídias (áudio, imagem, vídeo) - enviar menu automaticamente
                        elif message_type in ["audio", "voice", "ptt", "image", "video", "document", "sticker"]:
                            logger.info(f"📎 Mídia recebida (chats_updates) - Tipo: {message_type} de {sender_number} - Enviando menu automaticamente...")
                            if is_first_contact:
                                # Primeiro contato: enviar menu com foto da capa
                                result = send_whatsapp_menu(sender_number, send_image_first=True, use_capa=True)
                            else:
                                # Contatos subsequentes: enviar menu sem imagem
                                result = send_whatsapp_menu(sender_number, send_image_first=False)
                        
                        # Processar mensagens interativas (cliques no menu)
                        elif message_type in ["interactive", "list", "reply"]:
                            reply_data = last_message.get("reply", {})
                            
                            # Verificar se é botão (button_reply)
                            if reply_data.get("type") == "button_reply":
                                button_id = reply_data.get("button_reply", {}).get("id")
                                logger.info(f"🔘 Botão clicado (chats_updates): {button_id}")
                                result = processar_botao_menu(button_id, sender_number)
                            # Verificar se é lista (list_reply)
                            elif reply_data.get("type") == "list_reply":
                                list_reply = reply_data.get("list_reply", {})
                                item_id = list_reply.get("id")
                                item_title = list_reply.get("title")
                                result = processar_item_menu(item_id, item_title, sender_number)
                            else:
                                # Tentar processar como lista mesmo sem tipo definido
                                if last_message.get("list"):
                                    list_data = last_message.get("list", {})
                                    item_id = list_data.get("id")
                                    item_title = list_data.get("title")
                                    result = processar_item_menu(item_id, item_title, sender_number)
                    except Exception as e:
                        logger.error(f"Erro ao processar: {str(e)}", exc_info=True)
        
        # Se chegou aqui sem processar nada, pode ser um webhook de verificação ou formato desconhecido
        # Retornar sucesso mesmo assim para não quebrar a API
        logger.info("Webhook recebido mas nenhuma mensagem processada (pode ser verificação ou formato desconhecido)")
        
        # Retornar sucesso
        return JsonResponse({
            "status": "success",
            "message": "Webhook recebido",
            "version": CURRENT_VERSION
        }, status=200)
        
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON do webhook: {e}")
        # Retornar 200 mesmo com erro para não quebrar a API
        return JsonResponse({
            "status": "success",
            "message": "Webhook recebido (erro ao decodificar JSON)",
            "version": CURRENT_VERSION
        }, status=200)
    except Exception as e:
        logger.error(f"Erro no webhook WhatsApp: {e}", exc_info=True)
        # Retornar 200 mesmo com erro para não quebrar a API
        return JsonResponse({
            "status": "success",
            "message": "Webhook recebido (erro processado)",
            "error": str(e),
            "version": CURRENT_VERSION
        }, status=200)


@csrf_exempt
@require_http_methods(["GET"])
def whatsapp_test_webhook(request):
    """
    Endpoint para testar o webhook
    """
    return JsonResponse({
        "status": "webhook_ativo",
        "timestamp": get_local_time(),
        "version": CURRENT_VERSION,
        "url_webhook": "/app_igreja/api/whatsapp/webhook/"
    })


@csrf_exempt
@require_http_methods(["GET"])
def whatsapp_imagem_principal(request):
    """
    Endpoint que serve a imagem principal otimizada para WhatsApp
    Redimensiona para 800x800 pixels e qualidade 75% para economizar bytes da API
    """
    from django.http import HttpResponse
    from PIL import Image
    from io import BytesIO
    import os as os_module
    
    try:
        # Buscar imagem principal
        visual = TBVISUAL.objects.first()
        
        if visual and visual.VIS_FOTO_PRINCIPAL:
            # Caminho completo do arquivo
            image_path = visual.VIS_FOTO_PRINCIPAL.path
            
            if os_module.path.exists(image_path):
                # Abrir e otimizar imagem
                img = Image.open(image_path)
                
                # Converter para RGB se necessário
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Redimensionar para 800x800 (tamanho ideal para WhatsApp)
                width, height = img.size
                max_size = 800
                
                if width > max_size or height > max_size:
                    ratio = min(max_size / width, max_size / height)
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                else:
                    new_width, new_height = width, height
                
                # Salvar em memória com qualidade 75% (economiza bytes)
                output = BytesIO()
                img.save(output, format='JPEG', quality=75, optimize=True)
                output.seek(0)
                
                # Retornar imagem otimizada
                response = HttpResponse(output.read(), content_type='image/jpeg')
                response['Cache-Control'] = 'public, max-age=3600'  # Cache de 1 hora
                logger.info(f"✅ Imagem principal otimizada servida: {new_width}x{new_height} ({os_module.path.getsize(image_path)} bytes -> otimizado)")
                return response
            else:
                logger.warning(f"⚠️  Arquivo de imagem não encontrado: {image_path}")
        else:
            logger.info("ℹ️  Nenhuma imagem principal configurada, usando padrão")
        
        # Fallback: usar imagem padrão
        from django.conf import settings
        from django.contrib.staticfiles import finders
        default_image_path = finders.find('img/oncristo2.png')
        
        if not default_image_path:
            # Se não encontrar via staticfiles, tentar caminho direto
            default_image_path = os_module.path.join(settings.BASE_DIR, 'static', 'img', 'oncristo2.png')
        
        if os_module.path.exists(default_image_path):
            img = Image.open(default_image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Redimensionar se necessário
            width, height = img.size
            max_size = 800
            if width > max_size or height > max_size:
                ratio = min(max_size / width, max_size / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            output = BytesIO()
            img.save(output, format='JPEG', quality=75, optimize=True)
            output.seek(0)
            
            response = HttpResponse(output.read(), content_type='image/jpeg')
            response['Cache-Control'] = 'public, max-age=3600'
            return response
        
        # Se não encontrar nada, retornar 404
        return HttpResponse("Imagem não encontrada", status=404)
        
    except Exception as e:
        logger.error(f"❌ Erro ao servir imagem otimizada: {str(e)}", exc_info=True)
        return HttpResponse(f"Erro ao processar imagem: {str(e)}", status=500)


@csrf_exempt
@require_http_methods(["POST"])
def whatsapp_cadastro_dizimista(request):
    """
    Endpoint para cadastro de dizimista via API (ex: formulário web que chama a API)
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        
        # Reutiliza o formulário público de dizimistas
        form = DizimistaPublicoForm(data)
        if form.is_valid():
            dizimista = form.save(commit=False)
            dizimista.DIS_status = False  # Pendente por padrão
            dizimista.save()
            return JsonResponse({
                'success': True,
                'message': 'Dizimista cadastrado com sucesso!',
                'dizimista_id': dizimista.pk
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'JSON inválido'
        }, status=400)
    except Exception as e:
        logger.error(f"Erro no cadastro de dizimista via API: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
