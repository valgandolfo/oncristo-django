from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.generic import DetailView
from functools import wraps

# Imports dos models e forms
from ...models.area_admin.models_funcoes import TBFUNCAO
from ...forms.area_admin.forms_funcoes import FuncaoForm

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
def listar_funcoes(request):
    """
    Lista todas as funções com paginação
    """
    
    # Parâmetros de busca
    busca_nome = request.GET.get('busca_nome', '').strip()
    
    # Controla se o usuário já executou uma busca (preencheu algum filtro ou navegou na paginação)
    busca_realizada = bool(busca_nome or request.GET.get('page'))
    
    # Só carrega os registros no grid DEPOIS que o usuário aplicar um filtro
    if busca_realizada:
        funcoes = TBFUNCAO.objects.all().order_by('FUN_nome_funcao')
        
        # Aplicar filtros - se digitar "todos", lista todos sem filtro
        if busca_nome and busca_nome.lower() not in ['todos', 'todas']:
            funcoes = funcoes.filter(FUN_nome_funcao__icontains=busca_nome)
    else:
        # Queryset vazio até que o usuário faça a primeira busca
        funcoes = TBFUNCAO.objects.none()
    
    # Paginação
    paginator = Paginator(funcoes, 10)  # 10 funções por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    total_funcoes = TBFUNCAO.objects.count()
    
    context = {
        'page_title': 'Cadastro de Funções',
        'funcoes': page_obj,
        'page_obj': page_obj,
        'total_funcoes': total_funcoes,
        'modo_dashboard': True,
        'busca_realizada': busca_realizada,
        'busca_nome': busca_nome,
    }
    
    return render(request, 'admin_area/tpl_funcoes.html', context)


@login_required
@admin_required
def criar_funcao(request):
    """
    Cria uma nova função
    """
    from django.urls import reverse
    
    if request.method == 'POST':
        form = FuncaoForm(request.POST)
        if form.is_valid():
            funcao = form.save()
            return redirect('app_igreja:listar_funcoes')
    else:
        form = FuncaoForm()
    
    next_url = request.META.get('HTTP_REFERER', reverse('app_igreja:listar_funcoes'))
    
    context = {
        'form': form,
        'funcao': None,
        'acao': 'incluir',
        'model_verbose_name': 'Função',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_funcoes.html', context)


@login_required
@admin_required
def editar_funcao(request, funcao_id):
    """
    Edita uma função existente
    """
    from django.urls import reverse
    
    funcao = get_object_or_404(TBFUNCAO, FUN_id=funcao_id)
    
    if request.method == 'POST':
        form = FuncaoForm(request.POST, instance=funcao)
        if form.is_valid():
            funcao = form.save()
            return redirect('app_igreja:listar_funcoes')
    else:
        form = FuncaoForm(instance=funcao)
    
    next_url = request.META.get('HTTP_REFERER', reverse('app_igreja:listar_funcoes'))
    
    context = {
        'form': form,
        'funcao': funcao,
        'acao': 'editar',
        'model_verbose_name': 'Função',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_funcoes.html', context)


@login_required
@admin_required
def detalhar_funcao(request, funcao_id):
    """
    Visualiza os detalhes de uma função
    """
    funcao = get_object_or_404(TBFUNCAO, FUN_id=funcao_id)
    
    context = {
        'funcao': funcao,
        'acao': 'consultar',
        'model_verbose_name': 'Função',
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_funcoes.html', context)


@login_required
@admin_required
def excluir_funcao(request, funcao_id):
    """
    Exclui uma função
    """
    from django.urls import reverse
    
    funcao = get_object_or_404(TBFUNCAO, FUN_id=funcao_id)
    
    if request.method == 'POST':
        funcao.delete()
        return redirect('app_igreja:listar_funcoes')
    
    next_url = request.META.get('HTTP_REFERER', reverse('app_igreja:listar_funcoes'))
    
    context = {
        'funcao': funcao,
        'acao': 'excluir',
        'model_verbose_name': 'Função',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_funcoes.html', context)


@login_required
@admin_required
def dashboard_funcoes(request):
    """
    Dashboard com estatísticas das funções
    """
    
    # Estatísticas básicas
    total_funcoes = TBFUNCAO.objects.count()
    
    context = {
        'total_funcoes': total_funcoes,
    }
    
    return render(request, 'admin_area/dashboard_funcoes.html', context)
