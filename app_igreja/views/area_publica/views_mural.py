from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.urls import reverse

from ...models.area_admin.models_mural import TBMURAL
from ...models.area_admin.models_paroquias import TBPAROQUIA


def mural_publico(request, mural_id):
    """
    Visualiza os detalhes de um mural (área pública)
    Apenas murais ativos podem ser visualizados
    Usa o mesmo template da área admin
    """
    mural = get_object_or_404(TBMURAL, MUR_ID=mural_id, MUR_ativo=True)
    paroquia = TBPAROQUIA.objects.first()
    
    # Contar fotos
    fotos_count = sum([
        1 if mural.MUR_foto1_mural else 0,
        1 if mural.MUR_foto2_mural else 0,
        1 if mural.MUR_foto3_mural else 0,
        1 if mural.MUR_foto4_mural else 0,
        1 if mural.MUR_foto5_mural else 0,
    ])
    
    # Contar legendas
    legendas_count = sum([
        1 if mural.MUR_legenda1_mural else 0,
        1 if mural.MUR_legenda2_mural else 0,
        1 if mural.MUR_legenda3_mural else 0,
        1 if mural.MUR_legenda4_mural else 0,
        1 if mural.MUR_legenda5_mural else 0,
    ])
    
    # Usar HTTP_REFERER como fallback ou home
    next_url = request.META.get('HTTP_REFERER') or reverse('home')
    
    context = {
        'mural': mural,
        'paroquia': paroquia,
        'acao': 'consultar',
        'next_url': next_url,
        'fotos_count': fotos_count,
        'legendas_count': legendas_count,
        'mural_section': 'detail',
    }
    
    # Usa template específico para área pública
    return render(request, 'area_publica/tpl_mural_publico.html', context)

