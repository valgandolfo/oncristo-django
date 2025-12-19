"""
==================== VIEW AGENDA DO MÊS ====================
View para gerenciar agenda mensal com calendário (estrutura master-detail)
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse
from datetime import date, datetime
from calendar import monthrange, monthcalendar, setfirstweekday, SUNDAY
from django.db.models import Q

from ...models.area_admin.models_agenda_mes import TBAGENDAMES, TBITEAGENDAMES
from ...models.area_admin.models_modelo import TBMODELO, TBITEM_MODELO
from ...forms.area_admin.forms_agenda_mes import AgendaMesForm, AgendaDiaForm


@login_required
def agenda_mes(request):
    """
    View principal - mostra calendário do mês selecionado
    """
    # Obter mês e ano dos parâmetros GET
    mes_str = request.GET.get('mes', '')
    ano_str = request.GET.get('ano', '')
    dia_str = request.GET.get('dia', '')
    acao = request.GET.get('acao', '')  # incluir, editar, consultar
    criar_mes = request.GET.get('criar_mes', '')  # flag para criar mês
    
    hoje = date.today()
    mes = None
    ano = None
    
    # Validar mês e ano
    if mes_str and ano_str:
        try:
            mes = int(mes_str)
            ano = int(ano_str)
            if mes < 1 or mes > 12:
                mes = None
                ano = None
        except ValueError:
            mes = None
            ano = None
    
    # Se foi solicitado criar o mês
    if criar_mes == 'sim' and mes and ano:
        primeiro_dia_mes = date(ano, mes, 1)
        ultimo_dia_num = monthrange(ano, mes)[1]
        
        # Verificar se já existe
        agenda_mes_obj, created = TBAGENDAMES.objects.get_or_create(AGE_MES=primeiro_dia_mes)
        
        if created:
            # Criar todos os dias do mês em branco
            for dia in range(1, ultimo_dia_num + 1):
                TBITEAGENDAMES.objects.create(
                    AGE_ITE_MES=agenda_mes_obj,
                    AGE_ITE_DIA=dia,
                    AGE_ITE_MODELO=None,
                    AGE_ITE_ENCARGOS=''
                )
            messages.success(request, f'Agenda do mês {mes}/{ano} criada com sucesso!')
        else:
            messages.info(request, f'Agenda do mês {mes}/{ano} já existe!')
        
        return redirect(f"{request.path}?mes={mes}&ano={ano}")
    
    # Se foi selecionado um dia, processar ação
    dia = None
    dia_passado = False
    if dia_str:
        try:
            dia = int(dia_str)
            if dia < 1 or dia > 31:
                dia = None
            else:
                # Verificar se o dia passou
                if mes and ano:
                    data_dia = date(ano, mes, dia)
                    if data_dia < hoje:
                        dia_passado = True
                        # Forçar modo consulta se for dia passado
                        if acao in ['incluir', 'editar']:
                            acao = 'consultar'
        except ValueError:
            dia = None
    
    # Buscar agenda master do mês
    agenda_mes_obj = None
    if mes and ano:
        primeiro_dia_mes = date(ano, mes, 1)
        try:
            agenda_mes_obj = TBAGENDAMES.objects.get(AGE_MES=primeiro_dia_mes)
        except TBAGENDAMES.DoesNotExist:
            agenda_mes_obj = None
    
    # Buscar item do dia se existir
    agenda_dia = None
    if dia and agenda_mes_obj:
        try:
            agenda_dia = TBITEAGENDAMES.objects.get(AGE_ITE_MES=agenda_mes_obj, AGE_ITE_DIA=dia)
        except TBITEAGENDAMES.DoesNotExist:
            agenda_dia = None
    
    # Processar formulário de dia (POST)
    if request.method == 'POST':
        # Garantir dia a partir do POST (modal não envia dia via GET)
        try:
            dia = int(request.POST.get('dia', dia or 0))
            if dia < 1 or dia > 31:
                dia = None
            else:
                # Verificar se o dia passou
                if mes and ano:
                    data_dia = date(ano, mes, dia)
                    if data_dia < hoje:
                        dia_passado = True
                        messages.error(request, 'Não é possível editar dias que já passaram.')
                        return redirect(f"{request.path}?mes={mes}&ano={ano}")
        except (TypeError, ValueError):
            dia = None
        
        # Verificar se é cancelamento de lançamento
        if request.POST.get('cancelar_lancamento'):
            if mes and ano and dia:
                primeiro_dia_mes = date(ano, mes, 1)
                dia_post = int(request.POST.get('dia', dia))
                data_dia = date(ano, mes, dia_post)
                
                # Não permitir cancelar lançamento de dias passados
                if data_dia < hoje:
                    messages.error(request, 'Não é possível cancelar lançamento de dias que já passaram.')
                    return redirect(f"{request.path}?mes={mes}&ano={ano}")
                
                try:
                    agenda_mes_obj = TBAGENDAMES.objects.get(AGE_MES=primeiro_dia_mes)
                    agenda_existente = TBITEAGENDAMES.objects.get(AGE_ITE_MES=agenda_mes_obj, AGE_ITE_DIA=dia_post)
                    agenda_existente.AGE_ITE_MODELO = 0
                    agenda_existente.save()
                    messages.success(request, 'Lançamento cancelado com sucesso!')
                except (TBAGENDAMES.DoesNotExist, TBITEAGENDAMES.DoesNotExist):
                    messages.error(request, 'Erro ao cancelar lançamento.')
                
                return redirect(f"{request.path}?mes={mes}&ano={ano}")
        
        # Salvamento/edição normal
        if mes and ano and dia:
            primeiro_dia_mes = date(ano, mes, 1)
            dia_post = dia or int(request.POST.get('dia', 0) or 0)
            
            # Garantir que o master existe
            agenda_mes_obj, _ = TBAGENDAMES.objects.get_or_create(AGE_MES=primeiro_dia_mes)
            
            # Ler valores diretamente do POST para evitar falhas de validação do form
            modelo_raw = request.POST.get('modelo')
            horario_raw = request.POST.get('horario', '')
            encargos = request.POST.get('encargos', '')
            
            # Converter modelo para inteiro/None/0
            modelo_id = None
            if modelo_raw is not None and modelo_raw != '':
                if modelo_raw == '0':
                    modelo_id = 0
                else:
                    try:
                        modelo_id = int(modelo_raw)
                    except ValueError:
                        modelo_id = None
            
            # Se continuou None, gravar como 0 para não ficar NULL no banco
            if modelo_id is None:
                modelo_id = 0
            
            # Converter horário
            horario_obj = None
            if horario_raw:
                try:
                    from datetime import datetime
                    horario_obj = datetime.strptime(horario_raw, '%H:%M').time()
                except (ValueError, TypeError):
                    horario_obj = None
            
            # Verificar se é criação ou edição
            try:
                agenda_existente = TBITEAGENDAMES.objects.get(AGE_ITE_MES=agenda_mes_obj, AGE_ITE_DIA=dia_post)
                # Edição
                agenda_existente.AGE_ITE_MODELO = modelo_id
                agenda_existente.AGE_ITE_HORARIO = horario_obj
                agenda_existente.AGE_ITE_ENCARGOS = encargos
                agenda_existente.save()
                messages.success(request, 'Agenda atualizada com sucesso!')
            except TBITEAGENDAMES.DoesNotExist:
                # Criação
                TBITEAGENDAMES.objects.create(
                    AGE_ITE_MES=agenda_mes_obj,
                    AGE_ITE_DIA=dia_post,
                    AGE_ITE_MODELO=modelo_id,
                    AGE_ITE_HORARIO=horario_obj,
                    AGE_ITE_ENCARGOS=encargos
                )
                messages.success(request, 'Agenda criada com sucesso!')
            
            # Redirecionar para o calendário
            return redirect(f"{request.path}?mes={mes}&ano={ano}")
    
    # Gerar calendário do mês (só se mês/ano foram informados)
    calendario = []
    dias_com_agenda = set()
    agendas_mes_detalhes = {}
    
    if mes and ano:
        primeiro_dia_mes = date(ano, mes, 1)
        ultimo_dia_num = monthrange(ano, mes)[1]
        # Configurar calendário para começar no domingo
        setfirstweekday(SUNDAY)
        calendario = monthcalendar(ano, mes)
        
        # Buscar todas as agendas do mês
        if agenda_mes_obj:
            itens_agenda = TBITEAGENDAMES.objects.filter(AGE_ITE_MES=agenda_mes_obj)
            dias_com_agenda = set(itens_agenda.values_list('AGE_ITE_DIA', flat=True))
            
            # Buscar detalhes para exibir nos botões
            for item in itens_agenda:
                modelo_nome = None
                modelo_id = item.AGE_ITE_MODELO if item.AGE_ITE_MODELO else 0
                if item.AGE_ITE_MODELO:
                    try:
                        modelo_obj = TBMODELO.objects.get(pk=item.AGE_ITE_MODELO)
                        modelo_nome = modelo_obj.MOD_DESCRICAO
                    except TBMODELO.DoesNotExist:
                        pass
                agendas_mes_detalhes[item.AGE_ITE_DIA] = {
                    'tem_agenda': True,
                    'tem_modelo': bool(item.AGE_ITE_MODELO),
                    'modelo_nome': modelo_nome,
                    'modelo_id': modelo_id,
                    'agenda_id': item.AGE_ITE_ID
                }
    
    # Formulário de seleção de mês/ano
    form_mes = AgendaMesForm(initial={'mes': mes, 'ano': ano} if mes and ano else {})
    
    # Formulário de dia (se estiver em modo inclusão/edição)
    form_dia = None
    modelo_obj = None
    if acao in ['incluir', 'editar'] and dia and agenda_mes_obj:
        if agenda_dia:
            # Modo edição - buscar modelo pelo ID
            if agenda_dia.AGE_ITE_MODELO:
                try:
                    modelo_obj = TBMODELO.objects.get(pk=agenda_dia.AGE_ITE_MODELO)
                except TBMODELO.DoesNotExist:
                    modelo_obj = None
            form_dia = AgendaDiaForm(initial={
                'modelo': modelo_obj,
                'horario': agenda_dia.AGE_ITE_HORARIO,
                'encargos': agenda_dia.AGE_ITE_ENCARGOS
            })
        else:
            # Modo inclusão
            form_dia = AgendaDiaForm()
    
    # Nomes dos meses
    meses = [
        '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    
    # Buscar modelo do dia selecionado para exibir
    modelo_dia_selecionado = None
    if agenda_dia and agenda_dia.AGE_ITE_MODELO:
        try:
            modelo_dia_selecionado = TBMODELO.objects.get(pk=agenda_dia.AGE_ITE_MODELO)
        except TBMODELO.DoesNotExist:
            pass
    
    # Buscar todos os modelos para o select
    modelos = TBMODELO.objects.all().order_by('MOD_DESCRICAO')
    
    # Converter modelos para JSON para uso no JavaScript
    import json
    modelos_json = json.dumps([{'id': m.MOD_ID, 'descricao': m.MOD_DESCRICAO} for m in modelos])
    
    # Verificar se dia selecionado passou (se ainda não foi verificado)
    if dia and mes and ano and not dia_passado:
        data_dia = date(ano, mes, dia)
        if data_dia < hoje:
            dia_passado = True
    
    context = {
        'form_mes': form_mes,
        'form_dia': form_dia,
        'mes': mes,
        'ano': ano,
        'mes_nome': meses[mes] if mes else '',
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
        'primeiro_dia_mes': date(ano, mes, 1) if mes and ano else None,
        'mes_existe': agenda_mes_obj is not None if mes and ano else False,
        'dia_passado': dia_passado,
    }
    
    return render(request, 'admin_area/tpl_agenda_mes.html', context)


@login_required
def excluir_agenda_dia(request, agenda_id):
    """
    Excluir agenda de um dia
    """
    agenda_item = get_object_or_404(TBITEAGENDAMES, pk=agenda_id)
    mes = agenda_item.AGE_ITE_MES.AGE_MES.month
    ano = agenda_item.AGE_ITE_MES.AGE_MES.year
    agenda_item.delete()
    messages.success(request, 'Agenda excluída com sucesso!')
    return redirect(f"{reverse('app_igreja:agenda_mes')}?mes={mes}&ano={ano}")


@login_required
def buscar_encargos_modelo(request, modelo_id):
    """
    Retorna os encargos de um modelo via AJAX
    """
    try:
        modelo = get_object_or_404(TBMODELO, pk=modelo_id)
        itens = TBITEM_MODELO.objects.filter(ITEM_MOD_MODELO=modelo).order_by('ITEM_MOD_ID')
        
        encargos = []
        for item in itens:
            encargos.append({
                'encargo': item.ITEM_MOD_ENCARGO,
                'ocorrencias': item.ITEM_MOD_OCORRENCIA
            })
        
        return JsonResponse({
            'success': True,
            'encargos': encargos
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
