"""Gerenciar escala de missas: listar, criar, detalhar, editar e excluir itens (admin)."""
from datetime import date, datetime
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from ...models.area_admin.models_escala import TBESCALA, TBITEM_ESCALA
from ...models.area_admin.models_colaboradores import TBCOLABORADORES
from ...models.area_admin.models_grupos import TBGRUPOS
from ...forms.area_admin.forms_gerenciar_escala import ItemEscalaForm

URL_LISTAR_ITENS_ESCALA = 'app_igreja:listar_itens_escala'
MESES_PT = [
    '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
]
DIAS_SEMANA_PT = {
    0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira', 3: 'Quinta-feira',
    4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo',
}


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


def _redirect_listar_escala(mes, ano):
    return redirect(f"{reverse(URL_LISTAR_ITENS_ESCALA)}?mes={mes}&ano={ano}")


def _primeiro_dia(mes, ano):
    return date(ano, mes, 1) if mes and ano else None


def _parse_mes_ano(mes_str, ano_str):
    if not mes_str or not ano_str:
        return None, None
    try:
        mes, ano = int(mes_str.strip()), int(ano_str.strip())
        if 1 <= mes <= 12 and 2000 <= ano <= 2100:
            return mes, ano
    except ValueError:
        pass
    return None, None


def _enrich_item(item):
    """Atribui dia_semana_nome, colaborador_nome e grupo_nome ao item."""
    item.dia_semana_nome = DIAS_SEMANA_PT.get(item.ITE_ESC_DATA.weekday(), '')
    if item.ITE_ESC_COLABORADOR:
        try:
            col = TBCOLABORADORES.objects.get(COL_id=item.ITE_ESC_COLABORADOR)
            item.colaborador_nome = col.COL_nome_completo.split()[0] if col.COL_nome_completo else '-'
        except TBCOLABORADORES.DoesNotExist:
            item.colaborador_nome = '-'
    else:
        item.colaborador_nome = '-'
    if item.ITE_ESC_GRUPO:
        try:
            item.grupo_nome = TBGRUPOS.objects.get(GRU_id=item.ITE_ESC_GRUPO).GRU_nome_grupo
        except TBGRUPOS.DoesNotExist:
            item.grupo_nome = '-'
    else:
        item.grupo_nome = '-'


@login_required
@admin_required
def listar_itens_escala(request):
    """Lista itens da escala com filtro por mês/ano e paginação."""
    mes_str = request.GET.get('mes', '').strip()
    ano_str = request.GET.get('ano', '').strip()
    page_param = request.GET.get('page', '').strip()
    hoje = date.today()

    if not mes_str or not ano_str:
        context = {
            'modo_dashboard': True,
            'sem_filtro': True,
            'mes': hoje.month,
            'ano': hoje.year,
        }
        return render(request, 'admin_area/tpl_gerenciar_escala.html', context)

    parsed = _parse_mes_ano(mes_str, ano_str)
    if not parsed:
        messages.error(request, 'Mês e ano devem ser números válidos (mês 1-12, ano 2000-2100).')
        return redirect(URL_LISTAR_ITENS_ESCALA)
    mes, ano = parsed

    primeiro_dia_mes = _primeiro_dia(mes, ano)
    escala_master = TBESCALA.objects.filter(ESC_MESANO=primeiro_dia_mes).first()
    if not escala_master:
        messages.info(request, f'Nenhuma escala encontrada para {mes:02d}/{ano}. Gere a escala primeiro.')
        context = {'modo_dashboard': True, 'sem_filtro': True, 'mes': mes, 'ano': ano}
        return render(request, 'admin_area/tpl_gerenciar_escala.html', context)

    itens = TBITEM_ESCALA.objects.filter(ITE_ESC_ESCALA=escala_master).filter(
        ITE_ESC_DATA__gte=hoje
    ).order_by('ITE_ESC_DATA', 'ITE_ESC_HORARIO')
    for item in itens:
        _enrich_item(item)

    paginator = Paginator(itens, 50)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'escala_master': escala_master,
        'mes': mes,
        'ano': ano,
        'mes_nome': MESES_PT[mes],
        'modo_dashboard': True,
    }
    return render(request, 'admin_area/tpl_gerenciar_escala.html', context)


