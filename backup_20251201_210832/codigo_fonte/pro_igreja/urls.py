from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from app_igreja.models.area_admin.models_paroquias import TBPAROQUIA
from app_igreja.models.area_admin.models_mural import TBMURAL
from app_igreja.models.area_admin.models_visual import TBVISUAL
from app_igreja.models.area_admin.models_banners import TBBANNERS
from app_igreja.views.views_registro import register_view

def home(request):
    """Página inicial da aplicação"""
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
