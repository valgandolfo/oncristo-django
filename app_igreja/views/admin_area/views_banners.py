"""
==================== VIEWS DE BANNERS ====================
Arquivo com views para CRUD de Banners de Patrocinadores
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse
from functools import wraps

from ...models.area_admin.models_banners import TBBANNERS
from ...forms.area_admin.forms_banners import BannerForm


def admin_required(view_func):
    """Decorator para verificar se o usuário é administrador"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Apenas superusuários podem acessar área admin
        if not request.user.is_superuser:
            messages.error(request, 'Acesso negado. Apenas administradores podem acessar esta área.')
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_required
@admin_required
def listar_banners(request):
    """
    Lista todos os banners com paginação
    """
    
    # Busca
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    
    # Controla se o usuário já executou uma busca (preencheu algum filtro ou navegou na paginação)
    busca_realizada = bool(query or status_filter or request.GET.get('page'))
    
    # Só carrega os registros no grid DEPOIS que o usuário aplicar um filtro
    if busca_realizada:
        # Carrega os registros
        banners = TBBANNERS.objects.all()
        
        # Se digitar "todos" ou "todas", ignora outros filtros e traz tudo
        if query.lower() in ['todos', 'todas']:
            # Mantém todos os registros sem filtros adicionais
            pass
        else:
            if query:
                banners = banners.filter(
                    Q(BAN_NOME_PATROCINADOR__icontains=query) | 
                    Q(BAN_DESCRICAO_COMERCIAL__icontains=query) |
                    Q(BAN_TELEFONE__icontains=query) |
                    Q(BAN_ENDERECO__icontains=query)
                )
            
            if status_filter:
                if status_filter == 'ativo':
                    banners = banners.filter(BAN_ORDEM__gt=0)
                elif status_filter == 'inativo':
                    banners = banners.filter(BAN_ORDEM=0)
    else:
        # Queryset vazio até que o usuário faça a primeira busca
        banners = TBBANNERS.objects.none()
    
    # Ordenação
    banners = banners.order_by('BAN_ORDEM', 'BAN_NOME_PATROCINADOR')
    
    # Paginação
    paginator = Paginator(banners, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    total_banners = TBBANNERS.objects.count()
    ativos = TBBANNERS.objects.filter(BAN_ORDEM__gt=0).count()
    inativos = TBBANNERS.objects.filter(BAN_ORDEM=0).count()
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
        'total_banners': total_banners,
        'ativos': ativos,
        'inativos': inativos,
        'modo_dashboard': True,
        'busca_realizada': busca_realizada,
    }
    
    return render(request, 'admin_area/tpl_banners.html', context)


@login_required
@admin_required
def criar_banner(request):
    """
    Cria um novo banner
    """
    
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                banner = form.save()
                messages.success(request, 'Banner criado com sucesso! A imagem foi salva no AWS S3.')
            except Exception as e:
                messages.error(request, f'Erro ao salvar banner no S3: {str(e)}')
                return render(request, 'admin_area/tpl_banners.html', {
                    'form': form,
                    'acao': 'incluir',
                    'model_verbose_name': 'Banner de Patrocinador',
                    'next_url': request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_banners'),
                    'modo_detalhe': True,
                })
            return redirect('app_igreja:listar_banners')
        else:
            messages.error(request, 'Erro ao cadastrar banner. Verifique os dados.')
    else:
        form = BannerForm()
    
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_banners')
    context = {
        'form': form,
        'acao': 'incluir',
        'model_verbose_name': 'Banner de Patrocinador',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_banners.html', context)


@login_required
@admin_required
def detalhar_banner(request, banner_id):
    """
    Mostra detalhes de um banner
    """
    banner = get_object_or_404(TBBANNERS, id=banner_id)
    
    context = {
        'banner': banner,
        'acao': 'consultar',
        'model_verbose_name': 'Banner de Patrocinador',
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_banners.html', context)


@login_required
@admin_required
def editar_banner(request, banner_id):
    """
    Edita um banner existente
    """
    banner = get_object_or_404(TBBANNERS, id=banner_id)
    
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Banner atualizado com sucesso! A imagem foi salva no AWS S3.')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar banner no S3: {str(e)}')
                return render(request, 'admin_area/tpl_banners.html', {
                    'form': form,
                    'banner': banner,
                    'acao': 'editar',
                    'model_verbose_name': 'Banner de Patrocinador',
                    'next_url': request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_banners'),
                    'modo_detalhe': True,
                })
            return redirect('app_igreja:listar_banners')
        else:
            messages.error(request, 'Erro ao atualizar banner. Verifique os campos.')
    else:
        form = BannerForm(instance=banner)
    
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_banners')
    context = {
        'form': form,
        'banner': banner,
        'acao': 'editar',
        'model_verbose_name': 'Banner de Patrocinador',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_banners.html', context)


@login_required
@admin_required
def excluir_banner(request, banner_id):
    """
    Exclui um banner
    """
    banner = get_object_or_404(TBBANNERS, id=banner_id)
    
    if request.method == 'POST':
        banner.delete()
        messages.success(request, 'Banner excluído com sucesso!')
        return redirect('app_igreja:listar_banners')
    
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_banners')
    context = {
        'banner': banner,
        'acao': 'excluir',
        'model_verbose_name': 'Banner de Patrocinador',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_banners.html', context)
