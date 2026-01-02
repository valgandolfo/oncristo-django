from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.generic import DetailView
from functools import wraps

# Imports dos models e forms
from ...models.area_admin.models_celebrantes import TBCELEBRANTES
from ...forms.area_admin.forms_celebrantes import CelebranteForm

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
def listar_celebrantes(request):
    """
    Lista todos os celebrantes com paginação
    """
    
    # Busca
    query = request.GET.get('busca_nome', '').strip()
    ordenacao_filter = request.GET.get('busca_ordenacao', '').strip()
    ativo_filter = request.GET.get('filtro_ativo', '').strip()
    
    # Controla se o usuário já executou uma busca (preencheu algum filtro ou navegou na paginação)
    busca_realizada = bool(query or ordenacao_filter or ativo_filter or request.GET.get('page'))
    
    # Só carrega os registros no grid DEPOIS que o usuário aplicar um filtro
    if busca_realizada:
        celebrantes = TBCELEBRANTES.objects.all()
        
        # Aplicar filtros - se digitar "todos", lista todos sem filtro de nome
        if query and query.lower() not in ['todos', 'todas']:
            celebrantes = celebrantes.filter(CEL_nome_celebrante__icontains=query)
        
        # Outros filtros só aplicam se NÃO for "todos"
        if query.lower() not in ['todos', 'todas']:
            if ordenacao_filter:
                celebrantes = celebrantes.filter(CEL_ordenacao=ordenacao_filter)
                
            if ativo_filter != '':
                ativo_bool = ativo_filter == '1'
                celebrantes = celebrantes.filter(CEL_ativo=ativo_bool)
        
        # Ordenação final
        celebrantes = celebrantes.order_by('CEL_ordenacao', 'CEL_nome_celebrante')
    else:
        # Queryset vazio até que o usuário faça a primeira busca
        celebrantes = TBCELEBRANTES.objects.none()
        
    # Ordenação final
    celebrantes = celebrantes.order_by('CEL_ordenacao', 'CEL_nome_celebrante')
    
    # Paginação
    paginator = Paginator(celebrantes, 10)  # 10 celebrantes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'celebrantes': page_obj,
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
    """
    Cria um novo celebrante
    """
    
    if request.method == 'POST':
        form = CelebranteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Redirecionar para lista de celebrantes
            return redirect('app_igreja:listar_celebrantes')
        else:
            messages.error(request, 'Erro ao criar celebrante. Verifique os campos.')
    else:
        form = CelebranteForm()
    
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_celebrantes')
    context = {
        'form': form,
        'acao': 'incluir',
        'model_verbose_name': 'Celebrante',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_celebrantes.html', context)

@login_required
@admin_required
def editar_celebrante(request, celebrante_id):
    """
    Edita um celebrante existente
    """
    
    celebrante = get_object_or_404(TBCELEBRANTES, CEL_id=celebrante_id)
    
    if request.method == 'POST':
        form = CelebranteForm(request.POST, request.FILES, instance=celebrante)
        if form.is_valid():
            form.save()
            # Redirecionar para lista de celebrantes
            return redirect('app_igreja:listar_celebrantes')
        else:
            messages.error(request, 'Erro ao atualizar celebrante. Verifique os campos.')
    else:
        form = CelebranteForm(instance=celebrante)
    
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_celebrantes')
    context = {
        'form': form,
        'celebrante': celebrante,
        'acao': 'editar',
        'model_verbose_name': 'Celebrante',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_celebrantes.html', context)

@login_required
@admin_required
def detalhar_celebrante(request, celebrante_id):
    """
    Mostra detalhes de um celebrante
    """
    
    celebrante = get_object_or_404(TBCELEBRANTES, CEL_id=celebrante_id)
    
    context = {
        'celebrante': celebrante,
        'acao': 'consultar',
        'model_verbose_name': 'Celebrante',
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_celebrantes.html', context)

@login_required
@admin_required
def excluir_celebrante(request, celebrante_id):
    """
    Exclui um celebrante
    """
    
    celebrante = get_object_or_404(TBCELEBRANTES, CEL_id=celebrante_id)
    
    if request.method == 'POST':
        celebrante.delete()
        # Redirecionar para lista após exclusão
        return redirect('app_igreja:listar_celebrantes')
    
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_celebrantes')
    context = {
        'celebrante': celebrante,
        'acao': 'excluir',
        'model_verbose_name': 'Celebrante',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_celebrantes.html', context)


# Revertido: removida a Viewdad genérica de Celebrantes
