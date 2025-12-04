"""
View para verificar transmissão ao vivo do YouTube e exibir vídeo
"""
import re
import requests
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ...models.area_admin.models_paroquias import TBPAROQUIA

logger = logging.getLogger(__name__)


def extrair_id_canal_youtube(url):
    """
    Extrai o ID do canal ou username do YouTube da URL
    Suporta formatos:
    - https://www.youtube.com/@username
    - https://www.youtube.com/c/channelname
    - https://www.youtube.com/channel/UCxxxxx
    - https://youtube.com/@username
    """
    if not url:
        return None
    
    # Remover espaços e barras finais
    url = url.strip().rstrip('/')
    
    # Padrão para @username
    match = re.search(r'youtube\.com/@([^/?]+)', url)
    if match:
        return {'type': 'username', 'id': match.group(1)}
    
    # Padrão para /c/channelname
    match = re.search(r'youtube\.com/c/([^/?]+)', url)
    if match:
        return {'type': 'custom', 'id': match.group(1)}
    
    # Padrão para /channel/UCxxxxx
    match = re.search(r'youtube\.com/channel/([^/?]+)', url)
    if match:
        return {'type': 'channel', 'id': match.group(1)}
    
    return None


@csrf_exempt
@require_http_methods(["GET"])
def verificar_youtube_ao_vivo(request):
    """
    Verifica se há transmissão ao vivo no canal do YouTube da paróquia
    Retorna JSON com status e URL do vídeo ao vivo (se houver)
    """
    try:
        paroquia = TBPAROQUIA.objects.first()
        if not paroquia or not paroquia.PAR_url_youtube:
            return JsonResponse({
                'ao_vivo': False,
                'message': 'URL do YouTube não configurada'
            })
        
        youtube_url = paroquia.PAR_url_youtube
        canal_info = extrair_id_canal_youtube(youtube_url)
        
        if not canal_info:
            return JsonResponse({
                'ao_vivo': False,
                'message': 'Não foi possível extrair ID do canal'
            })
        
        # Por enquanto, vamos usar uma abordagem simples:
        # Verificar se há vídeos ao vivo na página do canal
        # Em produção, você pode usar a API do YouTube Data API v3
        
        # Abordagem alternativa: verificar via RSS feed do canal
        # ou usar iframe para detectar transmissão ao vivo
        
        # Por enquanto, vamos retornar que não há transmissão ao vivo
        # mas fornecer a URL do canal para o frontend verificar
        
        return JsonResponse({
            'ao_vivo': False,  # Será atualizado quando implementar verificação real
            'canal_url': youtube_url,
            'canal_info': canal_info,
            'message': 'Verificação de transmissão ao vivo não implementada ainda'
        })
        
    except Exception as e:
        logger.error(f"Erro ao verificar YouTube ao vivo: {e}", exc_info=True)
        return JsonResponse({
            'ao_vivo': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def obter_url_youtube_canal(request):
    """
    Retorna a URL do canal do YouTube da paróquia
    """
    try:
        paroquia = TBPAROQUIA.objects.first()
        if not paroquia or not paroquia.PAR_url_youtube:
            return JsonResponse({
                'url': None,
                'ao_vivo': False
            })
        
        return JsonResponse({
            'url': paroquia.PAR_url_youtube,
            'ao_vivo': False  # Será verificado no frontend
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter URL do YouTube: {e}", exc_info=True)
        return JsonResponse({
            'url': None,
            'error': str(e)
        }, status=500)

