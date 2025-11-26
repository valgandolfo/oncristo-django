"""
==================== VIEWS DE GERENCIAR ESCALA ====================
Views para CRUD completo de Gerenciar Escala de Missas
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse
from functools import wraps
from datetime import date, datetime
from calendar import monthrange

from ...models.area_admin.models_escala import TBESCALA, TBITEM_ESCALA
from ...models.area_admin.models_colaboradores import TBCOLABORADORES
from ...models.area_admin.models_grupos import TBGRUPOS
from ...forms.area_admin.forms_gerenciar_escala import ItemEscalaForm


def admin_required(view_func):
    """Decorator para verificar se o usuário é administrador"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Apenas superusuários podem acessar área admin
        if not request.user.is_superuser:
            messages.error(request, 'Acesso negado. Apenas administradores podem acessar esta área.')
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_required
@admin_required
def listar_itens_escala(request):
    """
    Lista todos os itens da escala com filtro por mês/ano
    """
    from datetime import date
    
    # Buscar mês/ano da query string
    mes = request.GET.get('mes', '')
    ano = request.GET.get('ano', '')
    
    # Se não tiver mês/ano, usar mês e ano atual como padrão
    if not mes or not ano:
        hoje = date.today()
        mes_atual = hoje.month
        ano_atual = hoje.year
        
        context = {
            'modo_dashboard': True,
            'sem_filtro': True,
            'mes': mes_atual,
            'ano': ano_atual,
        }
        return render(request, 'admin_area/tpl_gerenciar_escala.html', context)
    
    try:
        mes = int(mes)
        ano = int(ano)
        
        # Validar mês e ano
        if mes < 1 or mes > 12:
            messages.error(request, 'Mês inválido. Use valores entre 1 e 12.')
            return redirect('app_igreja:listar_itens_escala')
        
        if ano < 2000 or ano > 2100:
            messages.error(request, 'Ano inválido.')
            return redirect('app_igreja:listar_itens_escala')
        
        # Buscar escala master
        primeiro_dia_mes = date(ano, mes, 1)
        escala_master = TBESCALA.objects.filter(ESC_MESANO=primeiro_dia_mes).first()
        
        if not escala_master:
            messages.info(request, f'Nenhuma escala encontrada para {mes:02d}/{ano}. Gere a escala primeiro.')
            context = {
                'modo_dashboard': True,
                'sem_filtro': True,
                'mes': mes,
                'ano': ano,
            }
            return render(request, 'admin_area/tpl_gerenciar_escala.html', context)
        
        # Buscar itens da escala
        itens = TBITEM_ESCALA.objects.filter(
            ITE_ESC_ESCALA=escala_master
        ).order_by('ITE_ESC_DATA', 'ITE_ESC_HORARIO')
        
        # Organizar por dia para exibição
        dias_semana_pt = {
            0: 'Segunda-feira',
            1: 'Terça-feira',
            2: 'Quarta-feira',
            3: 'Quinta-feira',
            4: 'Sexta-feira',
            5: 'Sábado',
            6: 'Domingo'
        }
        
        meses_pt = [
            '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        
        # Adicionar nome do dia da semana, colaborador e grupo para cada item
        for item in itens:
            item.dia_semana_nome = dias_semana_pt.get(item.ITE_ESC_DATA.weekday(), '')
            
            # Buscar nome do colaborador
            if item.ITE_ESC_COLABORADOR:
                try:
                    colaborador = TBCOLABORADORES.objects.get(COL_id=item.ITE_ESC_COLABORADOR)
                    # Pegar primeiro nome
                    item.colaborador_nome = colaborador.COL_nome_completo.split()[0] if colaborador.COL_nome_completo else '-'
                except TBCOLABORADORES.DoesNotExist:
                    item.colaborador_nome = '-'
            else:
                item.colaborador_nome = '-'
            
            # Buscar nome do grupo
            if item.ITE_ESC_GRUPO:
                try:
                    grupo = TBGRUPOS.objects.get(GRU_id=item.ITE_ESC_GRUPO)
                    item.grupo_nome = grupo.GRU_nome_grupo
                except TBGRUPOS.DoesNotExist:
                    item.grupo_nome = '-'
            else:
                item.grupo_nome = '-'
        
        # Paginação
        paginator = Paginator(itens, 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'escala_master': escala_master,
            'mes': mes,
            'ano': ano,
            'mes_nome': meses_pt[mes],
            'modo_dashboard': True,
        }
        
        return render(request, 'admin_area/tpl_gerenciar_escala.html', context)
        
    except ValueError:
        messages.error(request, 'Mês e ano devem ser números válidos.')
        return redirect('app_igreja:listar_itens_escala')


@login_required
@admin_required
def criar_item_escala(request):
    """
    Cria um novo item da escala
    """
    mes = request.GET.get('mes', '')
    ano = request.GET.get('ano', '')
    
    if not mes or not ano:
        messages.error(request, 'Mês e ano são obrigatórios.')
        return redirect('app_igreja:listar_itens_escala')
    
    try:
        mes = int(mes)
        ano = int(ano)
        primeiro_dia_mes = date(ano, mes, 1)
        escala_master = get_object_or_404(TBESCALA, ESC_MESANO=primeiro_dia_mes)
    except (ValueError, TBESCALA.DoesNotExist):
        messages.error(request, 'Escala não encontrada para o mês/ano informado.')
        return redirect('app_igreja:listar_itens_escala')
    
    if request.method == 'POST':
        form = ItemEscalaForm(request.POST, escala=escala_master, acao='incluir')
        if form.is_valid():
            item = form.save(commit=False)
            item.ITE_ESC_ESCALA = escala_master
            item.save()
            messages.success(request, 'Item da escala criado com sucesso!')
            return redirect(f"{reverse('app_igreja:listar_itens_escala')}?mes={mes}&ano={ano}")
        else:
            messages.error(request, 'Erro ao criar item. Verifique os dados.')
    else:
        form = ItemEscalaForm(escala=escala_master, acao='incluir')
        # Definir data padrão como primeiro dia do mês se não especificada
        if not form.initial.get('ITE_ESC_DATA'):
            form.initial['ITE_ESC_DATA'] = primeiro_dia_mes
    
    dias_semana_pt = {
        0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira', 3: 'Quinta-feira',
        4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo'
    }
    
    context = {
        'form': form,
        'acao': 'incluir',
        'modo_detalhe': True,  # Necessário para o template base renderizar o bloco conteudo_detalhe
        'model_verbose_name': 'Item da Escala',
        'escala_master': escala_master,
        'mes': mes,
        'ano': ano,
        'dias_semana_pt': dias_semana_pt,
    }
    
    return render(request, 'admin_area/tpl_gerenciar_escala.html', context)


@login_required
@admin_required
def detalhar_item_escala(request, pk):
    """
    Visualiza detalhes de um item da escala
    """
    item = get_object_or_404(TBITEM_ESCALA, pk=pk)
    
    dias_semana_pt = {
        0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira', 3: 'Quinta-feira',
        4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo'
    }
    
    # Buscar colaborador e grupo se existirem
    colaborador = None
    grupo = None
    if item.ITE_ESC_COLABORADOR:
        try:
            colaborador = TBCOLABORADORES.objects.get(COL_id=item.ITE_ESC_COLABORADOR)
        except TBCOLABORADORES.DoesNotExist:
            pass
    
    if item.ITE_ESC_GRUPO:
        try:
            grupo = TBGRUPOS.objects.get(GRU_id=item.ITE_ESC_GRUPO)
        except TBGRUPOS.DoesNotExist:
            pass
    
    context = {
        'item': item,
        'acao': 'consultar',
        'modo_detalhe': True,  # Necessário para o template base renderizar o bloco conteudo_detalhe
        'model_verbose_name': 'Item da Escala',
        'dia_semana_nome': dias_semana_pt.get(item.ITE_ESC_DATA.weekday(), ''),
        'mes': item.ITE_ESC_DATA.month,
        'ano': item.ITE_ESC_DATA.year,
        'colaborador': colaborador,
        'grupo': grupo,
    }
    
    return render(request, 'admin_area/tpl_gerenciar_escala.html', context)


@login_required
@admin_required
def editar_item_escala(request, pk):
    """
    Edita um item da escala
    """
    item = get_object_or_404(TBITEM_ESCALA, pk=pk)
    
    if request.method == 'POST':
        form = ItemEscalaForm(request.POST, instance=item, escala=item.ITE_ESC_ESCALA, acao='editar')
        if form.is_valid():
            form.save()
            messages.success(request, 'Item da escala atualizado com sucesso!')
            mes = item.ITE_ESC_DATA.month
            ano = item.ITE_ESC_DATA.year
            return redirect(f"{reverse('app_igreja:listar_itens_escala')}?mes={mes}&ano={ano}")
        else:
            messages.error(request, 'Erro ao atualizar item. Verifique os dados.')
    else:
        form = ItemEscalaForm(instance=item, escala=item.ITE_ESC_ESCALA, acao='editar')
    
    dias_semana_pt = {
        0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira', 3: 'Quinta-feira',
        4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo'
    }
    
    context = {
        'form': form,
        'item': item,
        'acao': 'editar',
        'modo_detalhe': True,  # Necessário para o template base renderizar o bloco conteudo_detalhe
        'model_verbose_name': 'Item da Escala',
        'dia_semana_nome': dias_semana_pt.get(item.ITE_ESC_DATA.weekday(), ''),
        'mes': item.ITE_ESC_DATA.month,
        'ano': item.ITE_ESC_DATA.year,
    }
    
    return render(request, 'admin_area/tpl_gerenciar_escala.html', context)


@login_required
@admin_required
def excluir_item_escala(request, pk):
    """
    Exclui um item da escala
    """
    item = get_object_or_404(TBITEM_ESCALA, pk=pk)
    mes = item.ITE_ESC_DATA.month
    ano = item.ITE_ESC_DATA.year
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item da escala excluído com sucesso!')
        return redirect(f"{reverse('app_igreja:listar_itens_escala')}?mes={mes}&ano={ano}")
    
    dias_semana_pt = {
        0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira', 3: 'Quinta-feira',
        4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo'
    }
    
    context = {
        'item': item,
        'acao': 'excluir',
        'modo_detalhe': True,  # Necessário para o template base renderizar o bloco conteudo_detalhe
        'model_verbose_name': 'Item da Escala',
        'dia_semana_nome': dias_semana_pt.get(item.ITE_ESC_DATA.weekday(), ''),
        'mes': mes,
        'ano': ano,
    }
    
    return render(request, 'admin_area/tpl_gerenciar_escala.html', context)

