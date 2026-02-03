from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import reverse
from functools import wraps

from ...models.area_admin.models_colaboradores import TBCOLABORADORES
from ...forms.area_admin.forms_colaboradores import ColaboradorForm
from ...utils import reconstruir_url_com_filtros

FILTROS_COLABORADORES = ['busca_telefone', 'busca_nome', 'busca_apelido', 'busca_status', 'page']


def _redirect_listar_colaboradores(request):
    """Redirect para listagem preservando filtros do POST."""
    return redirect(reconstruir_url_com_filtros(request, 'app_igreja:listar_colaboradores', FILTROS_COLABORADORES))


def admin_required(view_func):
    """Decorator para verificar se o usuário é administrador"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, 'Acesso negado. Apenas administradores podem acessar esta área.')
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_required
@admin_required
def listar_colaboradores(request):
    """
    Lista colaboradores (padrão PAI-filho): suporta busca e status, com paginação
    """
    # Filtros específicos conforme solicitado
    busca_telefone = request.GET.get('busca_telefone', '').strip()
    busca_nome = request.GET.get('busca_nome', '').strip()
    busca_apelido = request.GET.get('busca_apelido', '').strip()
    busca_status = request.GET.get('busca_status', '').strip()

    # Controla se o usuário já executou uma busca (preencheu algum filtro ou navegou na paginação)
    busca_realizada = bool(
        busca_telefone or busca_nome or busca_apelido or busca_status or request.GET.get('page')
    )

    # Só carrega os registros no grid DEPOIS que o usuário aplicar um filtro
    if busca_realizada:
        colaboradores_qs = TBCOLABORADORES.objects.all()

        # Se digitar "todos" ou "todas" no nome, ignora outros filtros e traz tudo
        if busca_nome.lower() in ['todos', 'todas']:
            # Mantém todos os registros sem filtros adicionais
            pass
        else:
            # Aplicar filtros normais
            if busca_telefone:
                colaboradores_qs = colaboradores_qs.filter(COL_telefone__icontains=busca_telefone)
            
            if busca_nome:
                colaboradores_qs = colaboradores_qs.filter(COL_nome_completo__icontains=busca_nome)
            
            if busca_apelido:
                colaboradores_qs = colaboradores_qs.filter(COL_apelido__icontains=busca_apelido)
            
            if busca_status:
                colaboradores_qs = colaboradores_qs.filter(COL_status=busca_status)
    else:
        # Queryset vazio até que o usuário faça a primeira busca
        colaboradores_qs = TBCOLABORADORES.objects.none()

    # Estatísticas para o painel (considerando apenas o queryset atual)
    ativos = colaboradores_qs.filter(COL_status='ATIVO').count()
    inativos = colaboradores_qs.filter(COL_status='INATIVO').count()
    total_colaboradores = colaboradores_qs.count()

    # Paginação
    paginator = Paginator(colaboradores_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'colaboradores': page_obj,  # compat com template atual
        'total_colaboradores': total_colaboradores,
        'ativos': ativos,
        'inativos': inativos,
        # flags novo padrão
        'modo_dashboard': True,
        'busca_telefone': busca_telefone,
        'busca_nome': busca_nome,
        'busca_apelido': busca_apelido,
        'busca_status': busca_status,
        'busca_realizada': busca_realizada,
        'model_verbose_name_plural': 'Colaboradores',
    }

    return render(request, 'admin_area/tpl_colaboradores.html', context)

@login_required
@admin_required
def criar_colaborador(request):
    """
    Cria um novo colaborador
    """
    
    if request.method == 'POST':
        form = ColaboradorForm(request.POST, request.FILES)
        
        if form.is_valid():
            form.save()
            return _redirect_listar_colaboradores(request)
    else:
        form = ColaboradorForm()

    next_url = request.META.get('HTTP_REFERER')
    context = {
        'form': form,
        'titulo': 'Criar Novo Colaborador',
        # novo padrão PAI-filho
        'acao': 'incluir',
        'model_verbose_name': 'Colaborador',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_colaboradores.html', context)

@login_required
@admin_required
def editar_colaborador(request, colaborador_id):
    """
    Edita um colaborador existente
    """
    colaborador = get_object_or_404(TBCOLABORADORES, COL_id=colaborador_id)
    
    if request.method == 'POST':
        form = ColaboradorForm(request.POST, request.FILES, instance=colaborador)
        
        if form.is_valid():
            form.save()
            return _redirect_listar_colaboradores(request)
    else:
        form = ColaboradorForm(instance=colaborador)

    next_url = request.META.get('HTTP_REFERER')
    context = {
        'form': form,
        'colaborador': colaborador,
        'titulo': f'Editar Colaborador: {colaborador.COL_nome_completo}',
        # novo padrão PAI-filho
        'acao': 'editar',
        'model_verbose_name': 'Colaborador',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_colaboradores.html', context)

@login_required
@admin_required
def detalhar_colaborador(request, colaborador_id):
    """
    Mostra detalhes de um colaborador
    """
    colaborador = get_object_or_404(TBCOLABORADORES, COL_id=colaborador_id)
    context = {
        'colaborador': colaborador,
        'titulo': f'Detalhes do Colaborador: {colaborador.COL_nome_completo}',
        # compat atual
        'modo_detalhes': True,
        # novo padrão PAI-filho
        'acao': 'consultar',
        'model_verbose_name': 'Colaborador',
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_colaboradores.html', context)

@login_required
@admin_required
def excluir_colaborador(request, colaborador_id):
    """
    Exclui um colaborador
    """
    colaborador = get_object_or_404(TBCOLABORADORES, COL_id=colaborador_id)
    
    if request.method == 'POST':
        colaborador.delete()
        return _redirect_listar_colaboradores(request)

    next_url = request.META.get('HTTP_REFERER')
    context = {
        'colaborador': colaborador,
        'titulo': f'Excluir Colaborador: {colaborador.COL_nome_completo}',
        # compat atual
        'modo_exclusao': True,
        # novo padrão PAI-filho
        'acao': 'excluir',
        'model_verbose_name': 'Colaborador',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_colaboradores.html', context)
