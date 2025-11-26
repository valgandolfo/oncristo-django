"""
==================== VIEW PÚBLICA CALENDÁRIO DE EVENTOS ====================
View pública para visualizar calendário de eventos da paróquia
Filtro por período de data (data inicial e final)
"""

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import datetime, date
from django.db.models import Q

from ...models.area_admin.models_eventos import TBEVENTO, TBITEM_EVENTO
from ...models.area_admin.models_paroquias import TBPAROQUIA


def calendario_eventos_publico(request):
    """
    Área pública para visualizar calendário de eventos da paróquia
    Filtro por período de data (data inicial e final)
    """
    # Buscar paróquia
    paroquia = TBPAROQUIA.objects.first()
    
    # Buscar eventos ativos
    eventos = TBEVENTO.objects.filter(EVE_STATUS='Ativo').order_by('EVE_DT_INICIAL', 'EVE_HORA_INICIAL')
    
    # Filtros por data
    data_inicial_str = request.GET.get('data_inicial', '').strip()
    data_final_str = request.GET.get('data_final', '').strip()
    
    # Aplicar filtros
    data_inicial = None
    data_final = None
    
    if data_inicial_str:
        try:
            data_inicial = datetime.strptime(data_inicial_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    if data_final_str:
        try:
            data_final = datetime.strptime(data_final_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Se ambas as datas foram informadas, filtrar eventos que estão no período
    if data_inicial and data_final:
        # Eventos que começam ou terminam no período, ou que estão completamente dentro
        eventos = eventos.filter(
            Q(EVE_DT_INICIAL__range=[data_inicial, data_final]) |
            Q(EVE_DT_FINAL__range=[data_inicial, data_final]) |
            Q(EVE_DT_INICIAL__lte=data_inicial, EVE_DT_FINAL__gte=data_final) |
            Q(EVE_DT_INICIAL__gte=data_inicial, EVE_DT_INICIAL__lte=data_final) |
            Q(EVE_DT_FINAL__gte=data_inicial, EVE_DT_FINAL__lte=data_final)
        )
    elif data_inicial:
        # Apenas data inicial: eventos que começam a partir desta data
        eventos = eventos.filter(
            Q(EVE_DT_INICIAL__gte=data_inicial) |
            Q(EVE_DT_FINAL__gte=data_inicial) |
            Q(EVE_DT_INICIAL__lte=data_inicial, EVE_DT_FINAL__gte=data_inicial)
        )
    elif data_final:
        # Apenas data final: eventos que terminam até esta data
        eventos = eventos.filter(
            Q(EVE_DT_INICIAL__lte=data_final) |
            Q(EVE_DT_FINAL__lte=data_final) |
            Q(EVE_DT_INICIAL__lte=data_final, EVE_DT_FINAL__gte=data_final)
        )
    
    context = {
        'paroquia': paroquia,
        'eventos': eventos,
        'data_inicial': data_inicial_str,
        'data_final': data_final_str,
    }
    
    return render(request, 'area_publica/tpl_calendario_eventos_publico.html', context)


def ver_programacao_evento(request, evento_id):
    """
    Retorna os itens (atividades) de um evento específico
    Usado via AJAX para exibir programação
    """
    evento = get_object_or_404(TBEVENTO, pk=evento_id, EVE_STATUS='Ativo')
    itens = evento.itens.all().order_by('ITEM_EVE_DATA_INICIAL', 'ITEM_EVE_HORA_INICIAL')
    
    atividades = []
    for item in itens:
        atividades.append({
            'data': item.ITEM_EVE_DATA_INICIAL.strftime('%d/%m/%Y'),
            'hora': item.ITEM_EVE_HORA_INICIAL.strftime('%H:%M') if item.ITEM_EVE_HORA_INICIAL else '',
            'atividade': item.ITEM_EVE_ACAO,
        })
    
    from django.http import JsonResponse
    return JsonResponse({
        'evento_titulo': evento.EVE_TITULO,
        'atividades': atividades
    })

