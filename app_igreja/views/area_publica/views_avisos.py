from django.shortcuts import render
from django.utils import timezone
from datetime import datetime

from ...models.area_admin.models_avisos import TBAVISO
from ...models.area_admin.models_paroquias import TBPAROQUIA


def avisos_paroquia(request):
    """
    Área pública para visualizar avisos da paróquia
    Filtro por período de data
    """
    # Buscar paróquia
    paroquia = TBPAROQUIA.objects.first()
    
    # Buscar avisos
    avisos = TBAVISO.objects.all().order_by('-AVI_data')
    
    # Filtro por data (filtrar até a data)
    data_fim_str = request.GET.get('data_fim', '').strip()
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            avisos = avisos.filter(AVI_data__lte=data_fim)
        except ValueError:
            pass
    
    context = {
        'paroquia': paroquia,
        'avisos': avisos,
    }
    
    return render(request, 'area_publica/tpl_avisos_paroquia_publico.html', context)

