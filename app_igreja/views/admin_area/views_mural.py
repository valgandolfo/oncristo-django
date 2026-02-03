"""CRUD de Murais da Paróquia (admin)."""
from datetime import date
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from ...models.area_admin.models_mural import TBMURAL
from ...forms.area_admin.forms_mural import MuralForm
from ...utils_image import redimensionar_imagem

URL_LISTAR_MURAIS = 'app_igreja:listar_murais'
CAMPOS_FOTO_MURAL = [
    'MUR_foto1_mural', 'MUR_foto2_mural', 'MUR_foto3_mural',
    'MUR_foto4_mural', 'MUR_foto5_mural',
]


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


def _redirect_listar_murais():
    return redirect(URL_LISTAR_MURAIS)


def _aplicar_redimensionamento(mural, files):
    for campo in CAMPOS_FOTO_MURAL:
        if campo in files:
            img = redimensionar_imagem(files[campo])
            if img:
                setattr(mural, campo, img)


def _contar_fotos(mural):
    return sum(1 for c in CAMPOS_FOTO_MURAL if getattr(mural, c, None))


def _contar_legendas(mural):
    campos = ['MUR_legenda1_mural', 'MUR_legenda2_mural', 'MUR_legenda3_mural', 'MUR_legenda4_mural', 'MUR_legenda5_mural']
    return sum(1 for c in campos if getattr(mural, c, None))


@login_required
@admin_required
def listar_murais(request):
    """Lista murais com busca, filtro por status e paginação."""
    busca = request.GET.get('busca', '').strip()
    status = request.GET.get('status', '').strip()
    busca_realizada = bool(busca or status or request.GET.get('page'))

    if busca_realizada:
        murais = TBMURAL.objects.all().order_by('-MUR_data_mural')
        if busca.lower() not in ('todos', 'todas'):
            if busca:
                murais = murais.filter(MUR_titulo_mural__icontains=busca)
            if status == 'ativo':
                murais = murais.filter(MUR_ativo=True)
            elif status == 'inativo':
                murais = murais.filter(MUR_ativo=False)
    else:
        murais = TBMURAL.objects.none()

    paginator = Paginator(murais, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    hoje = date.today()

    context = {
        'page_obj': page_obj,
        'busca': busca,
        'status': status,
        'total_murais': TBMURAL.objects.count(),
        'ativos': TBMURAL.objects.filter(MUR_ativo=True).count(),
        'inativos': TBMURAL.objects.filter(MUR_ativo=False).count(),
        'murais_recentes': TBMURAL.objects.filter(MUR_ativo=True).order_by('-MUR_data_mural')[:5],
        'murais_mes': TBMURAL.objects.filter(MUR_data_mural__year=hoje.year, MUR_data_mural__month=hoje.month).count(),
        'modo_dashboard': True,
        'model_verbose_name': 'Mural da Paróquia',
        'mural_section': 'list',
        'busca_realizada': busca_realizada,
    }
    return render(request, 'admin_area/tpl_mural.html', context)


@login_required
@admin_required
def criar_mural(request):
    """Cria um novo mural."""
    if request.method == 'POST':
        form = MuralForm(request.POST, request.FILES)
        if form.is_valid():
            mural = form.save(commit=False)
            _aplicar_redimensionamento(mural, request.FILES)
            mural.save()
            messages.success(request, 'Mural criado com sucesso!')
            return _redirect_listar_murais()
        messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = MuralForm()

    next_url = request.META.get('HTTP_REFERER') or reverse(URL_LISTAR_MURAIS)
    context = {
        'form': form,
        'acao': 'incluir',
        'model_verbose_name': 'Mural da Paróquia',
        'next_url': next_url,
        'modo_detalhe': True,
        'mural_section': 'form',
    }
    return render(request, 'admin_area/tpl_mural.html', context)


@login_required
@admin_required
def detalhar_mural(request, mural_id):
    """Exibe detalhes de um mural."""
    mural = get_object_or_404(TBMURAL, MUR_ID=mural_id)
    next_url = request.META.get('HTTP_REFERER') or reverse(URL_LISTAR_MURAIS)
    context = {
        'mural': mural,
        'acao': 'consultar',
        'model_verbose_name': 'Mural da Paróquia',
        'next_url': next_url,
        'modo_detalhe': True,
        'fotos_count': _contar_fotos(mural),
        'legendas_count': _contar_legendas(mural),
        'mural_section': 'detail',
    }
    return render(request, 'admin_area/tpl_mural.html', context)


@login_required
@admin_required
def editar_mural(request, mural_id):
    """Edita um mural existente."""
    mural = get_object_or_404(TBMURAL, MUR_ID=mural_id)
    if request.method == 'POST':
        form = MuralForm(request.POST, request.FILES, instance=mural)
        if form.is_valid():
            mural = form.save(commit=False)
            _aplicar_redimensionamento(mural, request.FILES)
            mural.save()
            messages.success(request, 'Mural atualizado com sucesso!')
            return _redirect_listar_murais()
        messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = MuralForm(instance=mural)

    next_url = request.META.get('HTTP_REFERER') or reverse(URL_LISTAR_MURAIS)
    context = {
        'form': form,
        'mural': mural,
        'acao': 'editar',
        'model_verbose_name': 'Mural da Paróquia',
        'next_url': next_url,
        'modo_detalhe': True,
        'mural_section': 'form',
    }
    return render(request, 'admin_area/tpl_mural.html', context)


@login_required
@admin_required
def excluir_mural(request, mural_id):
    """Exclui um mural."""
    mural = get_object_or_404(TBMURAL, MUR_ID=mural_id)
    if request.method == 'POST':
        mural.delete()
        messages.success(request, 'Mural excluído com sucesso!')
        return _redirect_listar_murais()

    next_url = request.META.get('HTTP_REFERER') or reverse(URL_LISTAR_MURAIS)
    context = {
        'mural': mural,
        'acao': 'excluir',
        'model_verbose_name': 'Mural da Paróquia',
        'next_url': next_url,
        'modo_detalhe': True,
        'fotos_count': _contar_fotos(mural),
        'mural_section': 'delete',
    }
    return render(request, 'admin_area/tpl_mural.html', context)
