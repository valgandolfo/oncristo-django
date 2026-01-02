"""
==================== VIEWS MASTER-DETAIL EVENTOS ====================
Views para CRUD Master-Detail de Eventos e Itens do Evento
Estrutura genérica e reutilizável para outros master-detail
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.db.models import Q

from app_igreja.models.area_admin.models_eventos import TBEVENTO, TBITEM_EVENTO


def grava_item_evento(evento, data_inicial, acao, data_final, hora_inicial, hora_final):
    """
    Função unificada para gravar item de evento
    Retorna dict com success, message
    """
    try:
        if not all([data_inicial, hora_inicial, acao]):
            return {
                'success': False,
                'message': 'Dados do item incompletos!'
            }
        
        item = TBITEM_EVENTO.objects.create(
            ITEM_EVE_EVENTO=evento,
            ITEM_EVE_DATA_INICIAL=data_inicial,
            ITEM_EVE_ACAO=acao,
            ITEM_EVE_DATA_FINAL=data_final,
            ITEM_EVE_HORA_INICIAL=hora_inicial,
            ITEM_EVE_HORA_FINAL=hora_final
        )
        
        return {
            'success': True,
            'message': 'Item adicionado com sucesso!',
            'item_id': item.ITEM_EVE_ID
        }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Erro ao criar item: {str(e)}'
        }


@method_decorator(login_required, name='dispatch')
class MasterDetailEventoListView(View):
    """
    View para listar eventos Master-Detail
    """
    
    def get(self, request):
        # Busca e Filtros
        busca = request.GET.get('busca', '').strip()
        status = request.GET.get('status', '').strip()
        
        # Controla se o usuário já executou uma busca (preencheu algum filtro ou navegou na paginação)
        busca_realizada = bool(busca or status or request.GET.get('page'))
        
        # Só carrega os registros no grid DEPOIS que o usuário aplicar um filtro
        if busca_realizada:
            eventos = TBEVENTO.objects.all().order_by('-EVE_DTCADASTRO')
            
            # Se digitar "todos" ou "todas", ignora outros filtros e traz tudo
            if busca.lower() in ['todos', 'todas']:
                # Mantém todos os registros sem filtros adicionais
                pass
            else:
                if busca:
                    eventos = eventos.filter(EVE_TITULO__icontains=busca)
                
                if status:
                    eventos = eventos.filter(EVE_STATUS=status)
        else:
            # Queryset vazio até que o usuário faça a primeira busca
            eventos = TBEVENTO.objects.none()
        
        # Paginação
        paginator = Paginator(eventos, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Estatísticas
        total_eventos = TBEVENTO.objects.count()
        ativos = TBEVENTO.objects.filter(EVE_STATUS='Ativo').count()
        inativos = TBEVENTO.objects.filter(EVE_STATUS='Inativo').count()
        
        context = {
            'page_obj': page_obj,
            'busca': busca,
            'status': status,
            'total_eventos': total_eventos,
            'ativos': ativos,
            'inativos': inativos,
            'modo_dashboard': True,
            'model_verbose_name': 'Evento',
            'master_detail_mode': True,  # Flag para identificar modo master-detail
            'eventos_section': 'list',  # Seção: listagem
            'busca_realizada': busca_realizada,
        }
        
        return render(request, 'admin_area/tpl_eventos.html', context)


@method_decorator(login_required, name='dispatch')
class MasterDetailEventoView(View):
    """
    View para exibir detalhes de um evento específico com seus itens
    """
    
    def get(self, request, pk):
        evento = get_object_or_404(TBEVENTO, pk=pk)
        itens = evento.itens.all().order_by('ITEM_EVE_DATA_INICIAL', 'ITEM_EVE_HORA_INICIAL')
        confirmar_exclusao = request.GET.get('confirmar_exclusao', False)
        
        context = {
            'evento': evento,
            'itens': itens,
            'confirmar_exclusao': confirmar_exclusao,
            'page_title': f'Evento: {evento.EVE_TITULO}',
            'return_url': request.GET.get('return_url', ''),
            'eventos_section': 'view',  # Seção: visualização master-detail
        }
        
        return render(request, 'admin_area/tpl_eventos.html', context)


@method_decorator(login_required, name='dispatch')
class MasterDetailCreateView(View):
    """
    View unificada para criar e manter registros Master-Detail
    """
    
    def get(self, request, pk=None):
        """Exibe formulário de criação ou manutenção"""
        from app_igreja.models.area_admin.models_celebrantes import TBCELEBRANTES
        
        evento = None
        itens = []
        modo_manutencao = False
        
        # Verificar se há evento_id na URL (modo criação após criar evento)
        evento_id_url = request.GET.get('evento_id')
        
        if pk:
            # Modo manutenção: carregar evento existente
            evento = get_object_or_404(TBEVENTO, pk=pk)
            itens = evento.itens.all().order_by('ITEM_EVE_DATA_INICIAL', 'ITEM_EVE_HORA_INICIAL')
            modo_manutencao = True
        elif evento_id_url:
            # Modo criação após criar evento: carregar evento criado
            evento = get_object_or_404(TBEVENTO, pk=evento_id_url)
            itens = evento.itens.all().order_by('ITEM_EVE_DATA_INICIAL', 'ITEM_EVE_HORA_INICIAL')
            modo_manutencao = True
        
        # Buscar celebrantes ativos para o select
        celebrantes = TBCELEBRANTES.objects.filter(CEL_ativo=True).order_by('CEL_nome_celebrante')
        
        context = {
            'page_title': f'Manutenção Evento: {evento.EVE_TITULO}' if evento else 'Novo Evento',
            'evento': evento,
            'itens': itens,
            'celebrantes': celebrantes,
            'modo_manutencao': modo_manutencao,
            'return_url': request.GET.get('return_url', ''),
            'eventos_section': 'crud',  # Seção: CRUD master-detail
        }
        
        return render(request, 'admin_area/tpl_eventos.html', context)
    
    def post(self, request, pk=None):
        """Processa criação ou manutenção do evento"""
        try:
            action = request.POST.get('action')
            
            if action == 'atualizar_evento' and pk:
                # Atualizar dados do evento existente
                from app_igreja.models.area_admin.models_celebrantes import TBCELEBRANTES
                
                evento = get_object_or_404(TBEVENTO, pk=pk)
                
                # Validar campos obrigatórios
                titulo_evento = request.POST.get('EVE_TITULO')
                tipo = request.POST.get('EVE_TIPO')
                dt_inicial = request.POST.get('EVE_DT_INICIAL')
                status = request.POST.get('EVE_STATUS', 'Ativo')
                
                if not titulo_evento or not tipo or not dt_inicial:
                    return JsonResponse({
                        'success': False,
                        'message': 'Campos obrigatórios não preenchidos!'
                    })
                
                # Atualizar todos os campos
                evento.EVE_TITULO = titulo_evento
                evento.EVE_TIPO = tipo
                evento.EVE_DESCRICAO = request.POST.get('EVE_DESCRICAO') or None
                evento.EVE_DT_INICIAL = dt_inicial
                evento.EVE_DT_FINAL = request.POST.get('EVE_DT_FINAL') or None
                evento.EVE_HORA_INICIAL = request.POST.get('EVE_HORA_INICIAL') or None
                evento.EVE_HORA_FINAL = request.POST.get('EVE_HORA_FINAL') or None
                evento.EVE_LOCAL = request.POST.get('EVE_LOCAL') or None
                evento.EVE_ENDERECO = request.POST.get('EVE_ENDERECO') or None
                evento.EVE_RESPONSAVEL = request.POST.get('EVE_RESPONSAVEL') or None
                
                # Celebrante
                celebrante_id = request.POST.get('EVE_CELEBRANTE')
                if celebrante_id:
                    try:
                        evento.EVE_CELEBRANTE = TBCELEBRANTES.objects.get(pk=celebrante_id)
                    except TBCELEBRANTES.DoesNotExist:
                        evento.EVE_CELEBRANTE = None
                else:
                    evento.EVE_CELEBRANTE = None
                
                # Participantes
                try:
                    evento.EVE_PARTICIPANTES = int(request.POST.get('EVE_PARTICIPANTES', 0))
                except (ValueError, TypeError):
                    evento.EVE_PARTICIPANTES = 0
                
                try:
                    evento.EVE_CONFIRMADOS = int(request.POST.get('EVE_CONFIRMADOS', 0))
                except (ValueError, TypeError):
                    evento.EVE_CONFIRMADOS = 0
                
                evento.EVE_RECURSOS = request.POST.get('EVE_RECURSOS') or None
                evento.EVE_STATUS = status
                evento.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Dados do evento atualizados com sucesso!'
                })
            
            elif action == 'adicionar_item':
                # Adicionar novo item ao evento
                evento_id = request.POST.get('evento_id') or pk
                
                if not evento_id:
                    return JsonResponse({
                        'success': False,
                        'message': 'ID do evento não fornecido!'
                    })
                
                try:
                    evento = get_object_or_404(TBEVENTO, pk=evento_id)
                except Exception as e:
                    return JsonResponse({
                        'success': False,
                        'message': f'Evento não encontrado: {str(e)}'
                    })
                
                data_inicial = request.POST.get('ITEM_EVE_DATA_INICIAL')
                acao = request.POST.get('ITEM_EVE_ACAO')
                data_final = request.POST.get('ITEM_EVE_DATA_FINAL') or None
                hora_inicial = request.POST.get('ITEM_EVE_HORA_INICIAL')
                hora_final = request.POST.get('ITEM_EVE_HORA_FINAL') or None
                
                resultado = grava_item_evento(evento, data_inicial, acao, data_final, hora_inicial, hora_final)
                
                return JsonResponse({
                    'success': resultado['success'],
                    'message': resultado['message'],
                    'item_id': resultado.get('item_id')
                })
            
            elif action == 'editar_item' and pk:
                # Editar item existente
                evento = get_object_or_404(TBEVENTO, pk=pk)
                item_id = request.POST.get('item_id')
                data_inicial = request.POST.get('ITEM_EVE_DATA_INICIAL')
                acao = request.POST.get('ITEM_EVE_ACAO')
                data_final = request.POST.get('ITEM_EVE_DATA_FINAL') or None
                hora_inicial = request.POST.get('ITEM_EVE_HORA_INICIAL')
                hora_final = request.POST.get('ITEM_EVE_HORA_FINAL') or None

                if item_id and data_inicial and hora_inicial and acao:
                    item = TBITEM_EVENTO.objects.get(ITEM_EVE_ID=item_id, ITEM_EVE_EVENTO=evento)
                    item.ITEM_EVE_DATA_INICIAL = data_inicial
                    item.ITEM_EVE_ACAO = acao
                    item.ITEM_EVE_DATA_FINAL = data_final
                    item.ITEM_EVE_HORA_INICIAL = hora_inicial
                    item.ITEM_EVE_HORA_FINAL = hora_final
                    item.save()
                    return JsonResponse({
                        'success': True,
                        'message': 'Item editado com sucesso!'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Dados do item incompletos!'
                    })
            
            elif action == 'excluir_item' and pk:
                # Excluir item
                evento = get_object_or_404(TBEVENTO, pk=pk)
                item_id = request.POST.get('item_id')

                if item_id:
                    item = TBITEM_EVENTO.objects.get(ITEM_EVE_ID=item_id, ITEM_EVE_EVENTO=evento)
                    item.delete()
                    return JsonResponse({
                        'success': True,
                        'message': 'Item excluído com sucesso!'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'ID do item não fornecido!'
                    })
            
            else:
                # Modo criação: criar novo evento
                return self._criar_novo_evento(request)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro: {str(e)}'
            })
    
    def _criar_novo_evento(self, request):
        """Método auxiliar para criar novo evento"""
        try:
            from app_igreja.models.area_admin.models_celebrantes import TBCELEBRANTES
            
            titulo_evento = request.POST.get('EVE_TITULO')
            tipo = request.POST.get('EVE_TIPO')
            dt_inicial = request.POST.get('EVE_DT_INICIAL')
            status = request.POST.get('EVE_STATUS', 'Ativo')
            
            if not titulo_evento or not tipo or not dt_inicial:
                return JsonResponse({
                    'success': False,
                    'message': 'Campos obrigatórios não preenchidos!'
                })
            
            # Celebrante
            celebrante_id = request.POST.get('EVE_CELEBRANTE')
            celebrante = None
            if celebrante_id:
                try:
                    celebrante = TBCELEBRANTES.objects.get(pk=celebrante_id)
                except TBCELEBRANTES.DoesNotExist:
                    pass
            
            # Participantes
            try:
                participantes = int(request.POST.get('EVE_PARTICIPANTES', 0))
            except (ValueError, TypeError):
                participantes = 0
            
            try:
                confirmados = int(request.POST.get('EVE_CONFIRMADOS', 0))
            except (ValueError, TypeError):
                confirmados = 0
            
            # Criar evento
            evento = TBEVENTO.objects.create(
                EVE_TITULO=titulo_evento,
                EVE_TIPO=tipo,
                EVE_DESCRICAO=request.POST.get('EVE_DESCRICAO') or None,
                EVE_DT_INICIAL=dt_inicial,
                EVE_DT_FINAL=request.POST.get('EVE_DT_FINAL') or None,
                EVE_HORA_INICIAL=request.POST.get('EVE_HORA_INICIAL') or None,
                EVE_HORA_FINAL=request.POST.get('EVE_HORA_FINAL') or None,
                EVE_LOCAL=request.POST.get('EVE_LOCAL') or None,
                EVE_ENDERECO=request.POST.get('EVE_ENDERECO') or None,
                EVE_RESPONSAVEL=request.POST.get('EVE_RESPONSAVEL') or None,
                EVE_CELEBRANTE=celebrante,
                EVE_PARTICIPANTES=participantes,
                EVE_CONFIRMADOS=confirmados,
                EVE_RECURSOS=request.POST.get('EVE_RECURSOS') or None,
                EVE_STATUS=status
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Evento criado com sucesso!',
                'evento_id': evento.EVE_ID
            })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao criar evento: {str(e)}'
            })


@method_decorator(login_required, name='dispatch')
class MasterDetailDeleteView(View):
    """
    View para excluir um evento e seus itens
    """
    
    def post(self, request, pk):
        try:
            evento = get_object_or_404(TBEVENTO, pk=pk)
            titulo_evento = evento.EVE_TITULO
            
            # Excluir evento (os itens serão excluídos automaticamente por CASCADE)
            evento.delete()
            
            messages.success(request, f'Evento "{titulo_evento}" excluído com sucesso!')
            
            # Redirecionar para return_url se existir, senão para lista
            return_url = request.GET.get('return_url')
            if return_url:
                return redirect(return_url)
            else:
                return redirect('app_igreja:eventos_master_detail_list')
            
        except Exception as e:
            messages.error(request, f'Erro ao excluir evento: {str(e)}')
            return redirect('app_igreja:eventos_master_detail_view', pk=pk)


@method_decorator(login_required, name='dispatch')
class MasterDetailItensView(View):
    """
    View para retornar itens de um evento em JSON e adicionar novos itens
    """
    
    def get(self, request, pk):
        try:
            evento = get_object_or_404(TBEVENTO, pk=pk)
            itens = evento.itens.all().order_by('ITEM_EVE_DATA_INICIAL', 'ITEM_EVE_HORA_INICIAL')
            
            itens_data = []
            for item in itens:
                itens_data.append({
                    'id': item.ITEM_EVE_ID,
                    'data_inicial': str(item.ITEM_EVE_DATA_INICIAL),
                    'acao': item.ITEM_EVE_ACAO,
                    'data_final': str(item.ITEM_EVE_DATA_FINAL) if item.ITEM_EVE_DATA_FINAL else None,
                    'hora_inicial': str(item.ITEM_EVE_HORA_INICIAL),
                    'hora_final': str(item.ITEM_EVE_HORA_FINAL) if item.ITEM_EVE_HORA_FINAL else None
                })
            
            return JsonResponse({
                'success': True,
                'itens': itens_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro: {str(e)}'
            })
    
    def post(self, request, pk):
        """Adicionar novo item ao evento"""
        try:
            action = request.POST.get('action')
            
            if action == 'adicionar_item':
                evento = get_object_or_404(TBEVENTO, pk=pk)
                
                data_inicial = request.POST.get('ITEM_EVE_DATA_INICIAL')
                acao = request.POST.get('ITEM_EVE_ACAO')
                data_final = request.POST.get('ITEM_EVE_DATA_FINAL') or None
                hora_inicial = request.POST.get('ITEM_EVE_HORA_INICIAL')
                hora_final = request.POST.get('ITEM_EVE_HORA_FINAL') or None
                
                if not data_inicial or not hora_inicial or not acao:
                    return JsonResponse({
                        'success': False,
                        'message': 'Campos obrigatórios não preenchidos!'
                    })
                
                resultado = grava_item_evento(evento, data_inicial, acao, data_final, hora_inicial, hora_final)
                
                return JsonResponse({
                    'success': resultado['success'],
                    'message': resultado['message'],
                    'item_id': resultado.get('item_id')
                })
            
            elif action == 'excluir_item':
                item_id = request.POST.get('item_id')
                if not item_id:
                    return JsonResponse({
                        'success': False,
                        'message': 'ID do item não fornecido!'
                    })
                
                item = get_object_or_404(TBITEM_EVENTO, pk=item_id, ITEM_EVE_EVENTO_id=pk)
                item.delete()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Item excluído com sucesso!'
                })
            
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Ação não reconhecida!'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro: {str(e)}'
            })

