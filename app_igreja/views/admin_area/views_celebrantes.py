"""CRUD de Celebrantes (TBCELEBRANTES) - listar, criar, editar, detalhar, excluir."""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from ...forms.area_admin.forms_celebrantes import CelebranteForm
from ...models.area_admin.models_celebrantes import TBCELEBRANTES

URL_CELEBRANTES_CRUD_MAIS = 'app_igreja:celebrantes_crud_mais'


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
def listar_celebrantes(request):
    query = request.GET.get('busca_nome', '').strip()
    ordenacao_filter = request.GET.get('busca_ordenacao', '').strip()
    ativo_filter = request.GET.get('filtro_ativo', '').strip()
    busca_realizada = bool(query or ordenacao_filter or ativo_filter or request.GET.get('page'))
    if busca_realizada:
        celebrantes = TBCELEBRANTES.objects.all()
        if query and query.lower() not in ('todos', 'todas'):
            celebrantes = celebrantes.filter(CEL_nome_celebrante__icontains=query)
        if query.lower() not in ('todos', 'todas'):
            if ordenacao_filter:
                celebrantes = celebrantes.filter(CEL_ordenacao=ordenacao_filter)
            if ativo_filter != '':
                celebrantes = celebrantes.filter(CEL_ativo=(ativo_filter == '1'))
    else:
        celebrantes = TBCELEBRANTES.objects.none()
    celebrantes = celebrantes.order_by('CEL_ordenacao', 'CEL_nome_celebrante')
    paginator = Paginator(celebrantes, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'page_obj': page_obj,
        'query': query,
        'ordenacao_filter': ordenacao_filter,
        'ativo_filter': ativo_filter,
        'total_celebrantes': TBCELEBRANTES.objects.count(),
        'modo_dashboard': True,
        'busca_realizada': busca_realizada,
    }
    return render(request, 'admin_area/tpl_celebrantes.html', context)


@login_required
@admin_required
def criar_celebrante(request):
    if request.method == 'POST':
        form = CelebranteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(URL_CELEBRANTES_CRUD_MAIS)
        messages.error(request, 'Erro ao criar celebrante. Verifique os campos.')
    else:
        form = CelebranteForm()
    context = {
        'form': form, 'acao': 'incluir', 'model_verbose_name': 'Celebrante', 'modo_criacao': True,
        'next_url': request.META.get('HTTP_REFERER') or reverse(URL_CELEBRANTES_CRUD_MAIS), 'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_celebrantes.html', context)


@login_required
@admin_required
def editar_celebrante(request, celebrante_id):
    celebrante = get_object_or_404(TBCELEBRANTES, CEL_id=celebrante_id)
    if request.method == 'POST':
        form = CelebranteForm(request.POST, request.FILES, instance=celebrante)
        if form.is_valid():
            form.save()
            return redirect(URL_CELEBRANTES_CRUD_MAIS)
        messages.error(request, 'Erro ao atualizar celebrante. Verifique os campos.')
    else:
        form = CelebranteForm(instance=celebrante)
    context = {
        'form': form, 'celebrante': celebrante, 'acao': 'editar', 'model_verbose_name': 'Celebrante', 'modo_edicao_crud': True,
        'next_url': request.META.get('HTTP_REFERER') or reverse(URL_CELEBRANTES_CRUD_MAIS), 'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_celebrantes.html', context)


@login_required
@admin_required
def detalhar_celebrante(request, celebrante_id):
    celebrante = get_object_or_404(TBCELEBRANTES, CEL_id=celebrante_id)
    context = {'celebrante': celebrante, 'acao': 'consultar', 'model_verbose_name': 'Celebrante', 'modo_visualizacao_crud': True, 'modo_detalhe': True}
    return render(request, 'admin_area/tpl_celebrantes.html', context)


@login_required
@admin_required
def excluir_celebrante(request, celebrante_id):
    celebrante = get_object_or_404(TBCELEBRANTES, CEL_id=celebrante_id)
    if request.method == 'POST':
        celebrante.delete()
        return redirect(URL_CELEBRANTES_CRUD_MAIS)
    context = {
        'celebrante': celebrante, 'acao': 'excluir', 'model_verbose_name': 'Celebrante',
        'next_url': request.META.get('HTTP_REFERER') or reverse(URL_CELEBRANTES_CRUD_MAIS), 'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_celebrantes.html', context)
