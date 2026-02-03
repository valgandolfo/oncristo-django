"""
Avisos da Paróquia - Área Pública (avisos_paroquia_pub)
"""

from django.shortcuts import render
from django.urls import reverse
from datetime import datetime

from ...models.area_admin.models_avisos import TBAVISO
from ...models.area_admin.models_paroquias import TBPAROQUIA


def avisos_paroquia_pub(request):
    """
    Área pública para visualizar avisos da paróquia.
    Filtro por período de data.
    Template: tpl_avisos_paroquia_pub.html
    URL name: avisos_paroquia_pub
    """
    paroquia = TBPAROQUIA.objects.first()
    avisos = TBAVISO.objects.all().order_by('-AVI_data')

    data_fim_str = request.GET.get('data_fim', '').strip()
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            avisos = avisos.filter(AVI_data__lte=data_fim)
        except ValueError:
            pass

    if request.GET.get('modo') == 'app' or request.session.get('modo_app'):
        url_retorno = reverse('app_igreja:app_info')
    else:
        url_retorno = reverse('home')

    context = {
        'paroquia': paroquia,
        'avisos': avisos,
        'url_retorno': url_retorno,
    }
    return render(request, 'area_publica/tpl_avisos_paroquia_pub.html', context)
