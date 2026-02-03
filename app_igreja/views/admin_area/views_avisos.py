from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from ...forms.area_admin.forms_avisos import AvisoForm
from ...models.area_admin.models_avisos import TBAVISO

URL_LISTAR_AVISOS = 'app_igreja:listar_avisos'


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


def _redirect_listar_avisos():
    return redirect(URL_LISTAR_AVISOS)


@login_required
@admin_required
def listar_avisos(request):
    busca_titulo = request.GET.get('busca_titulo', '').strip()
    
    # Controla se o usuário já executou uma busca (preencheu algum filtro ou navegou na paginação)
    busca_realizada = bool(busca_titulo or request.GET.get('page'))
    
    if busca_realizada:
        avisos = TBAVISO.objects.all().order_by('-AVI_data', 'AVI_titulo')
        if busca_titulo and busca_titulo.lower() not in ('todos', 'todas'):
            avisos = avisos.filter(AVI_titulo__icontains=busca_titulo)
    else:
        avisos = TBAVISO.objects.none()
    
    paginator = Paginator(avisos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'modo_dashboard': True,
        'busca_realizada': busca_realizada,
        'busca_titulo': busca_titulo,
    }
    return render(request, 'admin_area/tpl_avisos.html', context)


@login_required
@admin_required
def criar_aviso(request):
    if request.method == 'POST':
        form = AvisoForm(request.POST)
        if form.is_valid():
            form.save()
            return _redirect_listar_avisos()
    else:
        form = AvisoForm()
    context = {
        'form': form, 'acao': 'incluir', 'model_verbose_name': 'Aviso',
        'next_url': request.META.get('HTTP_REFERER') or reverse(URL_LISTAR_AVISOS), 'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_avisos.html', context)


@login_required
@admin_required
def editar_aviso(request, aviso_id):
    aviso = get_object_or_404(TBAVISO, pk=aviso_id)
    if request.method == 'POST':
        form = AvisoForm(request.POST, instance=aviso)
        if form.is_valid():
            form.save()
            return _redirect_listar_avisos()
    else:
        form = AvisoForm(instance=aviso)
    context = {
        'form': form, 'aviso': aviso, 'acao': 'editar', 'model_verbose_name': 'Aviso',
        'next_url': request.META.get('HTTP_REFERER') or reverse(URL_LISTAR_AVISOS), 'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_avisos.html', context)


@login_required
@admin_required
def detalhar_aviso(request, aviso_id):
    aviso = get_object_or_404(TBAVISO, pk=aviso_id)
    acao = request.GET.get('acao', 'consultar')
    if acao == 'excluir' and request.method == 'POST':
        aviso.delete()
        return _redirect_listar_avisos()
    context = {
        'aviso': aviso, 'acao': acao, 'modo_detalhe': True, 'model_verbose_name': 'Aviso',
        'next_url': request.GET.get('next', reverse(URL_LISTAR_AVISOS)),
    }
    return render(request, 'admin_area/tpl_avisos.html', context)


@login_required
@admin_required
def excluir_aviso(request, aviso_id):
    aviso = get_object_or_404(TBAVISO, pk=aviso_id)
    if request.method == 'POST':
        aviso.delete()
        return _redirect_listar_avisos()
    context = {
        'aviso': aviso, 'acao': 'excluir', 'model_verbose_name': 'Aviso',
        'next_url': request.META.get('HTTP_REFERER') or reverse(URL_LISTAR_AVISOS), 'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_avisos.html', context)
