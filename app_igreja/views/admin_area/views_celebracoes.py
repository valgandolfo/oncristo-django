from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta

from app_igreja.models.area_admin.models_celebracoes import TBCELEBRACOES
from app_igreja.forms.area_admin.forms_celebracoes import CelebracaoForm

@login_required
def listar_celebracoes(request):
    """
    Lista todas as celebrações com filtros e paginação
    """
    # Filtros
    busca_nome = request.GET.get('busca_nome', '').strip()
    filtro_status = request.GET.get('status', '').strip()
    filtro_data_inicio = request.GET.get('data_inicio', '').strip()
    filtro_data_fim = request.GET.get('data_fim', '').strip()
    
    # Controla se o usuário já executou uma busca (preencheu algum filtro ou navegou na paginação)
    busca_realizada = bool(busca_nome or filtro_status or filtro_data_inicio or filtro_data_fim or request.GET.get('page'))
    
    # Só carrega os registros no grid DEPOIS que o usuário aplicar um filtro
    if busca_realizada:
        # Query base
        celebracoes = TBCELEBRACOES.objects.all()
        
        # Aplicar filtros
        if busca_nome:
            celebracoes = celebracoes.filter(
                Q(CEL_nome_solicitante__icontains=busca_nome) |
                Q(CEL_tipo_celebracao__icontains=busca_nome) |
                Q(CEL_local__icontains=busca_nome)
            )
        
        if filtro_status:
            celebracoes = celebracoes.filter(CEL_status=filtro_status)
        
        if filtro_data_inicio:
            celebracoes = celebracoes.filter(CEL_data_celebracao__gte=filtro_data_inicio)
        
        if filtro_data_fim:
            celebracoes = celebracoes.filter(CEL_data_celebracao__lte=filtro_data_fim)
        
        # Ordenação
        celebracoes = celebracoes.order_by('CEL_data_celebracao', 'CEL_horario')
    else:
        # Queryset vazio até que o usuário faça a primeira busca
        celebracoes = TBCELEBRACOES.objects.none()
    
    # Paginação
    paginator = Paginator(celebracoes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    total_celebracoes = TBCELEBRACOES.objects.count()
    pendentes = TBCELEBRACOES.objects.filter(CEL_status='pendente').count()
    confirmadas = TBCELEBRACOES.objects.filter(CEL_status='confirmada').count()
    realizadas = TBCELEBRACOES.objects.filter(CEL_status='realizada').count()
    canceladas = TBCELEBRACOES.objects.filter(CEL_status='cancelada').count()
    
    # Próximas celebrações (próximos 7 dias)
    data_limite = date.today() + timedelta(days=7)
    proximas_celebracoes = TBCELEBRACOES.objects.filter(
        CEL_data_celebracao__gte=date.today(),
        CEL_data_celebracao__lte=data_limite,
        CEL_status__in=['pendente', 'confirmada']
    ).order_by('CEL_data_celebracao', 'CEL_horario')[:5]
    
    context = {
        'page_obj': page_obj,
        'busca_nome': busca_nome,
        'filtro_status': filtro_status,
        'filtro_data_inicio': filtro_data_inicio,
        'filtro_data_fim': filtro_data_fim,
        'total_celebracoes': total_celebracoes,
        'pendentes': pendentes,
        'confirmadas': confirmadas,
        'realizadas': realizadas,
        'canceladas': canceladas,
        'proximas_celebracoes': proximas_celebracoes,
        'modo_dashboard': True,  # Migrado para nova tela pai dashboard
        'busca_realizada': busca_realizada,
    }
    
    return render(request, 'admin_area/tpl_celebracoes.html', context)

@login_required
def criar_celebracao(request):
    """
    Cria uma nova celebração
    """
    if request.method == 'POST':
        form = CelebracaoForm(request.POST)
        if form.is_valid():
            try:
                celebracao = form.save()
                messages.success(request, 'Celebração cadastrada com sucesso!')
                return redirect('app_igreja:listar_celebracoes')
            except Exception as e:
                messages.error(request, f'Erro ao salvar celebração: {str(e)}')
        else:
            # Se o formulário não é válido, mostrar erros
            messages.error(request, 'Por favor, corrija os erros no formulário.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CelebracaoForm()
    
    next_url = request.META.get('HTTP_REFERER', reverse('app_igreja:listar_celebracoes'))
    
    context = {
        'form': form,
        'acao': 'incluir',
        'model_verbose_name': 'Celebração',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_celebracoes.html', context)

@login_required
def detalhar_celebracao(request, celebracao_id):
    """
    Exibe detalhes de uma celebração
    """
    celebracao = get_object_or_404(TBCELEBRACOES, id=celebracao_id)
    
    next_url = request.META.get('HTTP_REFERER', reverse('app_igreja:listar_celebracoes'))
    
    context = {
        'celebracao': celebracao,
        'acao': 'consultar',
        'model_verbose_name': 'Celebração',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_celebracoes.html', context)

@login_required
def editar_celebracao(request, celebracao_id):
    """
    Edita uma celebração existente
    """
    celebracao = get_object_or_404(TBCELEBRACOES, id=celebracao_id)
    
    if request.method == 'POST':
        form = CelebracaoForm(request.POST, instance=celebracao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Celebração atualizada com sucesso!')
            return redirect('app_igreja:detalhar_celebracao', celebracao_id=celebracao.id)
    else:
        form = CelebracaoForm(instance=celebracao)
    
    next_url = request.META.get('HTTP_REFERER', reverse('app_igreja:listar_celebracoes'))
    
    context = {
        'form': form,
        'celebracao': celebracao,
        'acao': 'editar',
        'model_verbose_name': 'Celebração',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_celebracoes.html', context)

@login_required
def excluir_celebracao(request, celebracao_id):
    """
    Exclui uma celebração
    """
    celebracao = get_object_or_404(TBCELEBRACOES, id=celebracao_id)
    
    if request.method == 'POST':
        celebracao.delete()
        messages.success(request, 'Celebração excluída com sucesso!')
        return redirect('app_igreja:listar_celebracoes')
    
    next_url = request.META.get('HTTP_REFERER', reverse('app_igreja:listar_celebracoes'))
    
    context = {
        'celebracao': celebracao,
        'acao': 'excluir',
        'model_verbose_name': 'Celebração',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_celebracoes.html', context)
