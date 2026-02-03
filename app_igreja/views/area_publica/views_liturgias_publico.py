from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, date
from django.db.models import Q

from ...models.area_admin.models_extrator_liturgias import TBLITURGIA
from ...models.area_admin.models_paroquias import TBPAROQUIA


def liturgias_publico(request):
    """
    Área pública para visualizar liturgias
    Por padrão, mostra apenas a liturgia do dia atual
    Filtro por data e tipo de liturgia
    """
    # Buscar paróquia
    paroquia = TBPAROQUIA.objects.first()
    
    # Buscar liturgias ativas
    liturgias = TBLITURGIA.objects.filter(LIT_STATUSLIT=True).order_by('-LIT_DATALIT', 'LIT_TIPOLIT')
    
    # Filtro por data
    data_filtro_str = request.GET.get('data', '').strip()
    data_hoje = date.today()
    
    # Se não houver filtro de data, usar a data de hoje por padrão
    if not data_filtro_str:
        liturgias = liturgias.filter(LIT_DATALIT=data_hoje)
        data_filtro_str = data_hoje.strftime('%Y-%m-%d')  # Define o filtro como hoje para exibir no campo
    else:
        try:
            data_filtro = datetime.strptime(data_filtro_str, '%Y-%m-%d').date()
            liturgias = liturgias.filter(LIT_DATALIT=data_filtro)
        except ValueError:
            # Se a data for inválida, usar a data de hoje
            liturgias = liturgias.filter(LIT_DATALIT=data_hoje)
            data_filtro_str = data_hoje.strftime('%Y-%m-%d')
    
    # Filtro por tipo
    tipo_filtro = request.GET.get('tipo', '').strip()
    if tipo_filtro:
        liturgias = liturgias.filter(LIT_TIPOLIT__icontains=tipo_filtro)
    
    # Agrupar por data para melhor visualização
    liturgias_por_data = {}
    for liturgia in liturgias:
        data_key = liturgia.LIT_DATALIT.strftime('%d/%m/%Y')
        if data_key not in liturgias_por_data:
            liturgias_por_data[data_key] = []
        liturgias_por_data[data_key].append(liturgia)
    
    # Tipos disponíveis para o filtro
    tipos_disponiveis = TBLITURGIA.TIPO_LITURGIA_CHOICES
    
    # Determinar URL de retorno baseada no modo
    from django.urls import reverse
    if request.GET.get('modo') == 'app' or request.session.get('modo_app'):
        url_retorno = reverse('app_igreja:app_info')
    else:
        url_retorno = reverse('home')

    context = {
        'paroquia': paroquia,
        'liturgias': liturgias,
        'liturgias_por_data': liturgias_por_data,
        'tipos_disponiveis': tipos_disponiveis,
        'data_filtro': data_filtro_str,
        'tipo_filtro': tipo_filtro,
        'url_retorno': url_retorno,
    }
    
    return render(request, 'area_publica/tpl_liturgias_publico.html', context)

