from django.shortcuts import render
import logging
import json
from django.http import JsonResponse

from app_igreja.models.area_admin.models_paroquias import TBPAROQUIA

logger = logging.getLogger(__name__)

def get_horarios_por_dia(dia_semana):
    """Busca horários de missas por dia da semana"""
    try:
        # Busca a paróquia (assumindo que há apenas uma)
        paroquia = TBPAROQUIA.objects.first()
        
        if not paroquia or not paroquia.PAR_horarios_fixos_json:
            return []
        
        # Converte JSON para dicionário Python
        horarios_json = json.loads(paroquia.PAR_horarios_fixos_json)
        
        # Busca horários do dia específico
        horarios_do_dia = horarios_json.get(dia_semana, [])
        
        return horarios_do_dia
        
    except Exception as e:
        logger.error(f"Erro ao buscar horários para {dia_semana}: {e}")
        return []

def get_horarios_semana():
    """Busca todos os horários da semana organizados por dia"""
    try:
        dias_semana = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo']
        horarios_semana = {}
        
        for dia in dias_semana:
            horarios_semana[dia] = get_horarios_por_dia(dia)
        
        return horarios_semana
        
    except Exception as e:
        logger.error(f"Erro ao buscar horários da semana: {e}")
        return {}
        
def horarios_missas_publico(request):
    """Página pública de horários de missas"""
    try:
        # Busca horários da semana
        horarios_semana = get_horarios_semana()
        
        # Prepara os dados para o template
        context = {
            'horarios_semana': horarios_semana,
            'paroquia': getattr(request, 'paroquia', None),
        }
        
        # Renderiza o template
        return render(request, 'area_publica/tpl_horarios_missas.html', context)

    except Exception as e:
        logger.error(f"Erro na página de horários de missas: {str(e)}")
        return render(request, 'area_publica/error.html', {
            'error_message': f"Erro ao carregar horários: {str(e)}"
        }, status=500)

def api_horarios_missas(request):
    """API para buscar horários de missas"""
    try:
        horarios_semana = get_horarios_semana()
        return JsonResponse({'horarios_semana': horarios_semana})
    except Exception as e:
        logger.error(f"Erro na API de horários: {str(e)}")
        return JsonResponse({"error": "Erro interno do servidor"}, status=500)

def proximas_missas_api(request):
    """API para buscar próximas missas"""
    try:
        # Por enquanto retorna vazio
        return JsonResponse({'proximas_missas': []})
    except Exception as e:
        logger.error(f"Erro na API de próximas missas: {str(e)}")
        return JsonResponse({"error": "Erro interno do servidor"}, status=500)