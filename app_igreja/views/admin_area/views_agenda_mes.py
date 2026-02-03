"""Agenda do mês: calendário e itens por dia (admin)."""
import json
from calendar import monthrange, monthcalendar, setfirstweekday, SUNDAY
from datetime import date, datetime
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from ...models.area_admin.models_agenda_mes import TBAGENDAMES, TBITEAGENDAMES
from ...models.area_admin.models_modelo import TBMODELO, TBITEM_MODELO
from ...forms.area_admin.forms_agenda_mes import AgendaMesForm, AgendaDiaForm

URL_AGENDA_MES = 'app_igreja:agenda_mes'
MESES_NOMES = [
    '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
]


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


def _redirect_agenda(mes, ano):
    return redirect(f"{reverse(URL_AGENDA_MES)}?mes={mes}&ano={ano}")


def _parse_mes_ano(mes_str, ano_str):
    if not mes_str or not ano_str:
        return None, None
    try:
        mes, ano = int(mes_str), int(ano_str)
        return (mes, ano) if 1 <= mes <= 12 else (None, None)
    except ValueError:
        return None, None


def _primeiro_dia(mes, ano):
    return date(ano, mes, 1) if mes and ano else None


def _get_agenda_mes(mes, ano):
    p = _primeiro_dia(mes, ano)
    if not p:
        return None
    try:
        return TBAGENDAMES.objects.get(AGE_MES=p)
    except TBAGENDAMES.DoesNotExist:
        return None


def _get_agenda_dia(agenda_mes_obj, dia):
    if not agenda_mes_obj or not dia:
        return None
    try:
        return TBITEAGENDAMES.objects.get(AGE_ITE_MES=agenda_mes_obj, AGE_ITE_DIA=dia)
    except TBITEAGENDAMES.DoesNotExist:
        return None


def _dia_passado(ano, mes, dia, hoje=None):
    if not all([ano, mes, dia]):
        return False
    hoje = hoje or date.today()
    try:
        return date(ano, mes, dia) < hoje
    except (TypeError, ValueError):
        return False


def _parse_modelo_id(raw):
    if raw is None or raw == '':
        return 0
    if raw == '0':
        return 0
    try:
        return int(raw)
    except ValueError:
        return 0


def _parse_horario(raw):
    if not raw:
        return None
    try:
        return datetime.strptime(raw, '%H:%M').time()
    except (ValueError, TypeError):
        return None


