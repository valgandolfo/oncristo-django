"""
==================== VIEWS DE PLANOS ====================
Arquivo unificado com todas as views de Planos de Ação e Itens do Plano
Inclui: CRUD básico, CRUD de itens e Master-Detail
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.views import View
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta, date

from app_igreja.models.area_admin.models_planos import TBPLANO, TBITEMPLANO
from app_igreja.forms.area_admin.forms_planos import PlanoForm, ItemPlanoForm


@login_required
def listar_planos(request):
    """
    Lista todos os planos de ação com paginação e busca
    """
    # Parâmetros de busca
    busca = request.GET.get('busca', '')
    status = request.GET.get('status', '')
    
    # Query base
    planos = TBPLANO.objects.all().order_by('-PLA_data_cadastro')
    
    # Filtros
    if busca:
        planos = planos.filter(
            Q(PLA_titulo_plano__icontains=busca)
        )
    
    if status:
        if status == 'ativo':
            planos = planos.filter(PLA_ativo=True)
        elif status == 'inativo':
            planos = planos.filter(PLA_ativo=False)
    
    # Paginação
    paginator = Paginator(planos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    total_planos = TBPLANO.objects.count()
    ativos = TBPLANO.objects.filter(PLA_ativo=True).count()
    inativos = TBPLANO.objects.filter(PLA_ativo=False).count()
    
    # Planos recentes (últimos 5)
    planos_recentes = TBPLANO.objects.filter(
        PLA_ativo=True
    ).order_by('-PLA_data_cadastro')[:5]
    
    # Planos do mês atual
    hoje = date.today()
    planos_mes = TBPLANO.objects.filter(
        PLA_data_cadastro__year=hoje.year,
        PLA_data_cadastro__month=hoje.month
    ).count()
    
    context = {
        'page_obj': page_obj,
        'busca': busca,
        'status': status,
        'total_planos': total_planos,
        'ativos': ativos,
        'inativos': inativos,
        'planos_recentes': planos_recentes,
        'planos_mes': planos_mes,
        'modo_dashboard': True,  # Migrado para nova tela pai dashboard
        'model_verbose_name': 'Plano de Ação',
    }
    
    return render(request, 'admin_area/tpl_planos.html', context)


@login_required
def criar_plano(request):
    """
    Cria um novo plano de ação
    """
    if request.method == 'POST':
        form = PlanoForm(request.POST)
        if form.is_valid():
            plano = form.save()
            messages.success(request, 'Plano de ação criado com sucesso!')
            return redirect('app_igreja:listar_planos')
    else:
        form = PlanoForm()
    
    # Usar HTTP_REFERER como fallback, igual ao dizimistas
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_planos')
    
    context = {
        'form': form,
        'acao': 'incluir',
        'model_verbose_name': 'Plano de Ação',
        'next_url': next_url,
        'modo_detalhe': True,
        'planos_section': 'detail',  # Seção: CRUD básico
    }
    
    return render(request, 'admin_area/tpl_planos.html', context)


@login_required
def detalhar_plano(request, plano_id):
    """
    Visualiza os detalhes de um plano de ação
    """
    plano = get_object_or_404(TBPLANO, PLA_id=plano_id)
    
    # Usar HTTP_REFERER como fallback, igual ao dizimistas
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_planos')
    
    context = {
        'plano': plano,
        'acao': 'consultar',
        'model_verbose_name': 'Plano de Ação',
        'next_url': next_url,
        'modo_detalhe': True,
        'planos_section': 'detail',  # Seção: CRUD básico
    }
    
    return render(request, 'admin_area/tpl_planos.html', context)


@login_required
def editar_plano(request, plano_id):
    """
    Edita um plano de ação existente
    """
    plano = get_object_or_404(TBPLANO, PLA_id=plano_id)
    
    if request.method == 'POST':
        form = PlanoForm(request.POST, instance=plano)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plano de ação atualizado com sucesso!')
            return redirect('app_igreja:listar_planos')
    else:
        form = PlanoForm(instance=plano)
    
    # Usar HTTP_REFERER como fallback, igual ao dizimistas
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_planos')
    
    context = {
        'form': form,
        'plano': plano,
        'acao': 'editar',
        'model_verbose_name': 'Plano de Ação',
        'next_url': next_url,
        'modo_detalhe': True,
        'planos_section': 'detail',  # Seção: CRUD básico
    }
    
    return render(request, 'admin_area/tpl_planos.html', context)


@login_required
def excluir_plano(request, plano_id):
    """
    Exclui um plano de ação
    """
    plano = get_object_or_404(TBPLANO, PLA_id=plano_id)
    
    if request.method == 'POST':
        plano.delete()
        messages.success(request, 'Plano de ação excluído com sucesso!')
        return redirect('app_igreja:listar_planos')
    
    # Usar HTTP_REFERER como fallback, igual ao dizimistas
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_planos')
    
    context = {
        'plano': plano,
        'acao': 'excluir',
        'model_verbose_name': 'Plano de Ação',
        'next_url': next_url,
        'modo_detalhe': True,
        'planos_section': 'detail',  # Seção: CRUD básico
    }
    
    return render(request, 'admin_area/tpl_planos.html', context)


# ==================== VIEWS DE ITENS DO PLANO ====================

@login_required
def listar_itens_plano(request, plano_id=None):
    """
    Lista todos os itens de plano, opcionalmente filtrados por plano específico
    """
    # Se plano_id foi fornecido, filtrar por esse plano
    if plano_id:
        plano = get_object_or_404(TBPLANO, PLA_id=plano_id)
        itens = TBITEMPLANO.objects.filter(ITEM_PLANO_PLANO=plano).order_by('ITEM_HORA_PLANO')
        titulo = f'Itens do Plano: {plano.PLA_titulo_plano}'
    else:
        plano = None
        itens = TBITEMPLANO.objects.all().order_by('ITEM_PLANO_PLANO', 'ITEM_HORA_PLANO')
        titulo = 'Itens dos Planos'
    
    # Parâmetros de busca
    busca = request.GET.get('busca', '')
    
    # Filtros
    if busca:
        itens = itens.filter(
            Q(ITEM_ACAO_PLANO__icontains=busca) |
            Q(ITEM_PLANO_PLANO__PLA_titulo_plano__icontains=busca)
        )
    
    # Paginação
    paginator = Paginator(itens, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    total_itens = itens.count()
    
    context = {
        'page_obj': page_obj,
        'busca': busca,
        'total_itens': total_itens,
        'plano': plano,
        'titulo': titulo,
        'modo_dashboard': True,
        'model_verbose_name': 'Item do Plano',
    }
    
    return render(request, 'admin_area/tpl_item_plano.html', context)


@login_required
def criar_item_plano(request, plano_id=None):
    """
    Cria um novo item de plano
    Se plano_id for fornecido, pré-seleciona o plano
    """
    if request.method == 'POST':
        form = ItemPlanoForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(request, 'Item do plano criado com sucesso!')
            if plano_id:
                return redirect('app_igreja:listar_itens_plano', plano_id=plano_id)
            return redirect('app_igreja:listar_itens_plano')
    else:
        initial = {}
        if plano_id:
            plano = get_object_or_404(TBPLANO, PLA_id=plano_id)
            initial['ITEM_PLANO_PLANO'] = plano
        form = ItemPlanoForm(initial=initial)
    
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_itens_plano')
    
    context = {
        'form': form,
        'acao': 'incluir',
        'model_verbose_name': 'Item do Plano',
        'next_url': next_url,
        'modo_detalhe': True,
        'plano_id': plano_id,
    }
    
    return render(request, 'admin_area/tpl_item_plano.html', context)


@login_required
def detalhar_item_plano(request, item_id):
    """
    Visualiza os detalhes de um item de plano
    """
    item = get_object_or_404(TBITEMPLANO, ITEM_PLANO_ID=item_id)
    
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_itens_plano')
    
    context = {
        'item': item,
        'acao': 'consultar',
        'model_verbose_name': 'Item do Plano',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_item_plano.html', context)


@login_required
def editar_item_plano(request, item_id):
    """
    Edita um item de plano existente
    """
    item = get_object_or_404(TBITEMPLANO, ITEM_PLANO_ID=item_id)
    
    if request.method == 'POST':
        form = ItemPlanoForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item do plano atualizado com sucesso!')
            return redirect('app_igreja:listar_itens_plano', plano_id=item.ITEM_PLANO_PLANO.PLA_id)
    else:
        form = ItemPlanoForm(instance=item)
    
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_itens_plano')
    
    context = {
        'form': form,
        'item': item,
        'acao': 'editar',
        'model_verbose_name': 'Item do Plano',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_item_plano.html', context)


@login_required
def excluir_item_plano(request, item_id):
    """
    Exclui um item de plano
    """
    item = get_object_or_404(TBITEMPLANO, ITEM_PLANO_ID=item_id)
    plano_id = item.ITEM_PLANO_PLANO.PLA_id
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item do plano excluído com sucesso!')
        return redirect('app_igreja:listar_itens_plano', plano_id=plano_id)
    
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_itens_plano')
    
    context = {
        'item': item,
        'acao': 'excluir',
        'model_verbose_name': 'Item do Plano',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_item_plano.html', context)


# ==================== VIEWS MASTER-DETAIL PLANOS ====================

def grava_item_plano(plano, hora_plano, acao_plano):
    """
    Função unificada para gravar item de plano
    Retorna dict com success, message
    """
    try:
        if not all([hora_plano, acao_plano]):
            return {
                'success': False,
                'message': 'Dados do item incompletos!'
            }
        
        item = TBITEMPLANO.objects.create(
            ITEM_PLANO_PLANO=plano,
            ITEM_HORA_PLANO=hora_plano,
            ITEM_ACAO_PLANO=acao_plano
        )
        
        return {
            'success': True,
            'message': 'Item adicionado com sucesso!',
            'item_id': item.ITEM_PLANO_ID
        }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Erro ao criar item: {str(e)}'
        }


@method_decorator(login_required, name='dispatch')
class MasterDetailPlanoListView(View):
    """
    View para listar planos Master-Detail
    """
    
    def get(self, request):
        planos = TBPLANO.objects.all().order_by('-PLA_data_cadastro')
        
        # Busca
        busca = request.GET.get('busca', '')
        if busca:
            planos = planos.filter(PLA_titulo_plano__icontains=busca)
        
        # Filtro por status
        status = request.GET.get('status', '')
        if status == 'ativo':
            planos = planos.filter(PLA_ativo=True)
        elif status == 'inativo':
            planos = planos.filter(PLA_ativo=False)
        
        # Paginação
        paginator = Paginator(planos, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Estatísticas
        total_planos = TBPLANO.objects.count()
        ativos = TBPLANO.objects.filter(PLA_ativo=True).count()
        inativos = TBPLANO.objects.filter(PLA_ativo=False).count()
        
        context = {
            'page_obj': page_obj,
            'busca': busca,
            'status': status,
            'total_planos': total_planos,
            'ativos': ativos,
            'inativos': inativos,
            'modo_dashboard': True,
            'model_verbose_name': 'Plano de Ação',
            'master_detail_mode': True,
            'planos_section': 'list',
        }
        
        return render(request, 'admin_area/tpl_planos.html', context)


@method_decorator(login_required, name='dispatch')
class MasterDetailPlanoView(View):
    """
    View para exibir detalhes de um plano específico com seus itens
    """
    
    def get(self, request, pk):
        plano = get_object_or_404(TBPLANO, pk=pk)
        itens = plano.itens.all().order_by('ITEM_HORA_PLANO')
        confirmar_exclusao = request.GET.get('confirmar_exclusao', False)
        
        context = {
            'plano': plano,
            'itens': itens,
            'confirmar_exclusao': confirmar_exclusao,
            'page_title': f'Plano: {plano.PLA_titulo_plano}',
            'return_url': request.GET.get('return_url', ''),
            'planos_section': 'view',
        }
        
        return render(request, 'admin_area/tpl_planos.html', context)


@method_decorator(login_required, name='dispatch')
class MasterDetailCreateView(View):
    """
    View unificada para criar e manter registros Master-Detail
    """
    
    def get(self, request, pk=None):
        """Exibe formulário de criação ou manutenção"""
        plano = None
        itens = []
        modo_manutencao = False
        
        plano_id_url = request.GET.get('plano_id')
        
        if pk:
            plano = get_object_or_404(TBPLANO, pk=pk)
            itens = plano.itens.all().order_by('ITEM_HORA_PLANO')
            modo_manutencao = True
        elif plano_id_url:
            plano = get_object_or_404(TBPLANO, pk=plano_id_url)
            itens = plano.itens.all().order_by('ITEM_HORA_PLANO')
            modo_manutencao = True
        
        context = {
            'page_title': f'Manutenção Plano: {plano.PLA_titulo_plano}' if plano else 'Novo Plano',
            'plano': plano,
            'itens': itens,
            'modo_manutencao': modo_manutencao,
            'return_url': request.GET.get('return_url', ''),
            'planos_section': 'crud',
        }
        
        return render(request, 'admin_area/tpl_planos.html', context)
    
    def post(self, request, pk=None):
        """Processa criação ou manutenção do plano"""
        try:
            action = request.POST.get('action')
            
            if action == 'atualizar_plano' and pk:
                plano = get_object_or_404(TBPLANO, pk=pk)
                titulo_plano = request.POST.get('PLA_titulo_plano')
                ativo = request.POST.get('PLA_ativo') == 'on'
                
                if not titulo_plano:
                    return JsonResponse({
                        'success': False,
                        'message': 'Título do plano é obrigatório!'
                    })
                
                plano.PLA_titulo_plano = titulo_plano
                plano.PLA_ativo = ativo
                plano.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Dados do plano atualizados com sucesso!'
                })
            
            elif action == 'adicionar_item':
                plano_id = request.POST.get('plano_id') or pk
                
                if not plano_id:
                    return JsonResponse({
                        'success': False,
                        'message': 'ID do plano não fornecido!'
                    })
                
                try:
                    plano = get_object_or_404(TBPLANO, pk=plano_id)
                except Exception as e:
                    return JsonResponse({
                        'success': False,
                        'message': f'Plano não encontrado: {str(e)}'
                    })
                
                hora_plano = request.POST.get('ITEM_HORA_PLANO')
                acao_plano = request.POST.get('ITEM_ACAO_PLANO')
                
                resultado = grava_item_plano(plano, hora_plano, acao_plano)
                
                return JsonResponse({
                    'success': resultado['success'],
                    'message': resultado['message'],
                    'item_id': resultado.get('item_id')
                })
            
            elif action == 'editar_item' and pk:
                plano = get_object_or_404(TBPLANO, pk=pk)
                item_id = request.POST.get('item_id')
                hora_plano = request.POST.get('ITEM_HORA_PLANO')
                acao_plano = request.POST.get('ITEM_ACAO_PLANO')

                if item_id and hora_plano and acao_plano:
                    item = TBITEMPLANO.objects.get(ITEM_PLANO_ID=item_id, ITEM_PLANO_PLANO=plano)
                    item.ITEM_HORA_PLANO = hora_plano
                    item.ITEM_ACAO_PLANO = acao_plano
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
                plano = get_object_or_404(TBPLANO, pk=pk)
                item_id = request.POST.get('item_id')

                if item_id:
                    item = TBITEMPLANO.objects.get(ITEM_PLANO_ID=item_id, ITEM_PLANO_PLANO=plano)
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
                return self._criar_novo_plano(request)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro: {str(e)}'
            })
    
    def _criar_novo_plano(self, request):
        """Método auxiliar para criar novo plano"""
        try:
            titulo_plano = request.POST.get('PLA_titulo_plano')
            ativo = request.POST.get('PLA_ativo') == 'on'
            
            if not titulo_plano:
                return JsonResponse({
                    'success': False,
                    'message': 'Título do plano é obrigatório!'
                })
            
            plano = TBPLANO.objects.create(
                PLA_titulo_plano=titulo_plano,
                PLA_ativo=ativo
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Plano criado com sucesso!',
                'plano_id': plano.PLA_id
            })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao criar plano: {str(e)}'
            })


@method_decorator(login_required, name='dispatch')
class MasterDetailDeleteView(View):
    """
    View para excluir um plano e seus itens
    """
    
    def post(self, request, pk):
        try:
            plano = get_object_or_404(TBPLANO, pk=pk)
            titulo_plano = plano.PLA_titulo_plano
            
            plano.delete()
            
            messages.success(request, f'Plano "{titulo_plano}" excluído com sucesso!')
            
            return_url = request.GET.get('return_url')
            if return_url:
                return redirect(return_url)
            else:
                return redirect('app_igreja:planos_master_detail_list')
            
        except Exception as e:
            messages.error(request, f'Erro ao excluir plano: {str(e)}')
            return redirect('app_igreja:planos_master_detail_view', pk=pk)


@method_decorator(login_required, name='dispatch')
class MasterDetailItensView(View):
    """
    View para retornar itens de um plano em JSON e adicionar novos itens
    """
    
    def get(self, request, pk):
        try:
            plano = get_object_or_404(TBPLANO, pk=pk)
            itens = plano.itens.all().order_by('ITEM_HORA_PLANO')
            
            itens_data = []
            for item in itens:
                itens_data.append({
                    'id': item.ITEM_PLANO_ID,
                    'hora': str(item.ITEM_HORA_PLANO),
                    'acao': item.ITEM_ACAO_PLANO
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
        """Adicionar novo item ao plano"""
        try:
            action = request.POST.get('action')
            
            if action == 'adicionar_item':
                plano = get_object_or_404(TBPLANO, pk=pk)
                
                hora_plano = request.POST.get('ITEM_HORA_PLANO')
                acao_plano = request.POST.get('ITEM_ACAO_PLANO')
                
                if not hora_plano or not acao_plano:
                    return JsonResponse({
                        'success': False,
                        'message': 'Campos obrigatórios não preenchidos!'
                    })
                
                resultado = grava_item_plano(plano, hora_plano, acao_plano)
                
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
                
                item = get_object_or_404(TBITEMPLANO, pk=item_id, ITEM_PLANO_PLANO_id=pk)
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
