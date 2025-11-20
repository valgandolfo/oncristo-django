"""
==================== API WHATSAPP - CHATBOT ====================
API para receber webhooks do WhatsApp (Whapi Cloud) e processar comandos do chatbot
Integra com módulos existentes: Dizimistas, Liturgias, Celebrações, Orações, etc.
Baseado no app_chatbot.py (Flask) migrado para Django
"""

import os
import json
import logging
import requests
from datetime import date, datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from dotenv import load_dotenv

from ...models.area_admin.models_dizimistas import TBDIZIMISTAS
from ...models.area_publica.models_liturgias import TBLITURGIA
from ...models.area_admin.models_celebracoes import TBCELEBRACOES
from ...models.area_admin.models_oracoes import TBORACOES
from ...models.area_admin.models_paroquias import TBPAROQUIA
from ...forms.area_publica.forms_dizimistas import DizimistaPublicoForm

logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da API Whapi Cloud
API_KEY = os.getenv('WHAPI_KEY', os.getenv('WHATSAPP_API_KEY', ''))
API_BASE_URL = os.getenv('WHATSAPP_BASE_URL', 'https://gate.whapi.cloud')
CHANNEL_ID = os.getenv('CHANNEL_ID', os.getenv('WHATSAPP_CHANNEL_ID', ''))

# Versão atual do webhook
CURRENT_VERSION = "v2.0.0-django"

# Set para armazenar IDs de mensagens já processadas (em produção, usar Redis ou DB)
processed_messages = set()