@login_required
@admin_required
def agenda_mes(request):
    """Calendário do mês e CRUD de itens por dia."""
    mes, ano = _parse_mes_ano(request.GET.get('mes', ''), request.GET.get('ano', ''))
    dia_str = request.GET.get('dia', '').strip()
    acao = request.GET.get('acao', '')
    criar_mes = request.GET.get('criar_mes', '')
    hoje = date.today()

    # Criar mês se solicitado
    if criar_mes == 'sim' and mes and ano:
        p = _primeiro_dia(mes, ano)
        agenda_mes_obj, created = TBAGENDAMES.objects.get_or_create(AGE_MES=p)
        if created:
            for d in range(1, monthrange(ano, mes)[1] + 1):
                TBITEAGENDAMES.objects.create(
                    AGE_ITE_MES=agenda_mes_obj,
                    AGE_ITE_DIA=d,
                    AGE_ITE_MODELO=None,
                    AGE_ITE_ENCARGOS=''
                )
            messages.success(request, f'Agenda do mês {mes}/{ano} criada com sucesso!')
        else:
            messages.info(request, f'Agenda do mês {mes}/{ano} já existe!')
        return _redirect_agenda(mes, ano)

    # Dia selecionado e se passou
    dia = None
    dia_passado = False
    if dia_str:
        try:
            dia = int(dia_str)
            if 1 <= dia <= 31:
                dia_passado = _dia_passado(ano, mes, dia, hoje)
                if dia_passado and acao in ('incluir', 'editar'):
                    acao = 'consultar'
            else:
                dia = None
        except ValueError:
            dia = None

    agenda_mes_obj = _get_agenda_mes(mes, ano)
    agenda_dia = _get_agenda_dia(agenda_mes_obj, dia) if dia else None

    # POST: salvar ou cancelar lançamento
    if request.method == 'POST':
        try:
            dia = int(request.POST.get('dia', dia or 0))
            if dia < 1 or dia > 31:
                dia = None
            else:
                if _dia_passado(ano, mes, dia, hoje):
                    messages.error(request, 'Não é possível editar dias que já passaram.')
                    return _redirect_agenda(mes, ano)
        except (TypeError, ValueError):
            dia = None

        if request.POST.get('cancelar_lancamento') and mes and ano and dia:
            if _dia_passado(ano, mes, dia, hoje):
                messages.error(request, 'Não é possível cancelar lançamento de dias que já passaram.')
                return _redirect_agenda(mes, ano)
            agenda_mes_obj = _get_agenda_mes(mes, ano)
            agenda_existente = _get_agenda_dia(agenda_mes_obj, dia)
            if agenda_existente:
                agenda_existente.AGE_ITE_MODELO = 0
                agenda_existente.save()
                messages.success(request, 'Lançamento cancelado com sucesso!')
            else:
                messages.error(request, 'Erro ao cancelar lançamento.')
            return _redirect_agenda(mes, ano)

        if mes and ano and dia:
            p = _primeiro_dia(mes, ano)
            agenda_mes_obj, _ = TBAGENDAMES.objects.get_or_create(AGE_MES=p)
            modelo_id = _parse_modelo_id(request.POST.get('modelo'))
            horario_obj = _parse_horario(request.POST.get('horario', ''))
            encargos = request.POST.get('encargos', '')

            agenda_existente = _get_agenda_dia(agenda_mes_obj, dia)
            if agenda_existente:
                agenda_existente.AGE_ITE_MODELO = modelo_id
                agenda_existente.AGE_ITE_HORARIO = horario_obj
                agenda_existente.AGE_ITE_ENCARGOS = encargos
                agenda_existente.save()
                messages.success(request, 'Agenda atualizada com sucesso!')
            else:
                TBITEAGENDAMES.objects.create(
                    AGE_ITE_MES=agenda_mes_obj,
                    AGE_ITE_DIA=dia,
                    AGE_ITE_MODELO=modelo_id,
                    AGE_ITE_HORARIO=horario_obj,
                    AGE_ITE_ENCARGOS=encargos
                )
                messages.success(request, 'Agenda criada com sucesso!')
            return _redirect_agenda(mes, ano)

    # Calendário e detalhes
    calendario = []
    dias_com_agenda = set()
    agendas_mes_detalhes = {}
    if mes and ano:
        setfirstweekday(SUNDAY)
        calendario = monthcalendar(ano, mes)
        if agenda_mes_obj:
            itens_agenda = TBITEAGENDAMES.objects.filter(AGE_ITE_MES=agenda_mes_obj)
            dias_com_agenda = set(itens_agenda.values_list('AGE_ITE_DIA', flat=True))
            for item in itens_agenda:
                modelo_id = item.AGE_ITE_MODELO or 0
                modelo_nome = None
                if item.AGE_ITE_MODELO:
                    try:
                        modelo_nome = TBMODELO.objects.get(pk=item.AGE_ITE_MODELO).MOD_DESCRICAO
                    except TBMODELO.DoesNotExist:
                        pass
                agendas_mes_detalhes[item.AGE_ITE_DIA] = {
                    'tem_agenda': True,
                    'tem_modelo': bool(item.AGE_ITE_MODELO),
                    'modelo_nome': modelo_nome,
                    'modelo_id': modelo_id,
                    'agenda_id': item.AGE_ITE_ID
                }

    form_mes = AgendaMesForm(initial={'mes': mes, 'ano': ano} if mes and ano else {})
    form_dia = None
    modelo_obj = None
    if acao in ('incluir', 'editar') and dia and agenda_mes_obj:
        if agenda_dia:
            if agenda_dia.AGE_ITE_MODELO:
                try:
                    modelo_obj = TBMODELO.objects.get(pk=agenda_dia.AGE_ITE_MODELO)
                except TBMODELO.DoesNotExist:
                    pass
            form_dia = AgendaDiaForm(initial={
                'modelo': modelo_obj,
                'horario': agenda_dia.AGE_ITE_HORARIO,
                'encargos': agenda_dia.AGE_ITE_ENCARGOS
            })
        else:
            form_dia = AgendaDiaForm()

    modelo_dia_selecionado = None
    if agenda_dia and agenda_dia.AGE_ITE_MODELO:
        try:
            modelo_dia_selecionado = TBMODELO.objects.get(pk=agenda_dia.AGE_ITE_MODELO)
        except TBMODELO.DoesNotExist:
            pass

    modelos = TBMODELO.objects.all().order_by('MOD_DESCRICAO')
    modelos_json = json.dumps([{'id': m.MOD_ID, 'descricao': m.MOD_DESCRICAO} for m in modelos])

    if dia and mes and ano and not dia_passado:
        dia_passado = _dia_passado(ano, mes, dia, hoje)

    context = {
        'form_mes': form_mes,
        'form_dia': form_dia,
        'mes': mes,
        'ano': ano,
        'mes_nome': MESES_NOMES[mes] if mes else '',
        'calendario': calendario,
        'dias_com_agenda': dias_com_agenda,
        'agendas_mes_detalhes': agendas_mes_detalhes,
        'dia_selecionado': dia,
        'acao': acao,
        'agenda_dia': agenda_dia,
        'agenda_mes_obj': agenda_mes_obj,
        'modelo_dia_selecionado': modelo_dia_selecionado,
        'modelos': modelos,
        'modelos_json': modelos_json,
        'hoje': hoje,
        'primeiro_dia_mes': _primeiro_dia(mes, ano),
        'mes_existe': agenda_mes_obj is not None if mes and ano else False,
        'dia_passado': dia_passado,
    }
    return render(request, 'admin_area/tpl_agenda_mes.html', context)


@login_required
@admin_required
def excluir_agenda_dia(request, agenda_id):
    """Exclui o item de agenda de um dia."""
    agenda_item = get_object_or_404(TBITEAGENDAMES, pk=agenda_id)
    mes = agenda_item.AGE_ITE_MES.AGE_MES.month
    ano = agenda_item.AGE_ITE_MES.AGE_MES.year
    agenda_item.delete()
    messages.success(request, 'Agenda excluída com sucesso!')
    return _redirect_agenda(mes, ano)


@login_required
@admin_required
def buscar_encargos_modelo(request, modelo_id):
    """Retorna encargos do modelo via AJAX."""
    try:
        modelo = get_object_or_404(TBMODELO, pk=modelo_id)
        itens = TBITEM_MODELO.objects.filter(ITEM_MOD_MODELO=modelo).order_by('ITEM_MOD_ID')
        encargos = [{'encargo': i.ITEM_MOD_ENCARGO, 'ocorrencias': i.ITEM_MOD_OCORRENCIA} for i in itens]
        return JsonResponse({'success': True, 'encargos': encargos})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
