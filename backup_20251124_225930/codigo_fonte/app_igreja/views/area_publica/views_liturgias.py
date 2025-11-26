from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from datetime import datetime, date
import logging

from app_igreja.models.area_publica.models_liturgias import TBLITURGIA

logger = logging.getLogger(__name__)

def get_liturgia_por_data(data_lit):
    """Busca liturgia por data"""
    try:
        liturgias = TBLITURGIA.objects.filter(
            DATALIT=data_lit,
            STATUSLIT=True
        ).order_by(
            'TIPOLIT'  # Ordenação natural por tipo
        )
        
        if not liturgias.exists():
            return None
        
        liturgia_dict = {
            'data': data_lit.strftime('%d/%m/%Y'),
            'leituras': {}
        }
        
        for liturgia in liturgias:
            liturgia_dict['leituras'][liturgia.TIPOLIT] = liturgia.texto_formatado
        
        return liturgia_dict
        
    except Exception as e:
        logger.error(f"Erro ao buscar liturgia: {e}")
        return None

def get_liturgia_hoje():
    """Busca liturgia do dia atual"""
    return get_liturgia_por_data(date.today())

@require_http_methods(["GET"])
def liturgia_modal(request):
    """Página principal de liturgias - Modal"""
    try:
        # Busca liturgia de hoje por padrão
        liturgia_hoje = get_liturgia_hoje()
        data_hoje = date.today().strftime('%Y-%m-%d')

        context = {
            'liturgia_hoje': liturgia_hoje,
            'data_hoje': data_hoje,
        }
        
        return render(request, 'area_publica/liturgia_modal.html', context)

    except Exception as e:
        logger.error(f"Erro na página de liturgias: {str(e)}")
        return render(request, 'area_publica/error.html', {
            'error_message': f"Erro ao carregar página: {str(e)}"
        }, status=500)

@require_http_methods(["GET"])
def api_liturgia(request, data):
    """API para buscar liturgia por data"""
    try:
        data_obj = datetime.strptime(data, '%Y-%m-%d').date()
        liturgia = get_liturgia_por_data(data_obj)

        if not liturgia:
            return JsonResponse({"error": "Liturgia não encontrada"}, status=404)

        return JsonResponse(liturgia)

    except ValueError:
        return JsonResponse({"error": "Formato de data inválido"}, status=400)
    except Exception as e:
        logger.error(f"Erro na API de liturgia: {str(e)}")
        return JsonResponse({"error": "Erro interno do servidor"}, status=500)

@require_http_methods(["GET"])
def visualizar_liturgia(request, data):
    """Página para visualizar liturgia específica"""
    try:
        data_obj = datetime.strptime(data, '%Y-%m-%d').date()
        liturgia = get_liturgia_por_data(data_obj)

        if not liturgia:
            return render(request, 'area_publica/error.html', {
                'error_message': "Liturgia não encontrada"
            }, status=404)

        context = {
            'liturgia': liturgia,
            'data': data,
        }
        
        return render(request, 'area_publica/liturgia_visualizar.html', context)

    except ValueError:
        return render(request, 'area_publica/error.html', {
            'error_message': "Data inválida"
        }, status=400)
    except Exception as e:
        logger.error(f"Erro ao visualizar liturgia: {str(e)}")
        return render(request, 'area_publica/error.html', {
            'error_message': f"Erro ao carregar liturgia: {str(e)}"
        }, status=500)
