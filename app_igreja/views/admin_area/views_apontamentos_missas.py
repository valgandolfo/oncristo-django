"""
==================== VIEWS DE APONTAMENTOS ESCALA MISSA ====================
Views para apontar grupos e status nos itens da escala
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from datetime import date
from calendar import monthrange
import json
import logging

from ...models.area_admin.models_escala import TBESCALA, TBITEM_ESCALA
from ...models.area_admin.models_colaboradores import TBCOLABORADORES
from ...models.area_admin.models_grupos import TBGRUPOS
from ...models.area_admin.models_paroquias import TBPAROQUIA

logger = logging.getLogger(__name__)


def admin_required(view_func):
    """Decorator para verificar se o usuário é administrador"""
    from functools import wraps
    
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_superuser:
            messages.error(request, 'Acesso negado. Apenas administradores podem acessar esta área.')
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_required
@admin_required
def apontamentos_escala_missa(request):
    """
    Lista itens da escala para apontamento (sem os três pontinhos)
    """
    # Buscar mês/ano da query string
    mes = request.GET.get('mes', '')
    ano = request.GET.get('ano', '')
    
    # Se não tiver mês/ano, usar mês e ano atual como padrão
    if not mes or not ano:
        hoje = date.today()
        mes_atual = hoje.month
        ano_atual = hoje.year
        
        # Buscar grupos mesmo sem filtro para o modal
        grupos = TBGRUPOS.objects.filter(GRU_ativo=True).order_by('GRU_nome_grupo')
        
        context = {
            'modo_dashboard': True,
            'sem_filtro': True,
            'mes': mes_atual,
            'ano': ano_atual,
            'grupos': grupos,
        }
        return render(request, 'admin_area/tpl_apontamentos_missas.html', context)
    
    try:
        mes = int(mes)
        ano = int(ano)
        
        # Validar mês e ano
        if mes < 1 or mes > 12:
            messages.error(request, 'Mês inválido. Use valores entre 1 e 12.')
            return redirect('app_igreja:apontamentos_escala_missa')
        
        if ano < 2000 or ano > 2100:
            messages.error(request, 'Ano inválido.')
            return redirect('app_igreja:apontamentos_escala_missa')
        
        # Buscar escala master
        primeiro_dia_mes = date(ano, mes, 1)
        escala_master = TBESCALA.objects.filter(ESC_MESANO=primeiro_dia_mes).first()
        
        if not escala_master:
            messages.info(request, f'Nenhuma escala encontrada para {mes:02d}/{ano}. Gere a escala primeiro.')
            # Buscar grupos mesmo sem escala para o modal
            grupos = TBGRUPOS.objects.filter(GRU_ativo=True).order_by('GRU_nome_grupo')
            context = {
                'modo_dashboard': True,
                'sem_filtro': True,
                'mes': mes,
                'ano': ano,
                'grupos': grupos,
            }
            return render(request, 'admin_area/tpl_apontamentos_missas.html', context)
        
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
        
        # Buscar todos os grupos para o select
        grupos = TBGRUPOS.objects.filter(GRU_ativo=True).order_by('GRU_nome_grupo')
        
        # Adicionar nome do dia da semana, colaborador e grupo para cada item
        for item in itens:
            item.dia_semana_nome = dias_semana_pt.get(item.ITE_ESC_DATA.weekday(), '')
            
            # Buscar nome do colaborador
            if item.ITE_ESC_COLABORADOR:
                try:
                    colaborador = TBCOLABORADORES.objects.get(COL_id=item.ITE_ESC_COLABORADOR)
                    item.colaborador_nome = colaborador.COL_nome_completo
                    item.colaborador_telefone = colaborador.COL_telefone
                    item.colaborador_email = getattr(colaborador, 'COL_email', None)
                except TBCOLABORADORES.DoesNotExist:
                    item.colaborador_nome = '-'
                    item.colaborador_telefone = None
                    item.colaborador_email = None
            else:
                item.colaborador_nome = '-'
                item.colaborador_telefone = None
                item.colaborador_email = None
            
            # Buscar nome do grupo
            if item.ITE_ESC_GRUPO:
                try:
                    grupo = TBGRUPOS.objects.get(GRU_id=item.ITE_ESC_GRUPO)
                    item.grupo_nome = grupo.GRU_nome_grupo
                except TBGRUPOS.DoesNotExist:
                    item.grupo_nome = '-'
            else:
                item.grupo_nome = '-'
            
            # Adicionar informação de situação (bloqueado/desbloqueado)
            item.situacao_bloqueado = not item.ITE_ESC_SITUACAO
            
            # Adicionar informação de janela (se houver)
            if item.ITE_ESC_JANELA:
                janela_map = {
                    1: 'Todas Leituras',
                    2: 'Diferente da escolha Anterior',
                    3: 'Diferente das últimas duas escolhidas'
                }
                item.janela_descricao = janela_map.get(item.ITE_ESC_JANELA, '-')
            else:
                item.janela_descricao = '-'
        
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
            'grupos': grupos,
        }
        
        return render(request, 'admin_area/tpl_apontamentos_missas.html', context)
    
    except ValueError:
        messages.error(request, 'Mês e ano devem ser números válidos.')
        return redirect('app_igreja:apontamentos_escala_missa')
    except Exception as e:
        logger.error(f"Erro ao listar apontamentos: {str(e)}", exc_info=True)
        messages.error(request, f'Erro ao carregar apontamentos: {str(e)}')
        return redirect('app_igreja:apontamentos_escala_missa')


@login_required
@admin_required
@csrf_exempt
@require_http_methods(["POST"])
def atribuir_apontamento(request, item_id):
    """
    Atribui grupo e status a um item da escala
    """
    try:
        item = get_object_or_404(TBITEM_ESCALA, ITE_ESC_ID=item_id)
        
        data = json.loads(request.body)
        grupo_id = data.get('grupo_id')
        status = data.get('status')
        enviar_mensagem = data.get('enviar_mensagem', False)
        acao_situacao = data.get('acao_situacao')  # 'bloquear', 'desbloquear' ou 'janelas'
        dia_inicial = data.get('dia_inicial')
        dia_final = data.get('dia_final')
        janela = data.get('janela')  # 1, 2 ou 3
        
        # Validar status
        if status not in ['DEFINIDO', 'EM_ABERTO', 'RESERVADO']:
            return JsonResponse({'success': False, 'error': 'Status inválido'}, status=400)
        
        # Processar bloqueio/desbloqueio/janelas por período se especificado
        if acao_situacao and dia_inicial and dia_final:
            try:
                dia_inicial_int = int(dia_inicial)
                dia_final_int = int(dia_final)
                
                # Validar dias
                if dia_inicial_int < 1 or dia_inicial_int > 31 or dia_final_int < 1 or dia_final_int > 31:
                    return JsonResponse({'success': False, 'error': 'Dias inválidos'}, status=400)
                
                if dia_inicial_int > dia_final_int:
                    return JsonResponse({'success': False, 'error': 'Dia inicial deve ser menor ou igual ao dia final'}, status=400)
                
                # Buscar todos os itens do mesmo mês/ano no período especificado
                primeiro_dia_mes = date(item.ITE_ESC_DATA.year, item.ITE_ESC_DATA.month, 1)
                ultimo_dia_mes = monthrange(item.ITE_ESC_DATA.year, item.ITE_ESC_DATA.month)[1]
                
                # Ajustar dias para não ultrapassar o último dia do mês
                dia_inicial_ajustado = min(dia_inicial_int, ultimo_dia_mes)
                dia_final_ajustado = min(dia_final_int, ultimo_dia_mes)
                
                # Buscar itens no período
                itens_periodo = TBITEM_ESCALA.objects.filter(
                    ITE_ESC_ESCALA=item.ITE_ESC_ESCALA
                ).filter(
                    ITE_ESC_DATA__day__gte=dia_inicial_ajustado,
                    ITE_ESC_DATA__day__lte=dia_final_ajustado
                )
                
                if acao_situacao == 'janelas':
                    # Validar valor de janela
                    if janela not in [1, 2, 3]:
                        return JsonResponse({'success': False, 'error': 'Valor de janela inválido. Use 1, 2 ou 3.'}, status=400)
                    
                    # Atualizar janela de todos os itens do período
                    itens_atualizados = itens_periodo.update(ITE_ESC_JANELA=janela)
                    logger.info(f"✅ Janela {janela} aplicada no período: dias {dia_inicial_ajustado} a {dia_final_ajustado} - {itens_atualizados} item(ns) atualizado(s)")
                else:
                    # Determinar valor da situação
                    situacao_valor = True if acao_situacao == 'desbloquear' else False
                    
                    # Atualizar situação de todos os itens do período
                    itens_atualizados = itens_periodo.update(ITE_ESC_SITUACAO=situacao_valor)
                    logger.info(f"✅ {acao_situacao.capitalize()} período: dias {dia_inicial_ajustado} a {dia_final_ajustado} - {itens_atualizados} item(ns) atualizado(s)")
                
            except (ValueError, TypeError) as e:
                return JsonResponse({'success': False, 'error': f'Erro ao processar período: {str(e)}'}, status=400)
        
        # Atualizar item atual
        if grupo_id:
            item.ITE_ESC_GRUPO = int(grupo_id)
        item.ITE_ESC_STATUS = status
        item.save()
        
        # Se um grupo foi atribuído, atribuir automaticamente para todos os itens do mesmo dia e horário
        if grupo_id:
            grupo_id_int = int(grupo_id)
            # Buscar todos os itens do mesmo dia e horário (mesma escala)
            itens_mesmo_horario = TBITEM_ESCALA.objects.filter(
                ITE_ESC_ESCALA=item.ITE_ESC_ESCALA,
                ITE_ESC_DATA=item.ITE_ESC_DATA,
                ITE_ESC_HORARIO=item.ITE_ESC_HORARIO
            ).exclude(ITE_ESC_ID=item.ITE_ESC_ID)  # Excluir o item atual que já foi atualizado
            
            # Atualizar grupo para todos os itens do mesmo horário (mantendo o status individual)
            itens_atualizados = 0
            for item_horario in itens_mesmo_horario:
                item_horario.ITE_ESC_GRUPO = grupo_id_int
                item_horario.save()
                itens_atualizados += 1
            
            if itens_atualizados > 0:
                logger.info(f"✅ Grupo {grupo_id_int} atribuído automaticamente para {itens_atualizados} item(ns) do mesmo horário ({item.ITE_ESC_DATA.strftime('%d/%m/%Y')} às {item.ITE_ESC_HORARIO.strftime('%H:%M')})")
        
        # Se status for DEFINIDO e enviar_mensagem for True, enviar mensagem/email
        if status == 'DEFINIDO' and enviar_mensagem:
            # Buscar colaborador
            colaborador = None
            if item.ITE_ESC_COLABORADOR:
                try:
                    colaborador = TBCOLABORADORES.objects.get(COL_id=item.ITE_ESC_COLABORADOR)
                except TBCOLABORADORES.DoesNotExist:
                    pass
            
            if colaborador:
                # Enviar mensagem/email
                from ...views.area_publica.views_whatsapp_api import send_whatsapp_message
                from django.core.mail import send_mail
                from django.conf import settings
                
                # Preparar mensagem
                dias_semana_pt = {
                    0: 'Segunda-feira',
                    1: 'Terça-feira',
                    2: 'Quarta-feira',
                    3: 'Quinta-feira',
                    4: 'Sexta-feira',
                    5: 'Sábado',
                    6: 'Domingo'
                }
                dia_semana = dias_semana_pt.get(item.ITE_ESC_DATA.weekday(), '')
                
                mensagem = (
                    f"Estimado colaborador {colaborador.COL_nome_completo}, estou confirmando sua participação "
                    f"como colaborador executando o encargo de {item.ITE_ESC_ENCARGO or 'colaborador'} no dia "
                    f"{item.ITE_ESC_DATA.strftime('%d')} {dia_semana} na missa das "
                    f"{item.ITE_ESC_HORARIO.strftime('%H:%M')}, desde já contamos com a sua presença. Deus abençoe 🙏"
                )
                
                # Enviar WhatsApp se tiver telefone
                if colaborador.COL_telefone:
                    # Limpar e formatar telefone para WhatsApp
                    import re
                    # Remover todos os caracteres não numéricos
                    telefone_limpo = re.sub(r'[^\d]', '', str(colaborador.COL_telefone))
                    
                    # Log do telefone original e limpo
                    logger.info(f"📞 Telefone original: {colaborador.COL_telefone}")
                    logger.info(f"📞 Telefone limpo: {telefone_limpo}")
                    
                    # Adicionar código do país se não tiver
                    if not telefone_limpo.startswith('55'):
                        telefone_completo = f"55{telefone_limpo}"
                    else:
                        telefone_completo = telefone_limpo
                    
                    # Log do telefone completo para API
                    logger.info(f"📞 Telefone completo para API: {telefone_completo}")
                    
                    # Validar formato do telefone (deve ter 13 dígitos: 55 + DDD + número)
                    if len(telefone_completo) < 12 or len(telefone_completo) > 13:
                        logger.error(f"❌ Telefone inválido: {telefone_completo} (tamanho: {len(telefone_completo)})")
                        raise ValueError(f"Telefone inválido: {telefone_completo}")
                    
                    try:
                        # Enviar foto da paróquia primeiro (se houver)
                        from ...views.area_publica.views_whatsapp_api import send_whatsapp_image, get_imagem_capa_url
                        
                        # Buscar foto de capa da paróquia (VIS_FOTO_CAPA do TBVISUAL)
                        imagem_url = get_imagem_capa_url(optimized=False)
                        
                        if imagem_url:
                            logger.info(f"📸 URL da foto de capa: {imagem_url}")
                            
                            # Enviar foto primeiro
                            resultado_imagem = send_whatsapp_image(telefone_completo, imagem_url)
                            
                            # Verificar se houve erro no envio da imagem
                            if resultado_imagem.get('error'):
                                logger.warning(f"⚠️  Erro ao enviar imagem, mas continuando com mensagem: {resultado_imagem.get('error')}")
                            else:
                                logger.info(f"📸 Foto de capa da paróquia enviada para {colaborador.COL_nome_completo}")
                                
                                # Pequeno delay para garantir que a imagem seja processada antes da mensagem
                                import time
                                time.sleep(1)
                        else:
                            logger.warning(f"⚠️  Foto de capa da paróquia não encontrada, enviando apenas mensagem")
                        
                        # Enviar mensagem
                        resultado_mensagem = send_whatsapp_message(telefone_completo, mensagem)
                        
                        # Verificar se houve erro no envio
                        if resultado_mensagem.get('error'):
                            logger.error(f"❌ Erro ao enviar mensagem WhatsApp: {resultado_mensagem.get('error')}")
                            logger.error(f"   Telefone usado: {telefone_completo}")
                            logger.error(f"   Resposta da API: {resultado_mensagem}")
                        else:
                            logger.info(f"✅ Mensagem enviada com sucesso para colaborador {colaborador.COL_nome_completo}")
                            logger.info(f"   Telefone: {telefone_completo}")
                            logger.info(f"   Resposta da API: {resultado_mensagem}")
                    except Exception as e:
                        logger.error(f"❌ Erro ao enviar WhatsApp: {str(e)}", exc_info=True)
                        logger.error(f"   Telefone usado: {telefone_completo if 'telefone_completo' in locals() else 'N/A'}")
                        raise  # Re-raise para que o erro seja tratado acima
                
                # Enviar email se tiver (opcional - modelo pode não ter este campo)
                # Nota: O modelo TBCOLABORADORES pode não ter campo de email
                # Se precisar, adicione o campo ao modelo primeiro
        
        return JsonResponse({
            'success': True,
            'message': 'Apontamento atribuído com sucesso!'
        })
    
    except Exception as e:
        logger.error(f"Erro ao atribuir apontamento: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

