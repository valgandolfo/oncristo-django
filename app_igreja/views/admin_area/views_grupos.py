"""CRUD de Grupos Litúrgicos (TBGRUPOS) - listar, criar, editar, detalhar, excluir, dashboard."""
from datetime import date, timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from ...forms.area_admin.forms_grupos import GrupoForm
from ...models.area_admin.models_grupos import TBGRUPOS
from ...utils import reconstruir_url_com_filtros

URL_GRUPOS_CRUD_MAIS = 'app_igreja:grupos_crud_mais'
FILTROS_GRUPOS = ['busca_nome', 'filtro_ativo', 'page']


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, 'Acesso negado. Apenas administradores podem acessar esta área.')
            return redirect('app_igreja:admin_area')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def _redirect_listar_grupos(request):
    return redirect(reconstruir_url_com_filtros(request, URL_GRUPOS_CRUD_MAIS, FILTROS_GRUPOS))


@login_required
@admin_required
def listar_grupos(request):
    busca_nome = request.GET.get('busca_nome', '').strip()
    filtro_ativo = request.GET.get('filtro_ativo', '').strip()
    busca_realizada = bool(busca_nome or filtro_ativo or request.GET.get('page'))
    if busca_realizada:
        grupos = TBGRUPOS.objects.all().order_by('GRU_nome_grupo')
        if busca_nome and busca_nome.lower() not in ('todos', 'todas'):
            grupos = grupos.filter(GRU_nome_grupo__icontains=busca_nome)
        if filtro_ativo != '':
            grupos = grupos.filter(GRU_ativo=bool(int(filtro_ativo)))
    else:
        grupos = TBGRUPOS.objects.none()
    paginator = Paginator(grupos, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    qs = TBGRUPOS.objects.all()
    context = {
        'page_obj': page_obj,
        'grupos': page_obj,
        'total_grupos': qs.count(),
        'grupos_ativos': qs.filter(GRU_ativo=True).count(),
        'grupos_inativos': qs.filter(GRU_ativo=False).count(),
        'grupos_hoje': TBGRUPOS.objects.filter(GRU_data_cadastro__date=date.today()).count(),
        'modo_dashboard': True,
        'busca_realizada': busca_realizada,
        'busca_nome': busca_nome,
        'filtro_ativo': filtro_ativo,
    }
    return render(request, 'admin_area/tpl_grupos.html', context)


@login_required
@admin_required
def criar_grupo(request):
    if request.method == 'POST':
        form = GrupoForm(request.POST)
        if form.is_valid():
            form.save()
            return _redirect_listar_grupos(request)
    else:
        form = GrupoForm()
    context = {
        'form': form, 'grupo': None, 'acao': 'incluir', 'model_verbose_name': 'Grupo',
        'next_url': request.META.get('HTTP_REFERER') or reverse(URL_GRUPOS_CRUD_MAIS), 'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_grupos.html', context)


@login_required
@admin_required
def editar_grupo(request, grupo_id):
    grupo = get_object_or_404(TBGRUPOS, GRU_id=grupo_id)
    if request.method == 'POST':
        form = GrupoForm(request.POST, instance=grupo)
        if form.is_valid():
            form.save()
            return _redirect_listar_grupos(request)
    else:
        form = GrupoForm(instance=grupo)
    context = {
        'form': form, 'grupo': grupo, 'acao': 'editar', 'model_verbose_name': 'Grupo',
        'next_url': request.META.get('HTTP_REFERER') or reverse(URL_GRUPOS_CRUD_MAIS), 'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_grupos.html', context)


@login_required
@admin_required
def detalhar_grupo(request, grupo_id):
    grupo = get_object_or_404(TBGRUPOS, GRU_id=grupo_id)
    context = {'grupo': grupo, 'acao': 'consultar', 'model_verbose_name': 'Grupo', 'modo_detalhe': True}
    return render(request, 'admin_area/tpl_grupos.html', context)


@login_required
@admin_required
def excluir_grupo(request, grupo_id):
    grupo = get_object_or_404(TBGRUPOS, GRU_id=grupo_id)
    if request.method == 'POST':
        grupo.delete()
        return _redirect_listar_grupos(request)
    context = {
        'form': GrupoForm(instance=grupo), 'grupo': grupo, 'acao': 'excluir', 'model_verbose_name': 'Grupo',
        'next_url': request.META.get('HTTP_REFERER') or reverse(URL_GRUPOS_CRUD_MAIS), 'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_grupos.html', context)


@login_required
@admin_required
def dashboard_grupos(request):
    qs = TBGRUPOS.objects.all()
    data_limite = timezone.now() - timedelta(days=30)
    context = {
        'total_grupos': qs.count(),
        'grupos_ativos': qs.filter(GRU_ativo=True).count(),
        'grupos_inativos': qs.filter(GRU_ativo=False).count(),
        'grupos_recentes': TBGRUPOS.objects.filter(GRU_data_cadastro__gte=data_limite).count(),
        'grupos_por_status': qs.values('GRU_ativo').annotate(total=Count('GRU_id')).order_by('GRU_ativo'),
    }
    return render(request, 'admin_area/dashboard_grupos.html', context)
