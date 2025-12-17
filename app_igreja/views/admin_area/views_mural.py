from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse
from datetime import date

from app_igreja.models.area_admin.models_mural import TBMURAL
from app_igreja.forms.area_admin.forms_mural import MuralForm
from app_igreja.utils_image import redimensionar_imagem


@login_required
def listar_murais(request):
    """
    Lista todos os murais com paginação e busca
    """
    # Parâmetros de busca
    busca = request.GET.get('busca', '').strip()
    status = request.GET.get('status', '').strip()
    
    # Controla se o usuário já executou uma busca (preencheu algum filtro ou navegou na paginação)
    busca_realizada = bool(busca or status or request.GET.get('page'))
    
    # Só carrega os registros no grid DEPOIS que o usuário aplicar um filtro
    if busca_realizada:
        # Query base
        murais = TBMURAL.objects.all().order_by('-MUR_data_mural')
        
        # Filtros
        if busca:
            murais = murais.filter(
                Q(MUR_titulo_mural__icontains=busca)
            )
        
        if status:
            if status == 'ativo':
                murais = murais.filter(MUR_ativo=True)
            elif status == 'inativo':
                murais = murais.filter(MUR_ativo=False)
    else:
        # Queryset vazio até que o usuário faça a primeira busca
        murais = TBMURAL.objects.none()
    
    # Paginação
    paginator = Paginator(murais, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    total_murais = TBMURAL.objects.count()
    ativos = TBMURAL.objects.filter(MUR_ativo=True).count()
    inativos = TBMURAL.objects.filter(MUR_ativo=False).count()
    
    # Murais recentes (últimos 5)
    murais_recentes = TBMURAL.objects.filter(
        MUR_ativo=True
    ).order_by('-MUR_data_mural')[:5]
    
    # Murais do mês atual
    hoje = date.today()
    murais_mes = TBMURAL.objects.filter(
        MUR_data_mural__year=hoje.year,
        MUR_data_mural__month=hoje.month
    ).count()
    
    context = {
        'page_obj': page_obj,
        'busca': busca,
        'status': status,
        'total_murais': total_murais,
        'ativos': ativos,
        'inativos': inativos,
        'murais_recentes': murais_recentes,
        'murais_mes': murais_mes,
        'modo_dashboard': True,
        'model_verbose_name': 'Mural da Paróquia',
        'mural_section': 'list',  # Seção: Lista
        'busca_realizada': busca_realizada,
    }
    
    return render(request, 'admin_area/tpl_mural.html', context)


@login_required
def criar_mural(request):
    """
    Cria um novo mural
    """
    if request.method == 'POST':
        form = MuralForm(request.POST, request.FILES)
        if form.is_valid():
            mural = form.save(commit=False)
            
            # Redimensionar imagens antes de salvar
            campos_foto = [
                'MUR_foto1_mural', 'MUR_foto2_mural', 'MUR_foto3_mural',
                'MUR_foto4_mural', 'MUR_foto5_mural'
            ]
            
            for campo in campos_foto:
                if campo in request.FILES:
                    imagem_redimensionada = redimensionar_imagem(request.FILES[campo])
                    if imagem_redimensionada:
                        setattr(mural, campo, imagem_redimensionada)
            
            mural.save()
            messages.success(request, 'Mural criado com sucesso!')
            return redirect('app_igreja:listar_murais')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = MuralForm()
    
    # Usar HTTP_REFERER como fallback
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_murais')
    
    context = {
        'form': form,
        'acao': 'incluir',
        'model_verbose_name': 'Mural da Paróquia',
        'next_url': next_url,
        'modo_detalhe': True,
        'mural_section': 'form',  # Seção: Formulário (para CSS)
    }
    
    return render(request, 'admin_area/tpl_mural.html', context)


@login_required
def detalhar_mural(request, mural_id):
    """
    Visualiza os detalhes de um mural
    """
    mural = get_object_or_404(TBMURAL, MUR_ID=mural_id)
    
    # Contar fotos
    fotos_count = sum([
        1 if mural.MUR_foto1_mural else 0,
        1 if mural.MUR_foto2_mural else 0,
        1 if mural.MUR_foto3_mural else 0,
        1 if mural.MUR_foto4_mural else 0,
        1 if mural.MUR_foto5_mural else 0,
    ])
    
    # Contar legendas
    legendas_count = sum([
        1 if mural.MUR_legenda1_mural else 0,
        1 if mural.MUR_legenda2_mural else 0,
        1 if mural.MUR_legenda3_mural else 0,
        1 if mural.MUR_legenda4_mural else 0,
        1 if mural.MUR_legenda5_mural else 0,
    ])
    
    # Usar HTTP_REFERER como fallback
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_murais')
    
    context = {
        'mural': mural,
        'acao': 'consultar',
        'model_verbose_name': 'Mural da Paróquia',
        'next_url': next_url,
        'modo_detalhe': True,
        'fotos_count': fotos_count,
        'legendas_count': legendas_count,
        'mural_section': 'detail',  # Seção: Detalhes (para CSS)
    }
    
    return render(request, 'admin_area/tpl_mural.html', context)


@login_required
def editar_mural(request, mural_id):
    """
    Edita um mural existente
    """
    mural = get_object_or_404(TBMURAL, MUR_ID=mural_id)
    
    if request.method == 'POST':
        form = MuralForm(request.POST, request.FILES, instance=mural)
        if form.is_valid():
            mural = form.save(commit=False)
            
            # Redimensionar imagens antes de salvar
            campos_foto = [
                'MUR_foto1_mural', 'MUR_foto2_mural', 'MUR_foto3_mural',
                'MUR_foto4_mural', 'MUR_foto5_mural'
            ]
            
            for campo in campos_foto:
                if campo in request.FILES:
                    imagem_redimensionada = redimensionar_imagem(request.FILES[campo])
                    if imagem_redimensionada:
                        setattr(mural, campo, imagem_redimensionada)
            
            mural.save()
            messages.success(request, 'Mural atualizado com sucesso!')
            return redirect('app_igreja:listar_murais')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = MuralForm(instance=mural)
    
    # Usar HTTP_REFERER como fallback
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_murais')
    
    context = {
        'form': form,
        'mural': mural,
        'acao': 'editar',
        'model_verbose_name': 'Mural da Paróquia',
        'next_url': next_url,
        'modo_detalhe': True,
        'mural_section': 'form',  # Seção: Formulário (para CSS)
    }
    
    return render(request, 'admin_area/tpl_mural.html', context)


@login_required
def excluir_mural(request, mural_id):
    """
    Exclui um mural
    """
    mural = get_object_or_404(TBMURAL, MUR_ID=mural_id)
    
    if request.method == 'POST':
        mural.delete()
        messages.success(request, 'Mural excluído com sucesso!')
        return redirect('app_igreja:listar_murais')
    
    # Contar fotos
    fotos_count = sum([
        1 if mural.MUR_foto1_mural else 0,
        1 if mural.MUR_foto2_mural else 0,
        1 if mural.MUR_foto3_mural else 0,
        1 if mural.MUR_foto4_mural else 0,
        1 if mural.MUR_foto5_mural else 0,
    ])
    
    # Usar HTTP_REFERER como fallback
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_murais')
    
    context = {
        'mural': mural,
        'acao': 'excluir',
        'model_verbose_name': 'Mural da Paróquia',
        'next_url': next_url,
        'modo_detalhe': True,
        'fotos_count': fotos_count,
        'mural_section': 'delete',  # Seção: Exclusão (para CSS)
    }
    
    return render(request, 'admin_area/tpl_mural.html', context)

