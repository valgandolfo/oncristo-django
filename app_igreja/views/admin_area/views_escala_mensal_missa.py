from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from datetime import date, datetime, timedelta
import calendar
from ...models.area_admin.models_paroquias import TBPAROQUIA
from ...models.area_admin.models_escala import TBESCALA, TBITEM_ESCALA
from ...models.area_admin.models_modelo import TBITEM_MODELO, OCORRENCIA_DICT
from ...forms.area_admin.forms_escala_mensal_missa import EscalaMensalMissaForm, EditarDescricaoEscalaMissaForm


def escala_mensal_form(request):
    """
    Formulário para selecionar mês, ano, modelo e tema para gerar escala mensal.
    """
    if request.method == 'POST':
        form = EscalaMensalMissaForm(request.POST)
        if form.is_valid():
            mes = form.cleaned_data['mes']
            ano = form.cleaned_data['ano']
            modelo = form.cleaned_data['modelo']
            tema_mes = form.cleaned_data.get('tema_mes', '')
            
            # Gerar escala mensal
            modelo_id = modelo.MOD_ID
            tema_mes_valor = form.cleaned_data.get('tema_mes', '')
            from urllib.parse import urlencode
            params = urlencode({'modelo_id': modelo_id, 'tema_mes': tema_mes_valor})
            return redirect(f"{reverse('app_igreja:escala_mensal_gerar', args=[mes, ano])}?{params}")
    else:
        form = EscalaMensalMissaForm()
    
    context = {
        'form': form,
        'modo': 'form',
        'title': 'Gerar Escala de Missa',
    }
    
    return render(request, 'admin_area/tpl_escala_mensal_missa.html', context)


