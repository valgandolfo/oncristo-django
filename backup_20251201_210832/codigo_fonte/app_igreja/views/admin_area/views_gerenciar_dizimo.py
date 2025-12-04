"""
==================== VIEWS DE GERENCIAMENTO DE DÍZIMOS ====================
Views para gerenciar mensalidades de dizimistas
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q, F
from datetime import date, datetime, timedelta
import calendar
from ...models.area_admin.models_dizimistas import TBDIZIMISTAS, TBGERDIZIMO
from ...forms.area_admin.forms_gerenciar_dizimo import GerarMensalidadeDizimoForm, BuscarColetaDizimoForm, BaixarDizimoForm


def gerar_mensalidade_dizimo_form(request):
    """
    Formulário para selecionar mês, ano e dizimista para gerar mensalidades.
    """
    if request.method == 'POST':
        form = GerarMensalidadeDizimoForm(request.POST)
        if form.is_valid():
            mes = form.cleaned_data['mes']
            ano = form.cleaned_data['ano']
            dizimista = form.cleaned_data.get('dizimista')
            
            # Redirecionar para a função que gera as mensalidades
            if dizimista:
                return redirect(reverse('app_igreja:gerar_mensalidade_dizimo', args=[mes, ano, dizimista.pk]))
            else:
                return redirect(reverse('app_igreja:gerar_mensalidade_dizimo', args=[mes, ano, 0]))
    else:
        form = GerarMensalidadeDizimoForm()
    
    context = {
        'form': form,
        'modo': 'form_gerar',
        'title': 'Gerar Mensalidades de Dizimistas',
    }
    
    return render(request, 'admin_area/tpl_gerar_mensalidade_dizimo.html', context)


def gerar_mensalidade_dizimo(request, mes, ano, dizimista_id):
    """
    Gera as mensalidades de dizimistas para o mês/ano selecionado.
    Cria registros na tabela TBGERDIZIMO.
    """
    try:
        # Converter dizimista_id para inteiro
        dizimista_id = int(dizimista_id)
        
        # Data de referência (primeiro dia do mês)
        data_referencia = date(ano, mes, 1)
        
        # Verificar se já existem mensalidades para este mês/ano
        mensalidades_existentes = TBGERDIZIMO.objects.filter(
            GER_mesano=data_referencia
        )
        
        if dizimista_id > 0:
            # Gerar apenas para um dizimista específico
            dizimista = get_object_or_404(TBDIZIMISTAS, DIS_id=dizimista_id)
            mensalidades_existentes = mensalidades_existentes.filter(GER_dizimista=dizimista)
            
            # Verificar se já existe para este dizimista
            if mensalidades_existentes.exists():
                messages.warning(request, f'Já existe mensalidade gerada para {dizimista.DIS_nome} em {mes}/{ano}.')
                return redirect('app_igreja:gerar_mensalidade_dizimo_form')
            
            # Gerar mensalidade para este dizimista
            mensalidade_criada = criar_mensalidade_dizimista(dizimista, mes, ano, data_referencia)
            
            if mensalidade_criada:
                mensagem_sucesso = f'Mensalidade gerada com sucesso para {dizimista.DIS_nome}!'
            else:
                messages.error(request, f'Erro ao gerar mensalidade para {dizimista.DIS_nome}.')
                return redirect('app_igreja:gerar_mensalidade_dizimo_form')
        else:
            # Gerar para todos os dizimistas ativos
            dizimistas = TBDIZIMISTAS.objects.filter(DIS_status=True)
            
            if not dizimistas.exists():
                messages.warning(request, 'Não há dizimistas ativos cadastrados.')
                return redirect('app_igreja:gerar_mensalidade_dizimo_form')
            
            mensalidades_criadas = 0
            mensalidades_ignoradas = 0
            
            for dizimista in dizimistas:
                # Verificar se já existe
                if mensalidades_existentes.filter(GER_dizimista=dizimista).exists():
                    mensalidades_ignoradas += 1
                    continue
                
                if criar_mensalidade_dizimista(dizimista, mes, ano, data_referencia):
                    mensalidades_criadas += 1
            
            if mensalidades_criadas > 0:
                mensagem_sucesso = f'{mensalidades_criadas} mensalidades geradas com sucesso!'
                if mensalidades_ignoradas > 0:
                    mensagem_sucesso += f' ({mensalidades_ignoradas} já existiam e foram ignoradas)'
            else:
                messages.warning(request, 'Nenhuma mensalidade foi gerada. Todas já existem ou ocorreu um erro.')
                return redirect('app_igreja:gerar_mensalidade_dizimo_form')
        
        # Redirecionar para página de sucesso
        context = {
            'mensagem': mensagem_sucesso,
            'mes': mes,
            'ano': ano,
            'modo': 'sucesso_geracao',
            'title': 'Mensalidades Geradas com Sucesso',
        }
        return render(request, 'admin_area/tpl_gerar_mensalidade_dizimo.html', context)
        
    except Exception as e:
        messages.error(request, f'Erro ao gerar mensalidades: {str(e)}')
        return redirect('app_igreja:gerar_mensalidade_dizimo_form')


def criar_mensalidade_dizimista(dizimista, mes, ano, data_referencia):
    """
    Cria uma mensalidade para um dizimista específico.
    Usa o dia de pagamento do dizimista para calcular a data de vencimento.
    """
    try:
        # Obter dia de pagamento do dizimista (ou usar dia 10 como padrão)
        dia_pagamento = dizimista.DIS_dia_pagamento if dizimista.DIS_dia_pagamento else 10
        
        # Calcular data de vencimento (dia de pagamento do mês/ano)
        # Verificar se o dia existe no mês (ex: 31 de fevereiro não existe)
        ultimo_dia_mes = calendar.monthrange(ano, mes)[1]
        if dia_pagamento > ultimo_dia_mes:
            dia_pagamento = ultimo_dia_mes
        
        data_vencimento = date(ano, mes, dia_pagamento)
        
        # Obter valor do dízimo (ou usar 0 como padrão)
        valor_dizimo = dizimista.DIS_valor if dizimista.DIS_valor else 0
        
        # Criar registro na tabela TBGERDIZIMO
        mensalidade = TBGERDIZIMO.objects.create(
            GER_mesano=data_referencia,
            GER_dizimista=dizimista,
            GER_dtvencimento=data_vencimento,
            GER_vlr_dizimo=valor_dizimo,
            GER_dtpagto=None,
            GER_vlr_pago=None
        )
        
        return True
    except Exception as e:
        print(f"Erro ao criar mensalidade para {dizimista.DIS_nome}: {str(e)}")
        return False


def gerenciar_coleta_dizimo(request):
    """
    View principal para gerenciar coletas de dízimos.
    Permite buscar, filtrar e baixar mensalidades.
    Usa GET para busca (como gerenciar escala).
    """
    # Buscar parâmetros da query string (GET)
    mes = request.GET.get('mes', '')
    ano = request.GET.get('ano', '')
    dizimista_id = request.GET.get('dizimista', '')
    status = request.GET.get('status', 'TODOS')
    
    # Inicializar variáveis
    sem_filtro = True
    mensalidades = TBGERDIZIMO.objects.none()
    
    # Se não tiver parâmetros, mostrar apenas o formulário (sem busca automática)
    if not mes or not ano:
        # Preencher mês e ano atual por padrão
        hoje = date.today()
        form = BuscarColetaDizimoForm(initial={'mes': hoje.month, 'ano': hoje.year})
        mes = hoje.month  # Para o template
        ano = hoje.year  # Para o template
    else:
        # Processar busca
        try:
            mes = int(mes)
            ano = int(ano)
            
            # Validar mês e ano
            if mes < 1 or mes > 12:
                messages.error(request, 'Mês inválido. Use valores entre 1 e 12.')
                form = BuscarColetaDizimoForm()
                sem_filtro = True
            elif ano < 2000 or ano > 2100:
                messages.error(request, 'Ano inválido.')
                form = BuscarColetaDizimoForm()
                sem_filtro = True
            else:
                # Buscar mensalidades
                data_referencia = date(ano, mes, 1)
                mensalidades = TBGERDIZIMO.objects.filter(
                    GER_mesano=data_referencia
                ).select_related('GER_dizimista')
                
                # Filtro por dizimista
                if dizimista_id:
                    try:
                        dizimista = TBDIZIMISTAS.objects.get(pk=int(dizimista_id))
                        mensalidades = mensalidades.filter(GER_dizimista=dizimista)
                    except (ValueError, TBDIZIMISTAS.DoesNotExist):
                        pass
                
                # Filtro por status
                if status == 'PAGOS':
                    # Filtrar pagos: valor pago >= valor dízimo
                    mensalidades_list = list(mensalidades)
                    ids_pagos = [m.GER_id for m in mensalidades_list if m.GER_vlr_pago and m.GER_vlr_pago >= m.GER_vlr_dizimo]
                    if ids_pagos:
                        mensalidades = TBGERDIZIMO.objects.filter(GER_id__in=ids_pagos).select_related('GER_dizimista')
                    else:
                        mensalidades = TBGERDIZIMO.objects.none()
                elif status == 'EM_ABERTO':
                    mensalidades = mensalidades.filter(GER_vlr_pago__isnull=True)
                elif status == 'PARCIAL':
                    # Filtrar parciais: valor pago > 0 e < valor dízimo
                    mensalidades_list = list(mensalidades)
                    ids_parciais = [m.GER_id for m in mensalidades_list if m.GER_vlr_pago and m.GER_vlr_pago > 0 and m.GER_vlr_pago < m.GER_vlr_dizimo]
                    if ids_parciais:
                        mensalidades = TBGERDIZIMO.objects.filter(GER_id__in=ids_parciais).select_related('GER_dizimista')
                    else:
                        mensalidades = TBGERDIZIMO.objects.none()
                
                mensalidades = mensalidades.order_by('GER_dtvencimento', 'GER_dizimista__DIS_nome')
                sem_filtro = False
                
                # Inicializar form com valores
                form_data = {
                    'mes': mes,
                    'ano': ano,
                }
                if dizimista_id:
                    form_data['dizimista'] = int(dizimista_id)
                form = BuscarColetaDizimoForm(initial=form_data)
        except (ValueError, TypeError):
            messages.error(request, 'Parâmetros inválidos.')
            form = BuscarColetaDizimoForm()
            sem_filtro = True
    
    context = {
        'form': form,
        'mensalidades': mensalidades,
        'status_atual': status,
        'mes': mes if mes else '',
        'ano': ano if ano else '',
        'dizimista_id': dizimista_id,
        'sem_filtro': sem_filtro,
        'modo': 'gerenciar_coleta',
        'modo_dashboard': True,  # Ativar modo dashboard para usar os blocos corretos
        'title': 'Gerenciar Coleta Dízimo',
    }
    
    return render(request, 'admin_area/tpl_gerenciar_coleta_dizimo.html', context)


def baixar_dizimo(request):
    """
    Registra o pagamento de uma mensalidade
    """
    if request.method == 'POST':
        mensalidade_id = request.POST.get('mensalidade_id')
        form = BaixarDizimoForm(request.POST)
        
        if form.is_valid() and mensalidade_id:
            try:
                mensalidade = get_object_or_404(TBGERDIZIMO, GER_id=mensalidade_id)
                data_pagamento = form.cleaned_data['data_pagamento']
                valor_pago = form.cleaned_data['valor_pago']
                observacao = form.cleaned_data.get('observacao', '')
                
                mensalidade.GER_dtpagto = data_pagamento
                mensalidade.GER_vlr_pago = valor_pago
                mensalidade.GER_observacao = observacao
                mensalidade.save()
                
                messages.success(request, f'Mensalidade baixada com sucesso!')
            except Exception as e:
                messages.error(request, f'Erro ao baixar mensalidade: {str(e)}')
        else:
            messages.error(request, 'Erro ao baixar mensalidade. Verifique os dados informados.')
    
    # Redirecionar mantendo os filtros (pegar da referer ou GET)
    referer = request.META.get('HTTP_REFERER', '')
    if referer and '?' in referer:
        params = referer.split('?')[1]
        return redirect(f"{reverse('app_igreja:gerenciar_coleta_dizimo')}?{params}")
    else:
        # Tentar pegar dos GET params
        mes = request.GET.get('mes', '')
        ano = request.GET.get('ano', '')
        dizimista = request.GET.get('dizimista', '')
        status = request.GET.get('status', 'TODOS')
        
        params = []
        if mes: params.append(f'mes={mes}')
        if ano: params.append(f'ano={ano}')
        if dizimista: params.append(f'dizimista={dizimista}')
        if status: params.append(f'status={status}')
        
        url = reverse('app_igreja:gerenciar_coleta_dizimo')
        if params:
            url += '?' + '&'.join(params)
        
        return redirect(url)


def cancelar_baixa(request):
    """
    Cancela o pagamento de uma mensalidade (remove data e valor pago)
    """
    if request.method == 'POST':
        mensalidade_id = request.POST.get('mensalidade_id')
        
        if mensalidade_id:
            try:
                mensalidade = get_object_or_404(TBGERDIZIMO, GER_id=mensalidade_id)
                mensalidade.GER_dtpagto = None
                mensalidade.GER_vlr_pago = None
                mensalidade.GER_observacao = None
                mensalidade.save()
                
                messages.success(request, 'Baixa cancelada com sucesso!')
            except Exception as e:
                messages.error(request, f'Erro ao cancelar baixa: {str(e)}')
        else:
            messages.error(request, 'Mensalidade não informada.')
    
    # Redirecionar mantendo os filtros (pegar da referer ou GET)
    referer = request.META.get('HTTP_REFERER', '')
    if referer and '?' in referer:
        params = referer.split('?')[1]
        return redirect(f"{reverse('app_igreja:gerenciar_coleta_dizimo')}?{params}")
    else:
        # Tentar pegar dos GET params
        mes = request.GET.get('mes', '')
        ano = request.GET.get('ano', '')
        dizimista = request.GET.get('dizimista', '')
        status = request.GET.get('status', 'TODOS')
        
        params = []
        if mes: params.append(f'mes={mes}')
        if ano: params.append(f'ano={ano}')
        if dizimista: params.append(f'dizimista={dizimista}')
        if status: params.append(f'status={status}')
        
        url = reverse('app_igreja:gerenciar_coleta_dizimo')
        if params:
            url += '?' + '&'.join(params)
        
        return redirect(url)


def listar_mensalidades_dizimo(request, mes=None, ano=None):
    """
    Lista as mensalidades de dizimistas (master/detail).
    Permite filtrar por mês/ano.
    """
    # Se não foram passados mês/ano, usar o mês/ano atual
    if not mes or not ano:
        hoje = date.today()
        mes = hoje.month
        ano = hoje.year
    
    # Data de referência (primeiro dia do mês)
    data_referencia = date(ano, mes, 1)
    
    # Buscar todas as mensalidades do mês/ano
    mensalidades = TBGERDIZIMO.objects.filter(
        GER_mesano=data_referencia
    ).select_related('GER_dizimista').order_by('GER_dizimista__DIS_nome', 'GER_dtvencimento')
    
    # Estatísticas
    total_mensalidades = mensalidades.count()
    
    # Contar pagos (valor pago >= valor dízimo)
    total_pago = 0
    for m in mensalidades:
        if m.GER_vlr_pago and m.GER_vlr_pago >= m.GER_vlr_dizimo:
            total_pago += 1
    
    # Contar parciais (valor pago > 0 e < valor dízimo)
    total_parcial = 0
    for m in mensalidades:
        if m.GER_vlr_pago and m.GER_vlr_pago > 0 and m.GER_vlr_pago < m.GER_vlr_dizimo:
            total_parcial += 1
    
    # Contar atrasados (vencimento < hoje e não pago)
    hoje = date.today()
    total_atrasado = 0
    for m in mensalidades:
        if m.GER_dtvencimento < hoje and (not m.GER_vlr_pago or m.GER_vlr_pago < m.GER_vlr_dizimo):
            total_atrasado += 1
    
    # Contar pendentes (vencimento >= hoje e não pago)
    total_pendente = 0
    for m in mensalidades:
        if m.GER_dtvencimento >= hoje and (not m.GER_vlr_pago or m.GER_vlr_pago < m.GER_vlr_dizimo):
            total_pendente += 1
    
    # Valores
    valor_total_esperado = sum(m.GER_vlr_dizimo for m in mensalidades)
    valor_total_pago = sum(m.GER_vlr_pago for m in mensalidades if m.GER_vlr_pago)
    
    context = {
        'mensalidades': mensalidades,
        'mes': mes,
        'ano': ano,
        'data_referencia': data_referencia,
        'total_mensalidades': total_mensalidades,
        'total_pago': total_pago,
        'total_parcial': total_parcial,
        'total_atrasado': total_atrasado,
        'total_pendente': total_pendente,
        'valor_total_esperado': valor_total_esperado,
        'valor_total_pago': valor_total_pago,
        'modo': 'listagem',
        'title': f'Mensalidades de Dizimistas - {mes}/{ano}',
    }
    
    return render(request, 'admin_area/tpl_gerar_mensalidade_dizimo.html', context)

