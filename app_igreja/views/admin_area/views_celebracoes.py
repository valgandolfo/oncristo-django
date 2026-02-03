from functools import wraps
from datetime import date, timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from ...models.area_admin.models_celebracoes import TBCELEBRACOES
from ...forms.area_admin.forms_celebracoes import CelebracaoForm

URL_LISTAR_CELEBRACOES = 'app_igreja:listar_celebracoes'


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


def _redirect_listar_celebracoes():
    return redirect(URL_LISTAR_CELEBRACOES)


@login_required
@admin_required
def listar_celebracoes(request):
    """Lista celebrações com filtros e paginação."""
    busca_nome = request.GET.get('busca_nome', '').strip()
    filtro_status = request.GET.get('status', '').strip()
    filtro_data_inicio = request.GET.get('data_inicio', '').strip()
    filtro_data_fim = request.GET.get('data_fim', '').strip()
    busca_realizada = bool(busca_nome or filtro_status or filtro_data_inicio or filtro_data_fim or request.GET.get('page'))

    if busca_realizada:
        celebracoes = TBCELEBRACOES.objects.all()
        if busca_nome.lower() not in ['todos', 'todas']:
            if busca_nome:
                celebracoes = celebracoes.filter(
                    Q(CEL_nome_solicitante__icontains=busca_nome) |
                    Q(CEL_tipo_celebracao__icontains=busca_nome) |
                    Q(CEL_local__icontains=busca_nome)
                )
            if filtro_status:
                celebracoes = celebracoes.filter(CEL_status=filtro_status)
            if filtro_data_inicio:
                celebracoes = celebracoes.filter(CEL_data_celebracao__gte=filtro_data_inicio)
            if filtro_data_fim:
                celebracoes = celebracoes.filter(CEL_data_celebracao__lte=filtro_data_fim)
        celebracoes = celebracoes.order_by('CEL_data_celebracao', 'CEL_horario')
    else:
        celebracoes = TBCELEBRACOES.objects.none()

    paginator = Paginator(celebracoes, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    total_celebracoes = TBCELEBRACOES.objects.count()
    pendentes = TBCELEBRACOES.objects.filter(CEL_status='pendente').count()
    confirmadas = TBCELEBRACOES.objects.filter(CEL_status='confirmada').count()
    realizadas = TBCELEBRACOES.objects.filter(CEL_status='realizada').count()
    canceladas = TBCELEBRACOES.objects.filter(CEL_status='cancelada').count()
    data_limite = date.today() + timedelta(days=7)
    proximas_celebracoes = TBCELEBRACOES.objects.filter(
        CEL_data_celebracao__gte=date.today(),
        CEL_data_celebracao__lte=data_limite,
        CEL_status__in=['pendente', 'confirmada']
    ).order_by('CEL_data_celebracao', 'CEL_horario')[:5]

    context = {
        'page_obj': page_obj,
        'busca_nome': busca_nome,
        'filtro_status': filtro_status,
        'filtro_data_inicio': filtro_data_inicio,
        'filtro_data_fim': filtro_data_fim,
        'total_celebracoes': total_celebracoes,
        'pendentes': pendentes,
        'confirmadas': confirmadas,
        'realizadas': realizadas,
        'canceladas': canceladas,
        'proximas_celebracoes': proximas_celebracoes,
        'modo_dashboard': True,
        'busca_realizada': busca_realizada,
    }
    return render(request, 'admin_area/tpl_celebracoes.html', context)


@login_required
@admin_required
def criar_celebracao(request):
    """Cria uma nova celebração."""
    if request.method == 'POST':
        form = CelebracaoForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Celebração cadastrada com sucesso!')
                return _redirect_listar_celebracoes()
            except Exception as e:
                messages.error(request, f'Erro ao salvar celebração: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CelebracaoForm()

    next_url = request.META.get('HTTP_REFERER', reverse(URL_LISTAR_CELEBRACOES))
    context = {
        'form': form,
        'acao': 'incluir',
        'model_verbose_name': 'Celebração',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_celebracoes.html', context)


@login_required
@admin_required
def detalhar_celebracao(request, celebracao_id):
    """Exibe detalhes de uma celebração."""
    celebracao = get_object_or_404(TBCELEBRACOES, id=celebracao_id)
    next_url = request.META.get('HTTP_REFERER', reverse(URL_LISTAR_CELEBRACOES))
    context = {
        'celebracao': celebracao,
        'acao': 'consultar',
        'model_verbose_name': 'Celebração',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_celebracoes.html', context)


@login_required
@admin_required
def editar_celebracao(request, celebracao_id):
    """Edita uma celebração existente."""
    celebracao = get_object_or_404(TBCELEBRACOES, id=celebracao_id)
    if request.method == 'POST':
        form = CelebracaoForm(request.POST, instance=celebracao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Celebração atualizada com sucesso!')
            return _redirect_listar_celebracoes()
    else:
        form = CelebracaoForm(instance=celebracao)

    next_url = request.META.get('HTTP_REFERER', reverse(URL_LISTAR_CELEBRACOES))
    context = {
        'form': form,
        'celebracao': celebracao,
        'acao': 'editar',
        'model_verbose_name': 'Celebração',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_celebracoes.html', context)


@login_required
@admin_required
def excluir_celebracao(request, celebracao_id):
    """Exclui uma celebração."""
    celebracao = get_object_or_404(TBCELEBRACOES, id=celebracao_id)
    if request.method == 'POST':
        celebracao.delete()
        messages.success(request, 'Celebração excluída com sucesso!')
        return _redirect_listar_celebracoes()

    next_url = request.META.get('HTTP_REFERER', reverse(URL_LISTAR_CELEBRACOES))
    context = {
        'celebracao': celebracao,
        'acao': 'excluir',
        'model_verbose_name': 'Celebração',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_celebracoes.html', context)
