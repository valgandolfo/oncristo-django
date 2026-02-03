from django.shortcuts import render
from django.http import JsonResponse
from app_igreja.models.area_admin.models_paroquias import TBPAROQUIA
from app_igreja.models.area_admin.models_mural import TBMURAL
from app_igreja.models.area_admin.models_visual import TBVISUAL
from app_igreja.models.area_admin.models_banners import TBBANNERS

def get_app_context():
    """Retorna o contexto comum para as telas do app"""
    paroquia = TBPAROQUIA.objects.first()
    visual = TBVISUAL.objects.first()
    return {
        'paroquia': paroquia,
        'visual': visual,
    }

def app_home(request):
    """Tela Home do App Flutter"""
    context = get_app_context()
    return render(request, 'app/tab_home.html', context)

def app_info(request):
    """Tela de Informações do App Flutter"""
    context = get_app_context()
    return render(request, 'app/tab_info.html', context)

def app_servicos(request):
    """Tela de Serviços do App Flutter"""
    context = get_app_context()
    return render(request, 'app/tab_servicos.html', context)

def app_medias(request):
    """Tela de Mídias do App Flutter"""
    context = get_app_context()
    return render(request, 'app/tab_medias.html', context)

def app_config_api(request):
    """API que retorna a configuração dos menus para o Flutter"""
    base_url = request.build_absolute_uri('/')[:-1]
    
    config = {
        "tabs": [
            {
                "label": "HOME",
                "icon": "home",
                "url": f"{base_url}/app_igreja/app/home/?modo=app"
            },
            {
                "label": "INFORMAÇÕES",
                "icon": "info_outline",
                "url": f"{base_url}/app_igreja/app/info/?modo=app"
            },
            {
                "label": "SERVIÇOS",
                "icon": "list_alt",
                "url": f"{base_url}/app_igreja/app/servicos/?modo=app"
            },
            {
                "label": "MEDIAS",
                "icon": "share",
                "url": f"{base_url}/app_igreja/app/medias/?modo=app"
            }
        ]
    }
    return JsonResponse(config)