def escala_mensal_gerar(request, mes, ano):
    """
    Gera a escala mensal baseada no modelo selecionado.
    Cria o registro master (TBESCALA) e os registros detail (TBITEM_ESCALA) para cada dia/horário/encargo.
    """
    try:
        # Buscar dados do formulário via GET (redirecionamento) ou POST
        modelo_id = request.GET.get('modelo_id') or request.POST.get('modelo_id')
        tema_mes = request.GET.get('tema_mes', '') or request.POST.get('tema_mes', '')
        
        if not modelo_id:
            error_msg = 'Modelo não informado.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax') == 'true':
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('app_igreja:escala_mensal_form')
        
        from ...models.area_admin.models_modelo import TBMODELO
        modelo = get_object_or_404(TBMODELO, pk=modelo_id)
        
        # Verificar se já existe escala para este mês/ano
        # Como ESC_MESANO é chave primária, verificar se já existe
        primeiro_dia_mes = date(ano, mes, 1)
        
        # Verificar se deve sobrepor (parâmetro do usuário)
        sobrepor = request.GET.get('sobrepor', 'false').lower() == 'true' or request.POST.get('sobrepor', 'false').lower() == 'true'
        
        # Verificar se já existe escala (chave primária)
        try:
            escala_existente = TBESCALA.objects.get(ESC_MESANO=primeiro_dia_mes)
            # Se já existe, verificar se tem itens
            itens_existentes = TBITEM_ESCALA.objects.filter(ITE_ESC_ESCALA=escala_existente).count()
            if itens_existentes > 0 and not sobrepor:
                # Se existe e tem itens, perguntar se deseja sobrepor
                meses_pt = [
                    '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
                ]
                mes_nome = meses_pt[mes]
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax') == 'true':
                    return JsonResponse({
                        'success': False,
                        'message': f'Escala já existe para {mes_nome}/{ano} com {itens_existentes} itens cadastrados.',
                        'escala_existe': True,
                        'itens_existentes': itens_existentes,
                        'mes': mes_nome,
                        'ano': ano
                    }, status=200)  # Status 200 para não ser tratado como erro
                messages.warning(request, f'Escala já existe para {mes_nome}/{ano} com {itens_existentes} itens cadastrados.')
                return redirect('app_igreja:escala_mensal_form')
            # Se sobrepor ou não tem itens, pode continuar (limpará os itens antes de gerar)
        except TBESCALA.DoesNotExist:
            pass  # Não existe, pode criar
        
        # Buscar configurações da paróquia
        paroquia = TBPAROQUIA.objects.first()
        if not paroquia:
            error_msg = 'Configurações da paróquia não encontradas.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax') == 'true':
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('app_igreja:escala_mensal_form')
        
        # Obter horários fixos do JSON
        horarios_fixos = paroquia.get_horarios_fixos()
        
        if not horarios_fixos:
            error_msg = 'Nenhum horário configurado na paróquia.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax') == 'true':
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('app_igreja:escala_mensal_form')
        
        # Mapear dias da semana em inglês para português (chave do JSON)
        dias_semana_en_to_pt = {
            'Monday': 'segunda',
            'Tuesday': 'terca',
            'Wednesday': 'quarta',
            'Thursday': 'quinta',
            'Friday': 'sexta',
            'Saturday': 'sabado',
            'Sunday': 'domingo'
        }
        
        # Mapear dias da semana em português para número (0=segunda, 6=domingo)
        dias_semana_pt_to_num = {
            'segunda': 0,
            'terca': 1,
            'quarta': 2,
            'quinta': 3,
            'sexta': 4,
            'sabado': 5,
            'domingo': 6
        }
        
        # Criar ou obter registro master (TBESCALA)
        # O modelo não é gravado, apenas usado para gerar os itens
        escala_master, created = TBESCALA.objects.get_or_create(
            ESC_MESANO=primeiro_dia_mes,
            defaults={
                'ESC_TEMAMES': tema_mes or None
            }
        )
        
        # Se já existia, atualizar o tema do mês se fornecido
        if not created and tema_mes:
            escala_master.ESC_TEMAMES = tema_mes
            escala_master.save()
        
        # Se sobrepor ou já existia, limpar os itens antigos antes de gerar novos
        if sobrepor or not created:
            TBITEM_ESCALA.objects.filter(ITE_ESC_ESCALA=escala_master).delete()
        
        # Buscar itens do modelo
        itens_modelo = TBITEM_MODELO.objects.filter(ITEM_MOD_MODELO=modelo)
        
        if not itens_modelo.exists():
            error_msg = 'O modelo selecionado não possui itens cadastrados.'
            # Não deletar a escala master, apenas os itens
            TBITEM_ESCALA.objects.filter(ITE_ESC_ESCALA=escala_master).delete()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax') == 'true':
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.warning(request, error_msg)
            return redirect('app_igreja:escala_mensal_form')
        
        # Gerar dias do mês
        dias_mes = calendar.monthrange(ano, mes)[1]
        itens_criados = 0
        
        # Para cada item do modelo
        for item_modelo in itens_modelo:
            ocorrencias = item_modelo.ocorrencias_list()
            encargo = item_modelo.ITEM_MOD_ENCARGO
            
            # Para cada dia do mês
            for dia in range(1, dias_mes + 1):
                data_escala = date(ano, mes, dia)
                dia_semana_en = data_escala.strftime('%A')
                dia_semana_key = dias_semana_en_to_pt.get(dia_semana_en)
                
                if not dia_semana_key:
                    continue
                
                # Verificar se este dia deve ter este encargo
                deve_gerar = False
                if 'todos' in ocorrencias:
                    deve_gerar = True
                elif dia_semana_key in ocorrencias:
                    deve_gerar = True
                
                if not deve_gerar:
                    continue
                
                # Obter horários para este dia da semana
                horarios_do_dia = horarios_fixos.get(dia_semana_key, [])
                
                # Se horarios_do_dia for uma string única, converter para lista
                if isinstance(horarios_do_dia, str):
                    horarios_do_dia = [horarios_do_dia]
                elif not isinstance(horarios_do_dia, list):
                    horarios_do_dia = []
                
                # Para cada horário cadastrado, criar um registro TBITEM_ESCALA
                for horario_str in horarios_do_dia:
                    if not horario_str or not horario_str.strip():
                        continue
                    
                    # Converter string de horário para time
                    try:
                        partes = horario_str.strip().split(':')
                        if len(partes) >= 2:
                            hora = int(partes[0])
                            minuto = int(partes[1])
                            horario_time = datetime.strptime(f"{hora:02d}:{minuto:02d}", "%H:%M").time()
                        else:
                            continue
                    except (ValueError, IndexError):
                        continue
                    
                    # Criar registro detail (TBITEM_ESCALA)
                    # ITE_ESC_ENCARGO agora armazena a descrição do encargo (não o ID)
                    TBITEM_ESCALA.objects.create(
                        ITE_ESC_ESCALA=escala_master,
                        ITE_ESC_DATA=data_escala,
                        ITE_ESC_HORARIO=horario_time,
                        ITE_ESC_DESCRICAO=encargo,
                        ITE_ESC_ENCARGO=encargo,  # Descrição do encargo (do modelo)
                        ITE_ESC_STATUS='EM_ABERTO'  # Status padrão: Em aberto
                    )
                    itens_criados += 1
        
        # Nome do mês em português
        meses_pt = [
            '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        mes_nome = meses_pt[mes]
        
        # Se for requisição AJAX, retornar JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax') == 'true':
            return JsonResponse({
                'success': True,
                'message': f'Escala mensal gerada com sucesso!',
                'registros_gerados': itens_criados,
                'mes': mes_nome,
                'ano': ano
            })
        
        messages.success(request, f'Escala mensal gerada com sucesso! {itens_criados} itens criados.')
        return redirect('app_igreja:admin_area')
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        # Se for requisição AJAX, retornar JSON com erro
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax') == 'true':
            return JsonResponse({
                'success': False,
                'message': f'Erro ao gerar escala mensal: {str(e)}'
            }, status=500)
        
        messages.error(request, f'Erro ao gerar escala mensal: {str(e)}')
        return redirect('app_igreja:escala_mensal_form')


def escala_mensal_visualizar(request, mes, ano):
    """
    Visualiza a escala mensal.
    """
    # Buscar escala master do mês
    primeiro_dia_mes = date(ano, mes, 1)
    escala_master = TBESCALA.objects.filter(ESC_MESANO=primeiro_dia_mes).first()
    
    if not escala_master:
        messages.info(request, f'Nenhuma escala encontrada para {mes}/{ano}.')
        return redirect('app_igreja:escala_mensal_form')
    
    # Buscar itens da escala
    itens_escala = TBITEM_ESCALA.objects.filter(
        ITE_ESC_ESCALA=escala_master
    ).order_by('ITE_ESC_DATA', 'ITE_ESC_HORARIO', 'ITE_ESC_DESCRICAO')
    
    # Organizar por dia e adicionar nome do dia da semana
    dias_missas = {}
    dias_semana_pt = {
        0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira', 3: 'Quinta-feira',
        4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo'
    }
    
    for item in itens_escala:
        dia = item.ITE_ESC_DATA.day
        if dia not in dias_missas:
            dias_missas[dia] = []
        # Adicionar atributo dinâmico com nome do dia
        item.dia_semana_nome = dias_semana_pt.get(item.ITE_ESC_DATA.weekday(), '')
        dias_missas[dia].append(item)
    
    # Nome do mês em português
    meses_pt = [
        '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    mes_nome = meses_pt[mes]
    
    context = {
        'escala_master': escala_master,
        'dias_missas': dias_missas,
        'mes': mes,
        'ano': ano,
        'mes_nome': mes_nome,
        'modo': 'visualizar',
        'title': f'Escala Mensal - {mes_nome}/{ano}',
    }
    
    return render(request, 'admin_area/tpl_escala_mensal_missa.html', context)


def escala_mensal_editar_descricao(request, pk):
    """
    Edita a descrição de um item da escala específico.
    """
    item_escala = get_object_or_404(TBITEM_ESCALA, pk=pk)
    
    if request.method == 'POST':
        form = EditarDescricaoEscalaMissaForm(request.POST)
        if form.is_valid():
            item_escala.ITE_ESC_DESCRICAO = form.cleaned_data['descricao']
            item_escala.save()
            messages.success(request, 'Descrição do item atualizada com sucesso!')
            return redirect('app_igreja:escala_mensal_visualizar', 
                          mes=item_escala.ITE_ESC_DATA.month, ano=item_escala.ITE_ESC_DATA.year)
    else:
        form = EditarDescricaoEscalaMissaForm(initial={'descricao': item_escala.ITE_ESC_DESCRICAO})
    
    # Dia da semana em português
    dias_semana_pt = {
        0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira', 3: 'Quinta-feira',
        4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo'
    }
    dia_semana = dias_semana_pt[item_escala.ITE_ESC_DATA.weekday()]
    
    context = {
        'form': form,
        'item_escala': item_escala,
        'dia_semana': dia_semana,
        'modo': 'editar_descricao',
        'title': 'Editar Descrição do Item',
    }
    
    return render(request, 'admin_area/tpl_escala_mensal_missa.html', context)
