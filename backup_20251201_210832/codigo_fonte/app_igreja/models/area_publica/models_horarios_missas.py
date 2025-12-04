import logging
import json

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