def limpar_telefone(telefone):
    """Remove o código do país (55) do número do telefone"""
    if telefone and str(telefone).startswith('55'):
        return str(telefone)[2:]  # Remove os primeiros 2 dígitos (55)
    return telefone


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
        
        logger.info(f"Enviando mensagem para {phone}")
        
        response = requests.post(url, headers=headers, json=message_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("sent", False):
                logger.info(f"Mensagem enviada com sucesso. ID: {result.get('message', {}).get('id')}")
                return result
            else:
                logger.error(f"Erro ao enviar mensagem: {result}")
                return {"error": f"Erro ao enviar: {result}"}
        else:
            logger.error(f"Erro ao enviar mensagem: {response.status_code} - {response.text}")
            return {"error": f"Erro {response.status_code}: {response.text}"}
            
    except Exception as e:
        logger.error(f"Erro de conexão ao enviar mensagem: {str(e)}")
        return {"error": f"Erro de conexão: {str(e)}"}


def send_whatsapp_menu(phone):
    """Envia menu interativo via API Whapi Cloud"""
    try:
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
            "header": {"text": "📖 Paróquia - Menu Principal"},
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
                                    "title": "👥 Quero ser membro",
                                    "id": "cadastro_membro",
                                    "description": "Cadastro de membro para celebração das missas e eventos"
                                },
                                {
                                    "title": "⏰ Escalas de Missas",
                                    "id": "Escala_Missas",
                                    "description": "Para membros já cadastrados escalar celebrações como colaborador"
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


def processar_item_menu(item_id, item_title, sender_number):
    """Processa item selecionado do menu interativo"""
    telefone_limpo = limpar_telefone(sender_number)
    item_title_lower = (item_title or '').lower().strip()
    
    # Processar por título (mais confiável)
    if item_title:
        if "liturgias" in item_title_lower or "opcao 1" in item_title_lower:
            site_url = f"https://oncristo.com.br/app_igreja/liturgias/"
            return send_whatsapp_message(
                sender_number,
                "📖 **LITURGIAS**\n\n"
                "Acesse nossa página de liturgias para visualizar as leituras do dia:\n\n"
                f"🔗 {site_url}\n\n"
                "Na página você pode:\n"
                "• Ver as leituras de hoje\n"
                "• Alterar a data\n"
                "• Visualizar todas as leituras do dia"
            )
        
        elif "membro" in item_title_lower or "opcao 2" in item_title_lower:
            return send_whatsapp_message(
                sender_number,
                "📋 *CADASTRO DE MEMBRO*\n\n"
                "Funcionalidade em desenvolvimento.\n"
                "Em breve você poderá se cadastrar como membro."
            )
        
        elif "escalas" in item_title_lower or "opcao 3" in item_title_lower:
            return send_whatsapp_message(
                sender_number,
                "⏰ *ESCALAS DE MISSAS*\n\n"
                "Funcionalidade em desenvolvimento.\n"
                "Em breve você poderá acessar o sistema de escalas."
            )
        
        elif "dizimo" in item_title_lower or "dízimo" in item_title_lower or "opcao 4" in item_title_lower:
            # Cadastro de dizimista
            url_cadastro = f"https://oncristo.com.br/app_igreja/quero-ser-dizimista/"
            return send_whatsapp_message(
                sender_number,
                "💰 *CADASTRO DE DIZIMISTA*\n\n"
                "Para se cadastrar como dizimista, acesse:\n\n"
                f"🔗 {url_cadastro}\n\n"
                "Ou digite 'quero ser dizimista' para mais informações."
            )
        
        elif "agendar" in item_title_lower or "opcao 5" in item_title_lower:
            url_agendar = f"https://oncristo.com.br/app_igreja/agendar-celebracaoes/"
            return send_whatsapp_message(
                sender_number,
                "🕯️ *AGENDAR CELEBRAÇÕES*\n\n"
                "Para agendar celebrações, acesse:\n\n"
                f"🔗 {url_agendar}\n\n"
                "Você pode agendar:\n"
                "• Missas de 7º dia\n"
                "• Agradecimentos\n"
                "• Louvor\n"
                "• Outras celebrações"
            )
    
    # Processar por ID (fallback)
    if item_id == "liturgias":
        site_url = f"https://oncristo.com.br/app_igreja/liturgias/"
        return send_whatsapp_message(
            sender_number,
            "📖 **LITURGIAS**\n\n"
            "Acesse nossa página de liturgias:\n\n"
            f"🔗 {site_url}"
        )
    
    elif item_id == "dizimo_ofertas":
        url_cadastro = f"https://oncristo.com.br/app_igreja/quero-ser-dizimista/"
        return send_whatsapp_message(
            sender_number,
            "💰 *CADASTRO DE DIZIMISTA*\n\n"
            f"🔗 {url_cadastro}"
        )
    
    elif item_id == "Agendar_Celebracoes":
        url_agendar = f"https://oncristo.com.br/app_igreja/agendar-celebracaoes/"
        return send_whatsapp_message(
            sender_number,
            "🕯️ *AGENDAR CELEBRAÇÕES*\n\n"
            f"🔗 {url_agendar}"
        )
    
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
                
                # Verificar tipo de mensagem
                message_type = message.get("type")
                if message_type == "unknown":
                    logger.info("Mensagem tipo unknown, ignorando...")
                    continue
                
                # Adicionar ao conjunto de processadas
                if message_id:
                    processed_messages.add(message_id)
                
                # Extrair telefone de várias formas possíveis
                sender_number = (
                    message.get("from") or 
                    message.get("chat_id") or 
                    message.get("wa_id") or
                    message.get("sender") or
                    data.get("from")
                )
                
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
                        
                        # Sempre envia o menu (mesmo se não houver texto)
                        result = send_whatsapp_menu(sender_number)
                    
                    # Processar mensagens interativas (cliques no menu)
                    elif message_type in ["interactive", "list", "reply"]:
                        logger.info(f"Processando interação do menu: {message_type} para {sender_number}")
                        
                        # Extrair item selecionado
                        item_id = None
                        item_title = None
                        
                        # Formato 1: interactive -> list_reply
                        if message.get("interactive"):
                            interactive = message.get("interactive", {})
                            if interactive.get("type") == "list_reply":
                                list_reply = interactive.get("list_reply", {})
                                item_id = list_reply.get("id")
                                item_title = list_reply.get("title")
                        
                        # Formato 2: list -> id
                        elif message.get("list"):
                            list_data = message.get("list", {})
                            item_id = list_data.get("id")
                            item_title = list_data.get("title")
                        
                        # Formato 3: reply -> list_reply
                        elif message.get("reply"):
                            reply_data = message.get("reply", {})
                            if reply_data.get("type") == "list_reply":
                                list_reply = reply_data.get("list_reply", {})
                                item_id = list_reply.get("id")
                                item_title = list_reply.get("title")
                        
                        # Remover prefixo "ListV3:" se presente
                        if item_id and item_id.startswith("ListV3:"):
                            item_id = item_id.replace("ListV3:", "")
                        
                        logger.info(f"Item selecionado: {item_id}, Título: {item_title}")
                        
                        # Processar item do menu
                        result = processar_item_menu(item_id, item_title, sender_number)
                    
                    if result and "error" in result:
                        logger.error(f"Erro ao enviar resposta: {result['error']}")
                    
                except Exception as e:
                    logger.error(f"Erro ao processar mensagem: {str(e)}", exc_info=True)
        
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
                
                if sender_number and message_type in ['text', 'interactive', 'list', 'reply']:
                    try:
                        if message_type == "text":
                            result = send_whatsapp_menu(sender_number)
                        elif message_type in ["interactive", "list", "reply"]:
                            if last_message.get("reply", {}).get("type") == "list_reply":
                                reply_data = last_message.get("reply", {})
                                list_reply = reply_data.get("list_reply", {})
                                item_id = list_reply.get("id")
                                item_title = list_reply.get("title")
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
