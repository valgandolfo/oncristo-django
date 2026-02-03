"""CRUD de Funções (TBFUNCAO) - listar, criar, editar, detalhar, excluir, dashboard."""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from ...forms.area_admin.forms_funcoes import FuncaoForm
from ...models.area_admin.models_funcoes import TBFUNCAO

URL_FUNCOES_CRUD_MAIS = 'app_igreja:funcoes_crud_mais'


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


@login_required
@admin_required
def listar_funcoes(request):
    busca_nome = request.GET.get('busca_nome', '').strip()
    busca_realizada = bool(busca_nome or request.GET.get('page'))
    if busca_realizada:
        funcoes = TBFUNCAO.objects.all().order_by('FUN_nome_funcao')
        if busca_nome and busca_nome.lower() not in ('todos', 'todas'):
            funcoes = funcoes.filter(FUN_nome_funcao__icontains=busca_nome)
    else:
        funcoes = TBFUNCAO.objects.none()
    paginator = Paginator(funcoes, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'page_title': 'Cadastro de Funções',
        'funcoes': page_obj,
        'page_obj': page_obj,
        'total_funcoes': TBFUNCAO.objects.count(),
        'modo_dashboard': True,
        'busca_realizada': busca_realizada,
        'busca_nome': busca_nome,
    }
    return render(request, 'admin_area/tpl_funcoes.html', context)


@login_required
@admin_required
def criar_funcao(request):
    if request.method == 'POST':
        form = FuncaoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(URL_FUNCOES_CRUD_MAIS)
    else:
        form = FuncaoForm()
    context = {
        'form': form, 'funcao': None, 'acao': 'incluir', 'model_verbose_name': 'Função',
        'next_url': request.META.get('HTTP_REFERER') or reverse(URL_FUNCOES_CRUD_MAIS), 'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_funcoes.html', context)


@login_required
@admin_required
def editar_funcao(request, funcao_id):
    funcao = get_object_or_404(TBFUNCAO, FUN_id=funcao_id)
    if request.method == 'POST':
        form = FuncaoForm(request.POST, instance=funcao)
        if form.is_valid():
            form.save()
            return redirect(URL_FUNCOES_CRUD_MAIS)
    else:
        form = FuncaoForm(instance=funcao)
    context = {
        'form': form, 'funcao': funcao, 'acao': 'editar', 'model_verbose_name': 'Função',
        'next_url': request.META.get('HTTP_REFERER') or reverse(URL_FUNCOES_CRUD_MAIS), 'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_funcoes.html', context)


@login_required
@admin_required
def detalhar_funcao(request, funcao_id):
    funcao = get_object_or_404(TBFUNCAO, FUN_id=funcao_id)
    context = {'funcao': funcao, 'acao': 'consultar', 'model_verbose_name': 'Função', 'modo_detalhe': True}
    return render(request, 'admin_area/tpl_funcoes.html', context)


@login_required
@admin_required
def excluir_funcao(request, funcao_id):
    funcao = get_object_or_404(TBFUNCAO, FUN_id=funcao_id)
    if request.method == 'POST':
        funcao.delete()
        return redirect(URL_FUNCOES_CRUD_MAIS)
    context = {
        'funcao': funcao, 'acao': 'excluir', 'model_verbose_name': 'Função',
        'next_url': request.META.get('HTTP_REFERER') or reverse(URL_FUNCOES_CRUD_MAIS), 'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_funcoes.html', context)


@login_required
@admin_required
def dashboard_funcoes(request):
    context = {'total_funcoes': TBFUNCAO.objects.count()}
    return render(request, 'admin_area/dashboard_funcoes.html', context)
