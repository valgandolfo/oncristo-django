"""Modelos (master-detail) para missas: listar, criar, editar itens, excluir."""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

from ...models.area_admin.models_modelo import TBMODELO, TBITEM_MODELO, OCORRENCIA_CHOICES

URL_LISTAR_MODELOS = 'app_igreja:modelos_master_detail_list'


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


def _redirect_listar_modelos():
    return redirect(URL_LISTAR_MODELOS)


def _parse_ocorrencias(raw_value):
    if not raw_value:
        return []
    if isinstance(raw_value, list):
        return [v for v in raw_value if v]
    return [v for v in raw_value.split(',') if v]


def _grava_item_modelo(modelo, encargo, ocorrencias):
    if not encargo:
        return {'success': False, 'message': 'Informe o encargo do item.'}
    if not ocorrencias:
        return {'success': False, 'message': 'Selecione pelo menos uma ocorrência.'}
    try:
        item = TBITEM_MODELO.objects.create(
            ITEM_MOD_MODELO=modelo,
            ITEM_MOD_ENCARGO=encargo,
            ITEM_MOD_OCORRENCIA=','.join(ocorrencias),
        )
        return {'success': True, 'message': 'Item adicionado com sucesso!', 'item_id': item.ITEM_MOD_ID}
    except Exception as exc:
        return {'success': False, 'message': f'Erro ao criar item: {exc}'}


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class MasterDetailModeloListView(View):
    """Lista modelos com busca e paginação."""

    def get(self, request):
        busca = request.GET.get('busca', '').strip()
        busca_realizada = bool(busca or request.GET.get('page'))
        if busca_realizada:
            modelos = TBMODELO.objects.all().order_by('-MOD_DATA_CRIACAO')
            if busca and busca.lower() not in ('todos', 'todas'):
                modelos = modelos.filter(MOD_DESCRICAO__icontains=busca)
        else:
            modelos = TBMODELO.objects.none()
        paginator = Paginator(modelos, 10)
        page_obj = paginator.get_page(request.GET.get('page'))
        context = {
            'page_obj': page_obj,
            'busca': busca,
            'total_modelos': TBMODELO.objects.count(),
            'modo_dashboard': True,
            'model_verbose_name': 'Modelo',
            'master_detail_mode': True,
            'modelos_section': 'list',
            'busca_realizada': busca_realizada,
        }
        return render(request, 'admin_area/tpl_modelos.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class MasterDetailModeloView(View):
    """Detalhe do modelo e itens (consulta ou confirmação de exclusão)."""

    def get(self, request, pk):
        modelo = get_object_or_404(TBMODELO, pk=pk)
        itens = modelo.itens.all().order_by('ITEM_MOD_ID')
        acao = 'excluir' if request.GET.get('confirmar_exclusao') else 'consultar'
        next_url = request.META.get('HTTP_REFERER') or reverse(URL_LISTAR_MODELOS)
        context = {
            'modelo': modelo,
            'itens': itens,
            'confirmar_exclusao': request.GET.get('confirmar_exclusao'),
            'modelos_section': 'view',
            'ocorrencia_choices': OCORRENCIA_CHOICES,
            'modo_detalhe': True,
            'acao': acao,
            'model_verbose_name': 'Modelo',
            'next_url': next_url,
        }
        return render(request, 'admin_area/tpl_modelos.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class MasterDetailModeloCreateView(View):
    """Criar modelo, adicionar/editar/excluir itens (GET) e processar POST (AJAX)."""

    def get(self, request, pk=None):
        modelo_id = pk or request.GET.get('modelo_id')
        modelo = get_object_or_404(TBMODELO, pk=modelo_id) if modelo_id else None
        itens = list(modelo.itens.order_by('ITEM_MOD_ID')) if modelo else []
        context = {
            'modelo': modelo,
            'itens': itens,
            'modo_manutencao': bool(modelo),
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
            ocorrencias = _parse_ocorrencias(request.POST.get('ITEM_MOD_OCORRENCIA'))
            resultado = _grava_item_modelo(modelo, request.POST.get('ITEM_MOD_ENCARGO'), ocorrencias)
            return JsonResponse(resultado)
        if action == 'editar_item' and pk:
            modelo = get_object_or_404(TBMODELO, pk=pk)
            item = get_object_or_404(TBITEM_MODELO, ITEM_MOD_ID=request.POST.get('item_id'), ITEM_MOD_MODELO=modelo)
            encargo = request.POST.get('ITEM_MOD_ENCARGO')
            ocorrencias = _parse_ocorrencias(request.POST.get('ITEM_MOD_OCORRENCIA'))
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
            item = get_object_or_404(TBITEM_MODELO, ITEM_MOD_ID=request.POST.get('item_id'), ITEM_MOD_MODELO=modelo)
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
@method_decorator(admin_required, name='dispatch')
class MasterDetailModeloDeleteView(View):
    """Exclui modelo (POST)."""

    def post(self, request, pk):
        modelo = get_object_or_404(TBMODELO, pk=pk)
        return_url = request.POST.get('return_url')
        modelo.delete()
        messages.success(request, 'Modelo excluído com sucesso!')
        if return_url:
            return redirect(return_url)
        return _redirect_listar_modelos()
