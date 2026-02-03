from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from django.views.generic.base import RedirectView
from django.conf import settings
from app_igreja.views.area_publica.views_whatsapp_api import whatsapp_webhook, whatsapp_rota_diagnostico
from app_igreja.models.area_admin.models_paroquias import TBPAROQUIA
from app_igreja.models.area_admin.models_mural import TBMURAL
from app_igreja.models.area_admin.models_visual import TBVISUAL
from app_igreja.models.area_admin.models_banners import TBBANNERS
from app_igreja.views.area_publica.views_registro import register_view

def home(request):
    """Página inicial da aplicação"""
    # Se estiver no modo app, redirecionar para a home do app
    if request.GET.get('modo') == 'app':
        from django.shortcuts import redirect
        return redirect('app_igreja:app_home')

    # Buscar dados da paróquia (primeira paróquia cadastrada)
    paroquia = None
    try:
        paroquia = TBPAROQUIA.objects.first()
    except Exception as e:
        print(f"Erro ao buscar paróquia: {e}")
    
    # Buscar os 3 últimos murais ativos
    murais_recentes = []
    try:
        murais_recentes = TBMURAL.objects.filter(
            MUR_ativo=True
        ).order_by('-MUR_data_mural')[:3]
    except Exception as e:
        print(f"Erro ao buscar murais: {e}")
    
    # Buscar configurações visuais (imagens do S3)
    visual = None
    try:
        visual = TBVISUAL.objects.first()
    except Exception as e:
        print(f"Erro ao buscar configurações visuais: {e}")
    
    # Buscar banners ativos (ordem > 0)
    banners = []
    try:
        banners = TBBANNERS.objects.filter(BAN_ORDEM__gt=0).order_by('BAN_ORDEM')
    except Exception as e:
        print(f"Erro ao buscar banners: {e}")
    
    context = {
        'paroquia': paroquia,
        'murais_recentes': murais_recentes,
        'visual': visual,
        'banners': banners,
    }
    return render(request, 'home.html', context)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Favicon na raiz (evita 404): /favicon.ico → arquivo em static/ ou staticfiles/
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'favicon.ico', permanent=False), name='favicon'),
    # Webhook WhatsApp: https://oncristo.com.br/api/whatsapp/webhook/
    path('api/whatsapp/webhook/', whatsapp_webhook, name='whatsapp_webhook_root'),
    # Diagnóstico da rota: GET /api/whatsapp/rota/
    path('api/whatsapp/rota/', whatsapp_rota_diagnostico, name='whatsapp_rota_diagnostico'),
    # URLs de autenticação padrão do Django
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register_view, name='register'),
    
    # URLs de reset de senha
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # URLs do app principal
    path('', home, name='home'),
    path('app_igreja/', include('app_igreja.urls')),
]
