from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.generic import DetailView
from functools import wraps

# Imports dos models e forms
from ...models.area_admin.models_grupos import TBGRUPOS
from ...forms.area_admin.forms_grupos import GrupoForm

def admin_required(view_func):
    """Decorator para verificar se o usuário é administrador"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, 'Acesso negado. Apenas administradores podem acessar esta área.')
            return redirect('app_igreja:admin_area')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_required
@admin_required
def listar_grupos(request):
    """
    Lista todos os grupos litúrgicos com paginação
    """
    
    grupos = TBGRUPOS.objects.all().order_by('GRU_nome_grupo')
    
    # Parâmetros de busca
    busca_nome = request.GET.get('busca_nome', '')
    filtro_ativo = request.GET.get('filtro_ativo', '')
    
    # Aplicar filtros
    if busca_nome:
        grupos = grupos.filter(GRU_nome_grupo__icontains=busca_nome)
    
    if filtro_ativo != '':
        grupos = grupos.filter(GRU_ativo=bool(int(filtro_ativo)))
    
    # Paginação
    paginator = Paginator(grupos, 10)  # 10 grupos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    total_grupos = TBGRUPOS.objects.count()
    grupos_ativos = TBGRUPOS.objects.filter(GRU_ativo=True).count()
    grupos_inativos = TBGRUPOS.objects.filter(GRU_ativo=False).count()
    from datetime import date
    grupos_hoje = TBGRUPOS.objects.filter(GRU_data_cadastro__date=date.today()).count()
    
    context = {
        'page_obj': page_obj,
        'grupos': page_obj,
        'total_grupos': total_grupos,
        'grupos_ativos': grupos_ativos,
        'grupos_inativos': grupos_inativos,
        'grupos_hoje': grupos_hoje,
        'modo_dashboard': True,  # Migrado para nova tela pai dashboard
    }
    
    return render(request, 'admin_area/tpl_grupos.html', context)


@login_required
@admin_required
def criar_grupo(request):
    """
    Cria um novo grupo litúrgico
    """
    if request.method == 'POST':
        form = GrupoForm(request.POST)
        if form.is_valid():
            grupo = form.save()
            next_url = request.POST.get('next', reverse('app_igreja:listar_grupos'))
            return redirect(next_url)
    else:
        form = GrupoForm()
    
    next_url = request.META.get('HTTP_REFERER', reverse('app_igreja:listar_grupos'))
    
    context = {
        'form': form,
        'grupo': None,
        'acao': 'incluir',
        'model_verbose_name': 'Grupo',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_grupos.html', context)


@login_required
@admin_required
def editar_grupo(request, grupo_id):
    """
    Edita um grupo litúrgico existente
    """
    grupo = get_object_or_404(TBGRUPOS, GRU_id=grupo_id)
    
    if request.method == 'POST':
        form = GrupoForm(request.POST, instance=grupo)
        if form.is_valid():
            grupo = form.save()
            next_url = request.POST.get('next', reverse('app_igreja:listar_grupos'))
            return redirect(next_url)
    else:
        form = GrupoForm(instance=grupo)
    
    next_url = request.META.get('HTTP_REFERER', reverse('app_igreja:listar_grupos'))
    
    context = {
        'form': form,
        'grupo': grupo,
        'acao': 'editar',
        'model_verbose_name': 'Grupo',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_grupos.html', context)


@login_required
@admin_required
def detalhar_grupo(request, grupo_id):
    """
    Visualiza detalhes de um grupo litúrgico
    """
    grupo = get_object_or_404(TBGRUPOS, GRU_id=grupo_id)
    
    context = {
        'grupo': grupo,
        'acao': 'consultar',
        'model_verbose_name': 'Grupo',
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_grupos.html', context)


@login_required
@admin_required
def excluir_grupo(request, grupo_id):
    """
    Exclui um grupo litúrgico
    """
    grupo = get_object_or_404(TBGRUPOS, GRU_id=grupo_id)
    
    if request.method == 'POST':
        grupo.delete()
        next_url = request.POST.get('next', reverse('app_igreja:listar_grupos'))
        return redirect(next_url)
    
    form = GrupoForm(instance=grupo)
    next_url = request.META.get('HTTP_REFERER', reverse('app_igreja:listar_grupos'))
    
    context = {
        'form': form,
        'grupo': grupo,
        'acao': 'excluir',
        'model_verbose_name': 'Grupo',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_grupos.html', context)


@login_required
@admin_required
def dashboard_grupos(request):
    """
    Dashboard com estatísticas dos grupos
    """
    # Estatísticas gerais
    total_grupos = TBGRUPOS.objects.count()
    grupos_ativos = TBGRUPOS.objects.filter(GRU_ativo=True).count()
    grupos_inativos = TBGRUPOS.objects.filter(GRU_ativo=False).count()
    
    # Grupos criados nos últimos 30 dias
    from datetime import datetime, timedelta
    from django.utils import timezone
    data_limite = timezone.now() - timedelta(days=30)
    grupos_recentes = TBGRUPOS.objects.filter(GRU_data_cadastro__gte=data_limite).count()
    
    # Grupos por status
    from django.db.models import Count
    grupos_por_status = TBGRUPOS.objects.values('GRU_ativo').annotate(
        total=Count('GRU_id')
    ).order_by('GRU_ativo')
    
    context = {
        'total_grupos': total_grupos,
        'grupos_ativos': grupos_ativos,
        'grupos_inativos': grupos_inativos,
        'grupos_recentes': grupos_recentes,
        'grupos_por_status': grupos_por_status,
    }
    
    return render(request, 'admin_area/dashboard_grupos.html', context)
