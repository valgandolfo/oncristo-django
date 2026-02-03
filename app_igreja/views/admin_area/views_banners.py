"""CRUD de Banners de Patrocinadores (admin)."""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from ...models.area_admin.models_banners import TBBANNERS
from ...forms.area_admin.forms_banners import BannerForm

URL_LISTAR_BANNERS = 'app_igreja:listar_banners'


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


def _redirect_listar_banners():
    return redirect(URL_LISTAR_BANNERS)


@login_required
@admin_required
def listar_banners(request):
    """Lista banners com busca, filtro por status e paginação."""
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    busca_realizada = bool(query or status_filter or request.GET.get('page'))

    if busca_realizada:
        banners = TBBANNERS.objects.all()
        if query.lower() not in ('todos', 'todas'):
            if query:
                banners = banners.filter(
                    Q(BAN_NOME_PATROCINADOR__icontains=query) |
                    Q(BAN_DESCRICAO_COMERCIAL__icontains=query) |
                    Q(BAN_TELEFONE__icontains=query) |
                    Q(BAN_ENDERECO__icontains=query)
                )
            if status_filter == 'ativo':
                banners = banners.filter(BAN_ORDEM__gt=0)
            elif status_filter == 'inativo':
                banners = banners.filter(BAN_ORDEM=0)
    else:
        banners = TBBANNERS.objects.none()

    banners = banners.order_by('BAN_ORDEM', 'BAN_NOME_PATROCINADOR')
    paginator = Paginator(banners, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
        'total_banners': TBBANNERS.objects.count(),
        'ativos': TBBANNERS.objects.filter(BAN_ORDEM__gt=0).count(),
        'inativos': TBBANNERS.objects.filter(BAN_ORDEM=0).count(),
        'modo_dashboard': True,
        'busca_realizada': busca_realizada,
    }
    return render(request, 'admin_area/tpl_banners.html', context)


@login_required
@admin_required
def criar_banner(request):
    """Cria um novo banner."""
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Banner criado com sucesso! A imagem foi salva no AWS S3.')
                return _redirect_listar_banners()
            except Exception as e:
                messages.error(request, f'Erro ao salvar banner no S3: {str(e)}')
        else:
            messages.error(request, 'Erro ao cadastrar banner. Verifique os dados.')
    else:
        form = BannerForm()

    next_url = request.META.get('HTTP_REFERER') or reverse(URL_LISTAR_BANNERS)
    context = {
        'form': form,
        'acao': 'incluir',
        'model_verbose_name': 'Banner de Patrocinador',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_banners.html', context)


@login_required
@admin_required
def detalhar_banner(request, banner_id):
    """Exibe detalhes de um banner."""
    banner = get_object_or_404(TBBANNERS, id=banner_id)
    context = {
        'banner': banner,
        'acao': 'consultar',
        'model_verbose_name': 'Banner de Patrocinador',
        'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_banners.html', context)


@login_required
@admin_required
def editar_banner(request, banner_id):
    """Edita um banner existente."""
    banner = get_object_or_404(TBBANNERS, id=banner_id)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Banner atualizado com sucesso! A imagem foi salva no AWS S3.')
                return _redirect_listar_banners()
            except Exception as e:
                messages.error(request, f'Erro ao atualizar banner no S3: {str(e)}')
        else:
            messages.error(request, 'Erro ao atualizar banner. Verifique os campos.')
    else:
        form = BannerForm(instance=banner)

    next_url = request.META.get('HTTP_REFERER') or reverse(URL_LISTAR_BANNERS)
    context = {
        'form': form,
        'banner': banner,
        'acao': 'editar',
        'model_verbose_name': 'Banner de Patrocinador',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_banners.html', context)


@login_required
@admin_required
def excluir_banner(request, banner_id):
    """Exclui um banner."""
    banner = get_object_or_404(TBBANNERS, id=banner_id)
    if request.method == 'POST':
        banner.delete()
        messages.success(request, 'Banner excluído com sucesso!')
        return _redirect_listar_banners()

    next_url = request.META.get('HTTP_REFERER') or reverse(URL_LISTAR_BANNERS)
    context = {
        'banner': banner,
        'acao': 'excluir',
        'model_verbose_name': 'Banner de Patrocinador',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    return render(request, 'admin_area/tpl_banners.html', context)
