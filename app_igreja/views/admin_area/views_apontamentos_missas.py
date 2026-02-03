"""Apontamentos da escala de missas: listar itens e atribuir grupo/status (admin)."""
import json
import logging
import re
import time
from calendar import monthrange
from datetime import date
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ...models.area_admin.models_escala import TBESCALA, TBITEM_ESCALA
from ...models.area_admin.models_colaboradores import TBCOLABORADORES
from ...models.area_admin.models_grupos import TBGRUPOS

logger = logging.getLogger(__name__)

URL_APONTAMENTOS_ESCALA_MISSA = 'app_igreja:apontamentos_escala_missa'
MESES_PT = [
    '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
]
DIAS_SEMANA_PT = {
    0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira', 3: 'Quinta-feira',
    4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo',
}
JANELA_MAP = {1: 'Todas Leituras', 2: 'Diferente da escolha Anterior', 3: 'Diferente das últimas duas escolhidas'}
STATUS_VALIDOS = {'DEFINIDO', 'EM_ABERTO', 'RESERVADO'}


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


def _redirect_apontamentos():
    return redirect(URL_APONTAMENTOS_ESCALA_MISSA)


def _primeiro_dia(mes, ano):
    return date(ano, mes, 1) if mes and ano else None


def _parse_mes_ano(mes_str, ano_str):
    if not mes_str or not ano_str:
        return None, None
    try:
        mes, ano = int(mes_str), int(ano_str)
        if 1 <= mes <= 12 and 2000 <= ano <= 2100:
            return mes, ano
    except ValueError:
        pass
    return None, None


def _enrich_item_apontamento(item):
    """Atribui dia_semana_nome, colaborador_*, grupo_nome, situacao_bloqueado e janela_descricao ao item."""
    item.dia_semana_nome = DIAS_SEMANA_PT.get(item.ITE_ESC_DATA.weekday(), '')
    if item.ITE_ESC_COLABORADOR:
        try:
            col = TBCOLABORADORES.objects.get(COL_id=item.ITE_ESC_COLABORADOR)
            item.colaborador_nome = col.COL_nome_completo
            item.colaborador_telefone = col.COL_telefone
            item.colaborador_email = getattr(col, 'COL_email', None)
        except TBCOLABORADORES.DoesNotExist:
            item.colaborador_nome = '-'
            item.colaborador_telefone = None
            item.colaborador_email = None
    else:
        item.colaborador_nome = '-'
        item.colaborador_telefone = None
        item.colaborador_email = None
    if item.ITE_ESC_GRUPO:
        try:
            item.grupo_nome = TBGRUPOS.objects.get(GRU_id=item.ITE_ESC_GRUPO).GRU_nome_grupo
        except TBGRUPOS.DoesNotExist:
            item.grupo_nome = '-'
    else:
        item.grupo_nome = '-'
    item.situacao_bloqueado = not item.ITE_ESC_SITUACAO
    item.janela_descricao = JANELA_MAP.get(item.ITE_ESC_JANELA, '-') if item.ITE_ESC_JANELA else '-'


