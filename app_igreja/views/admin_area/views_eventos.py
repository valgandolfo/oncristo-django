from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from datetime import datetime, timedelta, date


from app_igreja.models.area_admin.models_eventos import TBEVENTO, TBITEM_EVENTO
from app_igreja.forms.area_admin.forms_eventos import EventoForm, ItemEventoForm


@login_required
def listar_eventos(request):
    """
    Lista todos os eventos com paginação e busca
    """
    # Parâmetros de busca
    busca = request.GET.get('busca', '')
    status = request.GET.get('status', '')
    
    # Query base
    eventos = TBEVENTO.objects.all().order_by('-EVE_DTCADASTRO')
    
    # Filtros
    if busca:
        eventos = eventos.filter(
            Q(EVE_TITULO__icontains=busca)
        )
    
    if status:
        eventos = eventos.filter(EVE_STATUS=status)
    
    # Paginação
    paginator = Paginator(eventos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    total_eventos = TBEVENTO.objects.count()
    ativos = TBEVENTO.objects.filter(EVE_STATUS='Ativo').count()
    inativos = TBEVENTO.objects.filter(EVE_STATUS='Inativo').count()
    
    # Eventos recentes (últimos 5)
    eventos_recentes = TBEVENTO.objects.filter(
        EVE_STATUS='Ativo'
    ).order_by('-EVE_DTCADASTRO')[:5]
    
    # Eventos do mês atual
    hoje = date.today()
    eventos_mes = TBEVENTO.objects.filter(
        EVE_DTCADASTRO__year=hoje.year,
        EVE_DTCADASTRO__month=hoje.month
    ).count()
    
    context = {
        'page_obj': page_obj,
        'busca': busca,
        'status': status,
        'total_eventos': total_eventos,
        'ativos': ativos,
        'inativos': inativos,
        'eventos_recentes': eventos_recentes,
        'eventos_mes': eventos_mes,
        'modo_dashboard': True,  # Migrado para nova tela pai dashboard
        'model_verbose_name': 'Evento',
    }
    
    return render(request, 'admin_area/tpl_eventos.html', context)


@login_required
def criar_evento(request):
    """
    Cria um novo evento
    """
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            evento = form.save()
            messages.success(request, 'Evento criado com sucesso!')
            return redirect('app_igreja:listar_eventos')
    else:
        form = EventoForm()
    
    # Usar HTTP_REFERER como fallback, igual ao dizimistas
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_eventos')
    
    context = {
        'form': form,
        'acao': 'incluir',
        'model_verbose_name': 'Evento',
        'next_url': next_url,
        'modo_detalhe': True,
        'eventos_section': 'detail',  # Seção: CRUD básico
    }
    
    return render(request, 'admin_area/tpl_eventos.html', context)


@login_required
def detalhar_evento(request, evento_id):
    """
    Visualiza os detalhes de um evento
    """
    evento = get_object_or_404(TBEVENTO, EVE_ID=evento_id)
    
    # Usar HTTP_REFERER como fallback, igual ao dizimistas
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_eventos')
    
    context = {
        'evento': evento,
        'acao': 'consultar',
        'model_verbose_name': 'Evento',
        'next_url': next_url,
        'modo_detalhe': True,
        'eventos_section': 'detail',  # Seção: CRUD básico
    }
    
    return render(request, 'admin_area/tpl_eventos.html', context)


@login_required
def editar_evento(request, evento_id):
    """
    Edita um evento existente
    """
    evento = get_object_or_404(TBEVENTO, EVE_ID=evento_id)
    
    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento atualizado com sucesso!')
            return redirect('app_igreja:listar_eventos')
    else:
        form = EventoForm(instance=evento)
    
    # Usar HTTP_REFERER como fallback, igual ao dizimistas
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_eventos')
    
    context = {
        'form': form,
        'evento': evento,
        'acao': 'editar',
        'model_verbose_name': 'Evento',
        'next_url': next_url,
        'modo_detalhe': True,
        'eventos_section': 'detail',  # Seção: CRUD básico
    }
    
    return render(request, 'admin_area/tpl_eventos.html', context)


@login_required
def excluir_evento(request, evento_id):
    """
    Exclui um evento
    """
    evento = get_object_or_404(TBEVENTO, EVE_ID=evento_id)
    
    if request.method == 'POST':
        evento.delete()
        messages.success(request, 'Evento excluído com sucesso!')
        return redirect('app_igreja:listar_eventos')
    
    # Usar HTTP_REFERER como fallback, igual ao dizimistas
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_eventos')
    
    context = {
        'evento': evento,
        'acao': 'excluir',
        'model_verbose_name': 'Evento',
        'next_url': next_url,
        'modo_detalhe': True,
        'eventos_section': 'detail',  # Seção: CRUD básico
    }
    
    return render(request, 'admin_area/tpl_eventos.html', context)


# ==================== VIEWS DE ITENS DE EVENTO ====================

@login_required
def listar_itens_evento(request, evento_id=None):
    """
    Lista todos os itens de evento, opcionalmente filtrados por evento específico
    """
    # Se evento_id foi fornecido, filtrar por esse evento
    if evento_id:
        evento = get_object_or_404(TBEVENTO, EVE_ID=evento_id)
        itens = TBITEM_EVENTO.objects.filter(ITEM_EVE_EVENTO=evento).order_by('ITEM_EVE_DATA_INICIAL', 'ITEM_EVE_HORA_INICIAL')
        titulo = f'Itens do Evento: {evento.EVE_TITULO}'
    else:
        evento = None
        itens = TBITEM_EVENTO.objects.all().order_by('ITEM_EVE_EVENTO', 'ITEM_EVE_DATA_INICIAL', 'ITEM_EVE_HORA_INICIAL')
        titulo = 'Itens dos Eventos'
    
    # Parâmetros de busca
    busca = request.GET.get('busca', '')
    
    # Filtros
    if busca:
        itens = itens.filter(
            Q(ITEM_EVE_EVENTO__EVE_TITULO__icontains=busca)
        )
    
    # Paginação
    paginator = Paginator(itens, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    total_itens = itens.count()
    
    context = {
        'page_obj': page_obj,
        'busca': busca,
        'total_itens': total_itens,
        'evento': evento,
        'titulo': titulo,
        'modo_dashboard': True,
        'model_verbose_name': 'Item do Evento',
        'eventos_section': 'item_list',  # Seção de listagem de itens
    }
    
    return render(request, 'admin_area/tpl_eventos.html', context)


@login_required
def criar_item_evento(request, evento_id=None):
    """
    Cria um novo item de evento
    Se evento_id for fornecido, pré-seleciona o evento
    """
    if request.method == 'POST':
        form = ItemEventoForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(request, 'Item do evento criado com sucesso!')
            if evento_id:
                return redirect('app_igreja:listar_itens_evento', evento_id=evento_id)
            return redirect('app_igreja:listar_itens_evento')
    else:
        initial = {}
        if evento_id:
            evento = get_object_or_404(TBEVENTO, EVE_ID=evento_id)
            initial['ITEM_EVE_EVENTO'] = evento
        form = ItemEventoForm(initial=initial)
    
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_itens_evento')
    
    context = {
        'form': form,
        'acao': 'incluir',
        'model_verbose_name': 'Item do Evento',
        'next_url': next_url,
        'modo_detalhe': True,
        'evento_id': evento_id,
        'eventos_section': 'item_detail',  # Seção de detalhe de item
    }
    
    return render(request, 'admin_area/tpl_eventos.html', context)


@login_required
def detalhar_item_evento(request, item_id):
    """
    Visualiza os detalhes de um item de evento
    """
    item = get_object_or_404(TBITEM_EVENTO, ITEM_EVE_ID=item_id)
    
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_itens_evento')
    
    context = {
        'item': item,
        'acao': 'consultar',
        'model_verbose_name': 'Item do Evento',
        'next_url': next_url,
        'modo_detalhe': True,
        'eventos_section': 'item_detail',  # Seção de detalhe de item
    }
    
    return render(request, 'admin_area/tpl_eventos.html', context)


@login_required
def editar_item_evento(request, item_id):
    """
    Edita um item de evento existente
    """
    item = get_object_or_404(TBITEM_EVENTO, ITEM_EVE_ID=item_id)
    
    if request.method == 'POST':
        form = ItemEventoForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item do evento atualizado com sucesso!')
            return redirect('app_igreja:listar_itens_evento', evento_id=item.ITEM_EVE_EVENTO.EVE_ID)
    else:
        form = ItemEventoForm(instance=item)
    
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_itens_evento')
    
    context = {
        'form': form,
        'item': item,
        'acao': 'editar',
        'model_verbose_name': 'Item do Evento',
        'next_url': next_url,
        'modo_detalhe': True,
        'eventos_section': 'item_detail',  # Seção de detalhe de item
    }
    
    return render(request, 'admin_area/tpl_eventos.html', context)


@login_required
def excluir_item_evento(request, item_id):
    """
    Exclui um item de evento
    """
    item = get_object_or_404(TBITEM_EVENTO, ITEM_EVE_ID=item_id)
    evento_id = item.ITEM_EVE_EVENTO.EVE_ID
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item do evento excluído com sucesso!')
        return redirect('app_igreja:listar_itens_evento', evento_id=evento_id)
    
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_itens_evento')
    
    context = {
        'item': item,
        'acao': 'excluir',
        'model_verbose_name': 'Item do Evento',
        'next_url': next_url,
        'modo_detalhe': True,
        'eventos_section': 'item_detail',  # Seção de detalhe de item
    }
    
    return render(request, 'admin_area/tpl_eventos.html', context)