@login_required
@admin_required
def criar_item_escala(request):
    """Cria um novo item da escala."""
    mes_str = request.GET.get('mes', '')
    ano_str = request.GET.get('ano', '')
    data_param = request.GET.get('data', '').strip()
    hora_param = request.GET.get('hora', '').strip()

    if not mes_str or not ano_str:
        messages.error(request, 'Mês e ano são obrigatórios.')
        return redirect(URL_LISTAR_ITENS_ESCALA)

    parsed = _parse_mes_ano(mes_str, ano_str)
    if not parsed:
        messages.error(request, 'Mês/ano inválidos.')
        return redirect(URL_LISTAR_ITENS_ESCALA)
    mes, ano = parsed

    primeiro_dia_mes = _primeiro_dia(mes, ano)
    try:
        escala_master = TBESCALA.objects.get(ESC_MESANO=primeiro_dia_mes)
    except TBESCALA.DoesNotExist:
        messages.error(request, 'Escala não encontrada para o mês/ano informado.')
        return redirect(URL_LISTAR_ITENS_ESCALA)

    if request.method == 'POST':
        form = ItemEscalaForm(request.POST, escala=escala_master, acao='incluir')
        if form.is_valid():
            item = form.save(commit=False)
            item.ITE_ESC_ESCALA = escala_master
            item.save()
            messages.success(request, 'Item da escala criado com sucesso!')
            return _redirect_listar_escala(mes, ano)
        messages.error(request, 'Erro ao criar item. Verifique os dados.')
    else:
        form = ItemEscalaForm(escala=escala_master, acao='incluir')
        if data_param:
            try:
                form.initial['ITE_ESC_DATA'] = datetime.strptime(data_param, '%Y-%m-%d').date()
            except ValueError:
                form.initial['ITE_ESC_DATA'] = primeiro_dia_mes
        else:
            form.initial['ITE_ESC_DATA'] = primeiro_dia_mes
        if hora_param:
            try:
                form.initial['ITE_ESC_HORARIO'] = datetime.strptime(hora_param, '%H:%M').time()
            except ValueError:
                pass

    dia_semana_nome = None
    if data_param:
        try:
            dia_semana_nome = DIAS_SEMANA_PT.get(datetime.strptime(data_param, '%Y-%m-%d').date().weekday())
        except ValueError:
            pass

    context = {
        'form': form,
        'acao': 'incluir',
        'modo_detalhe': True,
        'model_verbose_name': 'Item da Escala',
        'escala_master': escala_master,
        'mes': mes,
        'ano': ano,
        'dias_semana_pt': DIAS_SEMANA_PT,
        'dia_semana_nome': dia_semana_nome,
    }
    return render(request, 'admin_area/tpl_gerenciar_escala.html', context)


@login_required
@admin_required
def detalhar_item_escala(request, pk):
    """Exibe detalhes de um item da escala."""
    item = get_object_or_404(TBITEM_ESCALA, pk=pk)
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
        'modo_detalhe': True,
        'model_verbose_name': 'Item da Escala',
        'dia_semana_nome': DIAS_SEMANA_PT.get(item.ITE_ESC_DATA.weekday(), ''),
        'mes': item.ITE_ESC_DATA.month,
        'ano': item.ITE_ESC_DATA.year,
        'colaborador': colaborador,
        'grupo': grupo,
    }
    return render(request, 'admin_area/tpl_gerenciar_escala.html', context)


@login_required
@admin_required
def editar_item_escala(request, pk):
    """Edita um item da escala."""
    item = get_object_or_404(TBITEM_ESCALA, pk=pk)
    mes, ano = item.ITE_ESC_DATA.month, item.ITE_ESC_DATA.year

    if request.method == 'POST':
        form = ItemEscalaForm(request.POST, instance=item, escala=item.ITE_ESC_ESCALA, acao='editar')
        if form.is_valid():
            form.save()
            messages.success(request, 'Item da escala atualizado com sucesso!')
            return _redirect_listar_escala(mes, ano)
        messages.error(request, 'Erro ao atualizar item. Verifique os dados.')
    else:
        form = ItemEscalaForm(instance=item, escala=item.ITE_ESC_ESCALA, acao='editar')

    context = {
        'form': form,
        'item': item,
        'acao': 'editar',
        'modo_detalhe': True,
        'model_verbose_name': 'Item da Escala',
        'dia_semana_nome': DIAS_SEMANA_PT.get(item.ITE_ESC_DATA.weekday(), ''),
        'mes': mes,
        'ano': ano,
    }
    return render(request, 'admin_area/tpl_gerenciar_escala.html', context)


@login_required
@admin_required
def excluir_item_escala(request, pk):
    """Exclui um item da escala."""
    item = get_object_or_404(TBITEM_ESCALA, pk=pk)
    mes, ano = item.ITE_ESC_DATA.month, item.ITE_ESC_DATA.year

    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item da escala excluído com sucesso!')
        return _redirect_listar_escala(mes, ano)

    context = {
        'item': item,
        'acao': 'excluir',
        'modo_detalhe': True,
        'model_verbose_name': 'Item da Escala',
        'dia_semana_nome': DIAS_SEMANA_PT.get(item.ITE_ESC_DATA.weekday(), ''),
        'mes': mes,
        'ano': ano,
    }
    return render(request, 'admin_area/tpl_gerenciar_escala.html', context)