@login_required
@admin_required
def apontamentos_escala_missa(request):
    """Lista itens da escala para apontamento (grupos e status)."""
    mes_str = request.GET.get('mes', '')
    ano_str = request.GET.get('ano', '')
    grupos = TBGRUPOS.objects.filter(GRU_ativo=True).order_by('GRU_nome_grupo')

    if not mes_str or not ano_str:
        hoje = date.today()
        context = {
            'modo_dashboard': True,
            'sem_filtro': True,
            'mes': hoje.month,
            'ano': hoje.year,
            'grupos': grupos,
        }
        return render(request, 'admin_area/tpl_apontamentos_missas.html', context)

    try:
        parsed = _parse_mes_ano(mes_str, ano_str)
        if not parsed:
            messages.error(request, 'Mês e ano devem ser números válidos (mês 1-12, ano 2000-2100).')
            return _redirect_apontamentos()
        mes, ano = parsed

        if mes < 1 or mes > 12:
            messages.error(request, 'Mês inválido. Use valores entre 1 e 12.')
            return _redirect_apontamentos()
        if ano < 2000 or ano > 2100:
            messages.error(request, 'Ano inválido.')
            return _redirect_apontamentos()

        primeiro_dia_mes = _primeiro_dia(mes, ano)
        escala_master = TBESCALA.objects.filter(ESC_MESANO=primeiro_dia_mes).first()
        if not escala_master:
            messages.info(request, f'Nenhuma escala encontrada para {mes:02d}/{ano}. Gere a escala primeiro.')
            context = {'modo_dashboard': True, 'sem_filtro': True, 'mes': mes, 'ano': ano, 'grupos': grupos}
            return render(request, 'admin_area/tpl_apontamentos_missas.html', context)

        itens = TBITEM_ESCALA.objects.filter(ITE_ESC_ESCALA=escala_master).order_by(
            'ITE_ESC_DATA', 'ITE_ESC_HORARIO'
        )
        for item in itens:
            _enrich_item_apontamento(item)

        paginator = Paginator(itens, 50)
        page_obj = paginator.get_page(request.GET.get('page'))

        context = {
            'page_obj': page_obj,
            'escala_master': escala_master,
            'mes': mes,
            'ano': ano,
            'mes_nome': MESES_PT[mes],
            'modo_dashboard': True,
            'grupos': grupos,
        }
        return render(request, 'admin_area/tpl_apontamentos_missas.html', context)

    except ValueError:
        messages.error(request, 'Mês e ano devem ser números válidos.')
        return _redirect_apontamentos()
    except Exception as e:
        logger.error("Erro ao listar apontamentos: %s", str(e), exc_info=True)
        messages.error(request, f'Erro ao carregar apontamentos: {str(e)}')
        return _redirect_apontamentos()


