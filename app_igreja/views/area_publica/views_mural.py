from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.urls import reverse

from ...models.area_admin.models_mural import TBMURAL
from ...models.area_admin.models_paroquias import TBPAROQUIA


def mural_publico_redirect(request):
    """Redireciona /mural/ para o mural mais recente (mural_id=0)."""
    return redirect(reverse('app_igreja:mural_publico', args=[0]))


def mural_publico(request, mural_id):
    """
    Visualiza os detalhes de um mural (área pública)
    Apenas murais ativos podem ser visualizados
    """
    if mural_id == 0:
        # Se ID for 0, pegar o mural mais recente
        mural = TBMURAL.objects.filter(MUR_ativo=True).order_by('-MUR_data_mural').first()
        if not mural:
            # Se não houver nenhum mural ativo
            return render(request, 'area_publica/tpl_mural_publico.html', {
                'paroquia': TBPAROQUIA.objects.first(),
                'erro': 'Nenhum mural disponível no momento.'
            })
    else:
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
    
    # Determinar a URL de retorno correta
    url_retorno = request.META.get('HTTP_REFERER')
    if not url_retorno:
        if request.GET.get('modo') == 'app' or request.session.get('modo_app'):
            url_retorno = reverse('app_igreja:app_medias')
        else:
            url_retorno = reverse('home')
    elif 'modo=app' not in url_retorno and (request.GET.get('modo') == 'app' or request.session.get('modo_app')):
        # Garantir que o referer mantenha o modo app se estivermos no app
        sep = '&' if '?' in url_retorno else '?'
        url_retorno = f"{url_retorno}{sep}modo=app"
    
    context = {
        'mural': mural,
        'paroquia': paroquia,
        'acao': 'consultar',
        'url_retorno': url_retorno,
        'fotos_count': fotos_count,
        'legendas_count': legendas_count,
        'mural_section': 'detail',
    }
    
    # Usa template específico para área pública
    return render(request, 'area_publica/tpl_mural_publico.html', context)

