"""Escala mensal de missas: formulário, gerar, visualizar e editar descrição (admin)."""
import calendar
import traceback
from datetime import date, datetime
from functools import wraps
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from ...models.area_admin.models_paroquias import TBPAROQUIA
from ...models.area_admin.models_escala import TBESCALA, TBITEM_ESCALA
from ...models.area_admin.models_modelo import TBITEM_MODELO, TBMODELO
from ...models.area_admin.models_agenda_mes import TBAGENDAMES, TBITEAGENDAMES
from ...forms.area_admin.forms_escala_mensal_missa import EscalaMensalMissaForm, EditarDescricaoEscalaMissaForm

URL_ESCALA_MENSAL_FORM = 'app_igreja:escala_mensal_form'
MESES_PT = [
    '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
]
DIAS_SEMANA_PT = {
    0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira', 3: 'Quinta-feira',
    4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo',
}
DIAS_SEMANA_EN_TO_PT = {
    'Monday': 'segunda', 'Tuesday': 'terca', 'Wednesday': 'quarta', 'Thursday': 'quinta',
    'Friday': 'sexta', 'Saturday': 'sabado', 'Sunday': 'domingo',
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


def _redirect_escala_form():
    return redirect(URL_ESCALA_MENSAL_FORM)


def _is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax') == 'true'


def _respond_error(request, msg, status=400):
    if _is_ajax(request):
        return JsonResponse({'success': False, 'message': msg}, status=status)
    messages.error(request, msg)
    return _redirect_escala_form()


def _primeiro_dia(mes, ano):
    return date(ano, mes, 1)


def _str_to_time(horario_str):
    try:
        if isinstance(horario_str, str):
            partes = horario_str.strip().split(':')
            if len(partes) >= 2:
                return datetime.strptime(f"{int(partes[0]):02d}:{int(partes[1]):02d}", "%H:%M").time()
        elif hasattr(horario_str, 'time'):
            return horario_str.time() if callable(getattr(horario_str, 'time')) else horario_str
    except (ValueError, IndexError, AttributeError, TypeError):
        pass
    return None


def _horarios_iguais(horario1, horario2):
    if not horario1 or not horario2:
        return False
    h1, h2 = _str_to_time(str(horario1)), _str_to_time(str(horario2))
    return h1 and h2 and h1.hour == h2.hour and h1.minute == h2.minute


def _deve_gerar_encargo(ocorrencias_list, dia_semana_key):
    return 'todos' in ocorrencias_list or dia_semana_key in ocorrencias_list


def _criar_item_escala(escala_master, data_escala, horario, encargo):
    TBITEM_ESCALA.objects.create(
        ITE_ESC_ESCALA=escala_master,
        ITE_ESC_DATA=data_escala,
        ITE_ESC_HORARIO=horario,
        ITE_ESC_DESCRICAO=encargo,
        ITE_ESC_ENCARGO=encargo,
        ITE_ESC_STATUS='EM_ABERTO',
        ITE_ESC_SITUACAO=False
    )
    return 1


@login_required
@admin_required
def escala_mensal_form(request):
    """Formulário para selecionar mês, ano e modelo para gerar escala."""
    if request.method == 'POST':
        form = EscalaMensalMissaForm(request.POST)
        if form.is_valid():
            mes = form.cleaned_data['mes']
            ano = form.cleaned_data['ano']
            modelo = form.cleaned_data['modelo']
            tema_mes = form.cleaned_data.get('tema_mes', '')
            params = urlencode({'modelo_id': modelo.MOD_ID, 'tema_mes': tema_mes})
            return redirect(f"{reverse('app_igreja:escala_mensal_gerar', args=[mes, ano])}?{params}")
    else:
        form = EscalaMensalMissaForm()
    context = {'form': form, 'modo': 'form', 'title': 'Gerar Escala de Missa'}
    return render(request, 'admin_area/tpl_gerar_escala_missa.html', context)


@login_required
@admin_required
def escala_mensal_gerar(request, mes, ano):
    """Gera escala mensal a partir do modelo; considera agenda do mês e horários da paróquia."""
    try:
        modelo_id = request.GET.get('modelo_id') or request.POST.get('modelo_id')
        tema_mes = (request.GET.get('tema_mes') or request.POST.get('tema_mes') or '').strip()
        if not modelo_id:
            return _respond_error(request, 'Modelo não informado.')

        modelo = get_object_or_404(TBMODELO, pk=modelo_id)
        primeiro_dia_mes = _primeiro_dia(mes, ano)
        sobrepor = (request.GET.get('sobrepor') or request.POST.get('sobrepor') or 'false').lower() == 'true'

        try:
            escala_existente = TBESCALA.objects.get(ESC_MESANO=primeiro_dia_mes)
            itens_count = TBITEM_ESCALA.objects.filter(ITE_ESC_ESCALA=escala_existente).count()
            if itens_count > 0 and not sobrepor:
                if _is_ajax(request):
                    return JsonResponse({
                        'success': False, 'message': f'Escala já existe para {MESES_PT[mes]}/{ano} com {itens_count} itens.',
                        'escala_existe': True, 'itens_existentes': itens_count, 'mes': MESES_PT[mes], 'ano': ano
                    }, status=200)
                messages.warning(request, f'Escala já existe para {MESES_PT[mes]}/{ano} com {itens_count} itens.')
                return _redirect_escala_form()
        except TBESCALA.DoesNotExist:
            pass

        try:
            agenda_mes = TBAGENDAMES.objects.get(AGE_MES=primeiro_dia_mes)
        except TBAGENDAMES.DoesNotExist:
            return _respond_error(request, 'Primeiramente é necessário gerar a agenda do mês.')

        paroquia = TBPAROQUIA.objects.first()
        if not paroquia:
            return _respond_error(request, 'Configurações da paróquia não encontradas.')
        horarios_fixos = paroquia.get_horarios_fixos()
        if not horarios_fixos:
            return _respond_error(request, 'Nenhum horário configurado na paróquia.')

        escala_master, created = TBESCALA.objects.get_or_create(
            ESC_MESANO=primeiro_dia_mes,
            defaults={'ESC_TEMAMES': tema_mes or None}
        )
        if not created and tema_mes:
            escala_master.ESC_TEMAMES = tema_mes
            escala_master.save()
        if sobrepor or not created:
            TBITEM_ESCALA.objects.filter(ITE_ESC_ESCALA=escala_master).delete()

        itens_modelo_padrao = list(TBITEM_MODELO.objects.filter(ITEM_MOD_MODELO=modelo))
        if not itens_modelo_padrao:
            TBITEM_ESCALA.objects.filter(ITE_ESC_ESCALA=escala_master).delete()
            return _respond_error(request, 'O modelo selecionado não possui itens cadastrados.')

        itens_agenda = TBITEAGENDAMES.objects.filter(AGE_ITE_MES=agenda_mes).order_by('AGE_ITE_DIA')
        agenda_por_dia = {item.AGE_ITE_DIA: item for item in itens_agenda}
        dias_mes = calendar.monthrange(ano, mes)[1]
        itens_criados = 0

        for dia in range(1, dias_mes + 1):
            data_escala = date(ano, mes, dia)
            dia_semana_en = data_escala.strftime('%A')
            dia_semana_key = DIAS_SEMANA_EN_TO_PT.get(dia_semana_en)
            if not dia_semana_key:
                continue

            item_agenda = agenda_por_dia.get(dia)
            tem_lancamento = item_agenda and item_agenda.AGE_ITE_MODELO and item_agenda.AGE_ITE_MODELO != 0
            horarios_do_dia = horarios_fixos.get(dia_semana_key, [])
            if isinstance(horarios_do_dia, str):
                horarios_do_dia = [horarios_do_dia]
            elif not isinstance(horarios_do_dia, list):
                horarios_do_dia = []
            horarios_do_dia_times = []
            for h in horarios_do_dia:
                if h and str(h).strip():
                    t = _str_to_time(h)
                    if t:
                        horarios_do_dia_times.append(t)

            if tem_lancamento:
                modelo_agenda_id = item_agenda.AGE_ITE_MODELO
                horario_agenda = item_agenda.AGE_ITE_HORARIO
                try:
                    modelo_agenda = TBMODELO.objects.get(pk=modelo_agenda_id)
                    itens_modelo_agenda = list(TBITEM_MODELO.objects.filter(ITEM_MOD_MODELO=modelo_agenda))
                except TBMODELO.DoesNotExist:
                    modelo_agenda = None
                    itens_modelo_agenda = []
                horario_agenda_time = _str_to_time(str(horario_agenda)) if horario_agenda else None
                horario_agenda_esta_na_paroquia = any(
                    _horarios_iguais(horario_agenda_time, hp) for hp in horarios_do_dia_times
                ) if horario_agenda_time else False

                for horario_paroquia in horarios_do_dia_times:
                    if horario_agenda_esta_na_paroquia and _horarios_iguais(horario_agenda_time, horario_paroquia):
                        if modelo_agenda and itens_modelo_agenda:
                            for item_agenda_modelo in itens_modelo_agenda:
                                ocorrencias_agenda = item_agenda_modelo.ocorrencias_list()
                                if _deve_gerar_encargo(ocorrencias_agenda, dia_semana_key):
                                    itens_criados += _criar_item_escala(
                                        escala_master, data_escala, horario_paroquia, item_agenda_modelo.ITEM_MOD_ENCARGO
                                    )
                        else:
                            for item_modelo in itens_modelo_padrao:
                                if _deve_gerar_encargo(item_modelo.ocorrencias_list(), dia_semana_key):
                                    itens_criados += _criar_item_escala(
                                        escala_master, data_escala, horario_paroquia, item_modelo.ITEM_MOD_ENCARGO
                                    )
                    else:
                        for item_modelo in itens_modelo_padrao:
                            if _deve_gerar_encargo(item_modelo.ocorrencias_list(), dia_semana_key):
                                itens_criados += _criar_item_escala(
                                    escala_master, data_escala, horario_paroquia, item_modelo.ITEM_MOD_ENCARGO
                                )

                if not horario_agenda_esta_na_paroquia and horario_agenda_time and modelo_agenda and itens_modelo_agenda:
                    for item_agenda_modelo in itens_modelo_agenda:
                        if _deve_gerar_encargo(item_agenda_modelo.ocorrencias_list(), dia_semana_key):
                            itens_criados += _criar_item_escala(
                                escala_master, data_escala, horario_agenda_time, item_agenda_modelo.ITEM_MOD_ENCARGO
                            )
            else:
                for item_modelo in itens_modelo_padrao:
                    if not _deve_gerar_encargo(item_modelo.ocorrencias_list(), dia_semana_key):
                        continue
                    for horario_time in horarios_do_dia_times:
                        itens_criados += _criar_item_escala(
                            escala_master, data_escala, horario_time, item_modelo.ITEM_MOD_ENCARGO
                        )

        mes_nome = MESES_PT[mes]
        if _is_ajax(request):
            return JsonResponse({
                'success': True, 'message': 'Escala mensal gerada com sucesso!',
                'registros_gerados': itens_criados, 'mes': mes_nome, 'ano': ano
            })
        messages.success(request, f'Escala mensal gerada com sucesso! {itens_criados} itens criados.')
        return redirect('app_igreja:admin_area')

    except Exception as e:
        traceback.print_exc()
        if _is_ajax(request):
            return JsonResponse({'success': False, 'message': f'Erro ao gerar escala mensal: {str(e)}'}, status=500)
        messages.error(request, f'Erro ao gerar escala mensal: {str(e)}')
        return _redirect_escala_form()


@login_required
@admin_required
def escala_mensal_visualizar(request, mes, ano):
    """Visualiza a escala mensal do mês/ano."""
    primeiro_dia_mes = _primeiro_dia(mes, ano)
    escala_master = TBESCALA.objects.filter(ESC_MESANO=primeiro_dia_mes).first()
    if not escala_master:
        messages.info(request, f'Nenhuma escala encontrada para {mes}/{ano}.')
        return _redirect_escala_form()

    itens_escala = TBITEM_ESCALA.objects.filter(ITE_ESC_ESCALA=escala_master).order_by(
        'ITE_ESC_DATA', 'ITE_ESC_HORARIO', 'ITE_ESC_DESCRICAO'
    )
    dias_missas = {}
    for item in itens_escala:
        dia = item.ITE_ESC_DATA.day
        if dia not in dias_missas:
            dias_missas[dia] = []
        item.dia_semana_nome = DIAS_SEMANA_PT.get(item.ITE_ESC_DATA.weekday(), '')
        dias_missas[dia].append(item)

    context = {
        'escala_master': escala_master,
        'dias_missas': dias_missas,
        'mes': mes,
        'ano': ano,
        'mes_nome': MESES_PT[mes],
        'modo': 'visualizar',
        'title': f'Escala Mensal - {MESES_PT[mes]}/{ano}',
    }
    return render(request, 'admin_area/tpl_gerar_escala_missa.html', context)


@login_required
@admin_required
def escala_mensal_editar_descricao(request, pk):
    """Edita a descrição de um item da escala."""
    item_escala = get_object_or_404(TBITEM_ESCALA, pk=pk)
    if request.method == 'POST':
        form = EditarDescricaoEscalaMissaForm(request.POST)
        if form.is_valid():
            item_escala.ITE_ESC_DESCRICAO = form.cleaned_data['descricao']
            item_escala.save()
            messages.success(request, 'Descrição do item atualizada com sucesso!')
            return redirect(
                'app_igreja:escala_mensal_visualizar',
                mes=item_escala.ITE_ESC_DATA.month,
                ano=item_escala.ITE_ESC_DATA.year
            )
    else:
        form = EditarDescricaoEscalaMissaForm(initial={'descricao': item_escala.ITE_ESC_DESCRICAO})

    context = {
        'form': form,
        'item_escala': item_escala,
        'dia_semana': DIAS_SEMANA_PT[item_escala.ITE_ESC_DATA.weekday()],
        'modo': 'editar_descricao',
        'title': 'Editar Descrição do Item',
    }
    return render(request, 'admin_area/tpl_gerar_escala_missa.html', context)
