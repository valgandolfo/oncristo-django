from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

from app_igreja.models.area_admin.models_modelo import TBMODELO, TBITEM_MODELO, OCORRENCIA_CHOICES


def _parse_ocorrencias(raw_value):
    if not raw_value:
        return []
    if isinstance(raw_value, list):
        return [valor for valor in raw_value if valor]
    return [valor for valor in raw_value.split(',') if valor]


def grava_item_modelo(modelo, encargo, ocorrencias):
    try:
        if not encargo:
            return {'success': False, 'message': 'Informe o encargo do item.'}
        if not ocorrencias:
            return {'success': False, 'message': 'Selecione pelo menos uma ocorrência.'}

        ocorrencias_str = ','.join(ocorrencias)
        item = TBITEM_MODELO.objects.create(
            ITEM_MOD_MODELO=modelo,
            ITEM_MOD_ENCARGO=encargo,
            ITEM_MOD_OCORRENCIA=ocorrencias_str,
        )
        return {
            'success': True,
            'message': 'Item adicionado com sucesso!',
            'item_id': item.ITEM_MOD_ID,
        }
    except Exception as exc:
        return {'success': False, 'message': f'Erro ao criar item: {exc}'}


@method_decorator(login_required, name='dispatch')
class MasterDetailModeloListView(View):
    def get(self, request):
        modelos = TBMODELO.objects.all().order_by('-MOD_DATA_CRIACAO')
        busca = request.GET.get('busca', '')
        if busca:
            modelos = modelos.filter(MOD_DESCRICAO__icontains=busca)

        paginator = Paginator(modelos, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        total_modelos = TBMODELO.objects.count()

        context = {
            'page_obj': page_obj,
            'busca': busca,
            'total_modelos': total_modelos,
            'modo_dashboard': True,
            'model_verbose_name': 'Modelo',
            'master_detail_mode': True,
            'modelos_section': 'list',
        }
        return render(request, 'admin_area/tpl_modelos.html', context)


@method_decorator(login_required, name='dispatch')
class MasterDetailModeloView(View):
    def get(self, request, pk):
        modelo = get_object_or_404(TBMODELO, pk=pk)
        itens = modelo.itens.all().order_by('ITEM_MOD_ENCARGO')
        confirmar_exclusao = request.GET.get('confirmar_exclusao')
        
        # Determinar ação baseado no parâmetro
        if confirmar_exclusao:
            acao = 'excluir'
        else:
            acao = 'consultar'
        
        # URL para retornar
        next_url = request.META.get('HTTP_REFERER', None)
        if not next_url:
            next_url = reverse('app_igreja:modelos_master_detail_list')
        
        context = {
            'modelo': modelo,
            'itens': itens,
            'confirmar_exclusao': confirmar_exclusao,
            'modelos_section': 'view',
            'ocorrencia_choices': OCORRENCIA_CHOICES,
            # Variáveis para o padrão PAI-FILHO
            'modo_detalhe': True,
            'acao': acao,
            'model_verbose_name': 'Modelo',
            'next_url': next_url,
        }
        return render(request, 'admin_area/tpl_modelos.html', context)


@method_decorator(login_required, name='dispatch')
class MasterDetailModeloCreateView(View):
    def get(self, request, pk=None):
        modelo = None
        itens = []
        modo_manutencao = False
        modelo_id_url = request.GET.get('modelo_id')

        if pk:
            modelo = get_object_or_404(TBMODELO, pk=pk)
            itens = modelo.itens.all().order_by('ITEM_MOD_ENCARGO')
            modo_manutencao = True
        elif modelo_id_url:
            modelo = get_object_or_404(TBMODELO, pk=modelo_id_url)
            itens = modelo.itens.all().order_by('ITEM_MOD_ENCARGO')
            modo_manutencao = True

        context = {
            'modelo': modelo,
            'itens': itens,
            'modo_manutencao': modo_manutencao,
            'modelos_section': 'crud',
            'ocorrencia_choices': OCORRENCIA_CHOICES,
        }
        return render(request, 'admin_area/tpl_modelos.html', context)

    def post(self, request, pk=None):
        action = request.POST.get('action')

        if action == 'atualizar_modelo' and pk:
            modelo = get_object_or_404(TBMODELO, pk=pk)
            descricao = request.POST.get('MOD_DESCRICAO')
            if not descricao:
                return JsonResponse({'success': False, 'message': 'Informe a descrição do modelo.'})
            modelo.MOD_DESCRICAO = descricao
            modelo.save()
            return JsonResponse({'success': True, 'message': 'Modelo atualizado com sucesso!'})

        if action == 'adicionar_item':
            modelo_id = request.POST.get('modelo_id') or pk
            if not modelo_id:
                return JsonResponse({'success': False, 'message': 'Modelo não informado.'})
            modelo = get_object_or_404(TBMODELO, pk=modelo_id)

            encargo = request.POST.get('ITEM_MOD_ENCARGO')
            ocorrencias_raw = request.POST.get('ITEM_MOD_OCORRENCIA')
            ocorrencias = _parse_ocorrencias(ocorrencias_raw)

            resultado = grava_item_modelo(modelo, encargo, ocorrencias)
            return JsonResponse(resultado)

        if action == 'editar_item' and pk:
            modelo = get_object_or_404(TBMODELO, pk=pk)
            item_id = request.POST.get('item_id')
            item = get_object_or_404(TBITEM_MODELO, ITEM_MOD_ID=item_id, ITEM_MOD_MODELO=modelo)

            encargo = request.POST.get('ITEM_MOD_ENCARGO')
            ocorrencias_raw = request.POST.get('ITEM_MOD_OCORRENCIA')
            ocorrencias = _parse_ocorrencias(ocorrencias_raw)

            if not encargo:
                return JsonResponse({'success': False, 'message': 'Informe o encargo do item.'})
            if not ocorrencias:
                return JsonResponse({'success': False, 'message': 'Selecione pelo menos uma ocorrência.'})

            item.ITEM_MOD_ENCARGO = encargo
            item.ITEM_MOD_OCORRENCIA = ','.join(ocorrencias)
            item.save()
            return JsonResponse({'success': True, 'message': 'Item atualizado com sucesso!'})

        if action == 'excluir_item' and pk:
            modelo = get_object_or_404(TBMODELO, pk=pk)
            item_id = request.POST.get('item_id')
            item = get_object_or_404(TBITEM_MODELO, ITEM_MOD_ID=item_id, ITEM_MOD_MODELO=modelo)
            item.delete()
            return JsonResponse({'success': True, 'message': 'Item removido com sucesso!'})

        return self._criar_novo_modelo(request)

    def _criar_novo_modelo(self, request):
        descricao = request.POST.get('MOD_DESCRICAO')
        if not descricao:
            return JsonResponse({'success': False, 'message': 'Informe a descrição do modelo.'})
        modelo = TBMODELO.objects.create(MOD_DESCRICAO=descricao)
        return JsonResponse({'success': True, 'message': 'Modelo criado com sucesso!', 'modelo_id': modelo.MOD_ID})


@method_decorator(login_required, name='dispatch')
class MasterDetailModeloDeleteView(View):
    def post(self, request, pk):
        modelo = get_object_or_404(TBMODELO, pk=pk)
        return_url = request.POST.get('return_url')
        modelo.delete()
        messages.success(request, 'Modelo excluído com sucesso!')
        if return_url:
            return redirect(return_url)
        return redirect('app_igreja:modelos_master_detail_list')
