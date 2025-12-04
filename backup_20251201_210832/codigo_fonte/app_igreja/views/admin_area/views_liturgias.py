from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from functools import wraps

from ...models.area_publica.models_liturgias import TBLITURGIA
from ...forms.area_admin.forms_liturgias import LiturgiaForm

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
def listar_liturgias(request):
    """Lista todas as liturgias com busca e paginação"""
    liturgias = TBLITURGIA.objects.all().order_by('-LIT_DATALIT', 'LIT_TIPOLIT')
    
    # Busca por data ou tipo
    busca_data = request.GET.get('busca_data', '')
    busca_tipo = request.GET.get('busca_tipo', '')
    
    if busca_data:
        liturgias = liturgias.filter(LIT_DATALIT__icontains=busca_data)
    
    if busca_tipo:
        liturgias = liturgias.filter(LIT_TIPOLIT__icontains=busca_tipo)
    
    paginator = Paginator(liturgias, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'modo_dashboard': True,
    }
    return render(request, 'admin_area/tpl_liturgias.html', context)

@login_required
@admin_required
def criar_liturgia(request):
    """Cria uma nova liturgia"""
    if request.method == 'POST':
        form = LiturgiaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Liturgia cadastrada com sucesso!')
            return redirect('app_igreja:listar_liturgias')
    else:
        form = LiturgiaForm()
    
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_liturgias')
    context = {
        'form': form,
        'acao': 'incluir',
        'model_verbose_name': 'Liturgia',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_liturgias.html', context)

@login_required
@admin_required
def editar_liturgia(request, liturgia_id):
    """Edita uma liturgia existente"""
    liturgia = get_object_or_404(TBLITURGIA, pk=liturgia_id)
    
    if request.method == 'POST':
        form = LiturgiaForm(request.POST, instance=liturgia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Liturgia atualizada com sucesso!')
            return redirect('app_igreja:listar_liturgias')
    else:
        form = LiturgiaForm(instance=liturgia)
    
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_liturgias')
    context = {
        'form': form,
        'liturgia': liturgia,
        'acao': 'editar',
        'model_verbose_name': 'Liturgia',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_liturgias.html', context)

@login_required
@admin_required
def detalhar_liturgia(request, liturgia_id):
    """Exibe detalhes de uma liturgia"""
    liturgia = get_object_or_404(TBLITURGIA, pk=liturgia_id)
    acao = request.GET.get('acao', 'consultar')
    
    if acao == 'excluir' and request.method == 'POST':
        liturgia.delete()
        messages.success(request, 'Liturgia excluída com sucesso!')
        return redirect('app_igreja:listar_liturgias')
    
    context = {
        'liturgia': liturgia,
        'acao': acao,
        'modo_detalhe': True,
        'model_verbose_name': 'Liturgia',
        'next_url': request.GET.get('next', reverse('app_igreja:listar_liturgias')),
    }
    return render(request, 'admin_area/tpl_liturgias.html', context)

@login_required
@admin_required
def excluir_liturgia(request, liturgia_id):
    """Exclui uma liturgia"""
    liturgia = get_object_or_404(TBLITURGIA, pk=liturgia_id)
    
    if request.method == 'POST':
        liturgia.delete()
        messages.success(request, 'Liturgia excluída com sucesso!')
        return redirect('app_igreja:listar_liturgias')
    
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_liturgias')
    context = {
        'liturgia': liturgia,
        'acao': 'excluir',
        'model_verbose_name': 'Liturgia',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_liturgias.html', context)