@login_required
@admin_required
@csrf_exempt
@require_http_methods(["POST"])
def atribuir_apontamento(request, item_id):
    """Atribui grupo e status a um item da escala (AJAX)."""
    try:
        item = get_object_or_404(TBITEM_ESCALA, ITE_ESC_ID=item_id)
        data = json.loads(request.body)
        grupo_id = data.get('grupo_id')
        status = data.get('status')
        enviar_mensagem = data.get('enviar_mensagem', False)
        acao_situacao = data.get('acao_situacao')
        dia_inicial = data.get('dia_inicial')
        dia_final = data.get('dia_final')
        janela = data.get('janela')

        if status not in STATUS_VALIDOS:
            return JsonResponse({'success': False, 'error': 'Status inválido'}, status=400)

        if acao_situacao and dia_inicial is not None and dia_final is not None:
            try:
                dia_inicial_int = int(dia_inicial)
                dia_final_int = int(dia_final)
                if not (1 <= dia_inicial_int <= 31 and 1 <= dia_final_int <= 31):
                    return JsonResponse({'success': False, 'error': 'Dias inválidos'}, status=400)
                if dia_inicial_int > dia_final_int:
                    return JsonResponse({'success': False, 'error': 'Dia inicial deve ser menor ou igual ao dia final'}, status=400)

                ano, mes = item.ITE_ESC_DATA.year, item.ITE_ESC_DATA.month
                ultimo_dia = monthrange(ano, mes)[1]
                dia_ini = min(dia_inicial_int, ultimo_dia)
                dia_fim = min(dia_final_int, ultimo_dia)

                itens_periodo = TBITEM_ESCALA.objects.filter(
                    ITE_ESC_ESCALA=item.ITE_ESC_ESCALA,
                    ITE_ESC_DATA__day__gte=dia_ini,
                    ITE_ESC_DATA__day__lte=dia_fim
                )

                if acao_situacao == 'janelas':
                    if janela not in (1, 2, 3):
                        return JsonResponse({'success': False, 'error': 'Valor de janela inválido. Use 1, 2 ou 3.'}, status=400)
                    n = itens_periodo.update(ITE_ESC_JANELA=janela)
                    logger.info("Janela %s aplicada no período: dias %s a %s - %s item(ns)", janela, dia_ini, dia_fim, n)
                else:
                    situacao_valor = acao_situacao == 'desbloquear'
                    n = itens_periodo.update(ITE_ESC_SITUACAO=situacao_valor)
                    logger.info("%s período: dias %s a %s - %s item(ns)", acao_situacao.capitalize(), dia_ini, dia_fim, n)
            except (ValueError, TypeError) as e:
                return JsonResponse({'success': False, 'error': f'Erro ao processar período: {str(e)}'}, status=400)

        if grupo_id:
            item.ITE_ESC_GRUPO = int(grupo_id)
        item.ITE_ESC_STATUS = status
        item.save()

        if grupo_id:
            grupo_id_int = int(grupo_id)
            itens_mesmo_horario = TBITEM_ESCALA.objects.filter(
                ITE_ESC_ESCALA=item.ITE_ESC_ESCALA,
                ITE_ESC_DATA=item.ITE_ESC_DATA,
                ITE_ESC_HORARIO=item.ITE_ESC_HORARIO
            ).exclude(ITE_ESC_ID=item.ITE_ESC_ID)
            for it in itens_mesmo_horario:
                it.ITE_ESC_GRUPO = grupo_id_int
                it.save()
            if itens_mesmo_horario:
                logger.info(
                    "Grupo %s atribuído para %s item(ns) do mesmo horário (%s às %s)",
                    grupo_id_int, itens_mesmo_horario.count(),
                    item.ITE_ESC_DATA.strftime('%d/%m/%Y'),
                    item.ITE_ESC_HORARIO.strftime('%H:%M')
                )

        if status == 'DEFINIDO' and enviar_mensagem:
            colaborador = None
            if item.ITE_ESC_COLABORADOR:
                try:
                    colaborador = TBCOLABORADORES.objects.get(COL_id=item.ITE_ESC_COLABORADOR)
                except TBCOLABORADORES.DoesNotExist:
                    pass

            if colaborador:
                dia_semana = DIAS_SEMANA_PT.get(item.ITE_ESC_DATA.weekday(), '')
                texto = (
                    f"Estimado colaborador {colaborador.COL_nome_completo}, estou confirmando sua participação "
                    f"como colaborador executando o encargo de {item.ITE_ESC_ENCARGO or 'colaborador'} no dia "
                    f"{item.ITE_ESC_DATA.strftime('%d')} {dia_semana} na missa das "
                    f"{item.ITE_ESC_HORARIO.strftime('%H:%M')}, desde já contamos com a sua presença. Deus abençoe 🙏"
                )
                if colaborador.COL_telefone:
                    telefone_limpo = re.sub(r'[^\d]', '', str(colaborador.COL_telefone))
                    telefone_completo = f"55{telefone_limpo}" if not telefone_limpo.startswith('55') else telefone_limpo
                    if len(telefone_completo) < 12 or len(telefone_completo) > 13:
                        logger.error("Telefone inválido: %s", telefone_completo)
                        raise ValueError(f"Telefone inválido: {telefone_completo}")

                    try:
                        from ...views.area_publica.views_whatsapp_api import (
                            send_whatsapp_message,
                            send_whatsapp_image,
                            get_imagem_capa_url,
                        )
                        imagem_url = get_imagem_capa_url(optimized=False)
                        if imagem_url:
                            res_img = send_whatsapp_image(telefone_completo, imagem_url)
                            if res_img.get('error'):
                                logger.warning("Erro ao enviar imagem: %s", res_img.get('error'))
                            else:
                                time.sleep(1)
                        res_msg = send_whatsapp_message(telefone_completo, texto)
                        if res_msg.get('error'):
                            logger.error("Erro ao enviar WhatsApp: %s", res_msg.get('error'))
                        else:
                            logger.info("Mensagem enviada para %s", colaborador.COL_nome_completo)
                    except Exception as e:
                        logger.error("Erro ao enviar WhatsApp: %s", str(e), exc_info=True)
                        raise

        return JsonResponse({'success': True, 'message': 'Apontamento atribuído com sucesso!'})

    except Exception as e:
        logger.error("Erro ao atribuir apontamento: %s", str(e), exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
