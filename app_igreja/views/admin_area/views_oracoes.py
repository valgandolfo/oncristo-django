from functools import wraps
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from ...models.area_admin.models_oracoes import TBORACOES
from ...forms.area_admin.forms_oracoes import OracaoForm, OracaoFiltroForm

URL_LISTAR_ORACOES = 'app_igreja:listar_oracoes'


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


def _redirect_listar_oracoes():
    return redirect(URL_LISTAR_ORACOES)


@login_required
@admin_required
def listar_oracoes(request):
    """Lista pedidos de orações com paginação e filtros."""
    filtro_form = OracaoFiltroForm(request.GET)
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    tipo_filter = request.GET.get('tipo_oracao', '').strip()
    ativo_filter = request.GET.get('ativo', '').strip()
    data_inicio = request.GET.get('data_inicio', '').strip()
    data_fim = request.GET.get('data_fim', '').strip()
    busca_realizada = bool(query or status_filter or tipo_filter or ativo_filter or data_inicio or data_fim or request.GET.get('page'))

    if busca_realizada:
        oracoes = TBORACOES.objects.all()
        if query.lower() not in ['todos', 'todas']:
            if query:
                oracoes = oracoes.filter(
                    Q(ORA_nome_solicitante__icontains=query) |
                    Q(ORA_telefone_pedinte__icontains=query) |
                    Q(ORA_descricao__icontains=query)
                )
            if status_filter:
                oracoes = oracoes.filter(ORA_status=status_filter)
            if tipo_filter:
                oracoes = oracoes.filter(ORA_tipo_oracao=tipo_filter)
            if ativo_filter:
                oracoes = oracoes.filter(ORA_ativo=(ativo_filter.lower() == 'true'))
            if data_inicio:
                try:
                    oracoes = oracoes.filter(ORA_data_pedido__gte=datetime.strptime(data_inicio, '%Y-%m-%d').date())
                except ValueError:
                    pass
            if data_fim:
                try:
                    oracoes = oracoes.filter(ORA_data_pedido__lte=datetime.strptime(data_fim, '%Y-%m-%d').date())
                except ValueError:
                    pass
        oracoes = oracoes.order_by('-ORA_data_pedido', 'ORA_nome_solicitante')
    else:
        oracoes = TBORACOES.objects.none()

    paginator = Paginator(oracoes, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    total_oracoes = TBORACOES.objects.count()
    pendentes = TBORACOES.objects.filter(ORA_status='PENDENTE').count()
    em_oracao = TBORACOES.objects.filter(ORA_status='EM_ORACAO').count()
    atendidos = TBORACOES.objects.filter(ORA_status='ATENDIDO').count()
    cancelados = TBORACOES.objects.filter(ORA_status='CANCELADO').count()
    ativos = TBORACOES.objects.filter(ORA_ativo=True).count()
    hoje = datetime.now()
    inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    oracoes_mes = TBORACOES.objects.filter(ORA_data_pedido__gte=inicio_mes).count()

    context = {
        'page_obj': page_obj,
        'filtro_form': filtro_form,
        'query': query,
        'status_filter': status_filter,
        'tipo_filter': tipo_filter,
        'ativo_filter': ativo_filter,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'total_oracoes': total_oracoes,
        'pendentes': pendentes,
        'em_oracao': em_oracao,
        'atendidos': atendidos,
        'cancelados': cancelados,
        'ativos': ativos,
        'oracoes_mes': oracoes_mes,
        'modo_dashboard': True,
        'busca_realizada': busca_realizada,
    }
    return render(request, 'admin_area/tpl_oracoes.html', context)


@login_required
@admin_required
def criar_oracao(request):
    """Cria um novo pedido de oração."""
    if request.method == 'POST':
        form = OracaoForm(request.POST)
        if form.is_valid():
            oracao = form.save(commit=False)
            oracao.ORA_usuario_id = request.user
            oracao.save()
            messages.success(request, 'Pedido de oração cadastrado com sucesso!')
            return _redirect_listar_oracoes()
        messages.error(request, 'Erro ao cadastrar pedido de oração. Verifique os dados.')
    else:
        form = OracaoForm()

    next_url = request.META.get('HTTP_REFERER') or reverse(URL_LISTAR_ORACOES)
    context = {
        'form': form,
        'acao': 'incluir',
        'model_verbose_name': 'Pedido de Oração',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_oracoes.html', context)


@login_required
@admin_required
def detalhar_oracao(request, oracao_id):
    """Mostra detalhes de um pedido de oração."""
    oracao = get_object_or_404(TBORACOES, id=oracao_id)
    next_url = request.META.get('HTTP_REFERER') or reverse(URL_LISTAR_ORACOES)
    context = {
        'oracao': oracao,
        'acao': 'consultar',
        'model_verbose_name': 'Pedido de Oração',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_oracoes.html', context)


@login_required
@admin_required
def editar_oracao(request, oracao_id):
    """Edita um pedido de oração existente."""
    oracao = get_object_or_404(TBORACOES, id=oracao_id)
    if request.method == 'POST':
        form = OracaoForm(request.POST, instance=oracao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pedido de oração atualizado com sucesso!')
            return _redirect_listar_oracoes()
        messages.error(request, 'Erro ao atualizar pedido de oração. Verifique os campos.')
    else:
        form = OracaoForm(instance=oracao)

    next_url = request.META.get('HTTP_REFERER') or reverse(URL_LISTAR_ORACOES)
    context = {
        'form': form,
        'oracao': oracao,
        'acao': 'editar',
        'model_verbose_name': 'Pedido de Oração',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_oracoes.html', context)


@login_required
@admin_required
def excluir_oracao(request, oracao_id):
    """Exclui um pedido de oração."""
    oracao = get_object_or_404(TBORACOES, id=oracao_id)
    if request.method == 'POST':
        oracao.delete()
        messages.success(request, 'Pedido de oração excluído com sucesso!')
        return _redirect_listar_oracoes()

    next_url = request.META.get('HTTP_REFERER') or reverse(URL_LISTAR_ORACOES)
    context = {
        'oracao': oracao,
        'acao': 'excluir',
        'model_verbose_name': 'Pedido de Oração',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_oracoes.html', context)


@login_required
@admin_required
def dashboard_oracoes(request):
    """Dashboard com estatísticas dos pedidos de orações."""
    total_oracoes = TBORACOES.objects.count()
    pendentes = TBORACOES.objects.filter(ORA_status='PENDENTE').count()
    em_oracao = TBORACOES.objects.filter(ORA_status='EM_ORACAO').count()
    atendidos = TBORACOES.objects.filter(ORA_status='ATENDIDO').count()
    cancelados = TBORACOES.objects.filter(ORA_status='CANCELADO').count()
    ativos = TBORACOES.objects.filter(ORA_ativo=True).count()
    oracoes_por_tipo = TBORACOES.objects.values('ORA_tipo_oracao').annotate(count=Count('ORA_id')).order_by('-count')[:5]
    oracoes_por_status = TBORACOES.objects.values('ORA_status').annotate(count=Count('ORA_id')).order_by('-count')
    hoje = datetime.now()
    inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    novos_mes = TBORACOES.objects.filter(ORA_data_pedido__gte=inicio_mes).count()
    sete_dias_atras = hoje - timedelta(days=7)
    ultimos_7_dias = TBORACOES.objects.filter(ORA_data_pedido__gte=sete_dias_atras).count()
    pendentes_antigos = TBORACOES.objects.filter(
        ORA_status='PENDENTE',
        ORA_data_pedido__lt=sete_dias_atras.date()
    ).count()

    context = {
        'total_oracoes': total_oracoes,
        'pendentes': pendentes,
        'em_oracao': em_oracao,
        'atendidos': atendidos,
        'cancelados': cancelados,
        'ativos': ativos,
        'oracoes_por_tipo': oracoes_por_tipo,
        'oracoes_por_status': oracoes_por_status,
        'novos_mes': novos_mes,
        'ultimos_7_dias': ultimos_7_dias,
        'pendentes_antigos': pendentes_antigos,
        'titulo': 'Dashboard de Pedidos de Orações',
        'modo_dashboard': True,
    }
    return render(request, 'admin_area/tpl_oracoes.html', context)


@login_required
@admin_required
def alterar_status_oracao(request, oracao_id):
    """Altera o status de um pedido de oração via AJAX."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido!'})
    oracao = get_object_or_404(TBORACOES, id=oracao_id)
    novo_status = request.POST.get('status')
    if novo_status not in dict(TBORACOES.STATUS_CHOICES):
        return JsonResponse({'success': False, 'message': 'Status inválido!'})
    oracao.ORA_status = novo_status
    oracao.save()
    return JsonResponse({
        'success': True,
        'message': 'Status alterado com sucesso!',
        'novo_status': oracao.get_status_display(),
        'status_class': oracao.get_status_class()
    })


@login_required
@admin_required
def toggle_ativo_oracao(request, oracao_id):
    """Alterna ativo/inativo de um pedido de oração via AJAX."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido!'})
    oracao = get_object_or_404(TBORACOES, id=oracao_id)
    oracao.ORA_ativo = not oracao.ORA_ativo
    oracao.save()
    return JsonResponse({
        'success': True,
        'message': f'Pedido {"ativado" if oracao.ORA_ativo else "desativado"} com sucesso!',
        'ativo': oracao.ORA_ativo
    })
