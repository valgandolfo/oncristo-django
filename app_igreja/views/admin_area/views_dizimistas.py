from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from datetime import datetime
from functools import wraps

from ...models.area_admin.models_dizimistas import TBDIZIMISTAS, TBDOACAODIZIMO
from ...forms.area_admin.forms_dizimistas import DizimistaForm, DoacaoDizimoForm

def admin_required(view_func):
    """Decorator para verificar se o usuário é administrador"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Apenas superusuários podem acessar área admin
        if not request.user.is_superuser:
            messages.error(request, 'Acesso negado. Apenas administradores podem acessar esta área.')
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_required
@admin_required
def listar_dizimistas(request):
    """
    Lista todos os dizimistas com paginação
    """
    
    # Busca
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    # Controla se o usuário já executou uma busca (preencheu algum filtro ou navegou na paginação)
    busca_realizada = bool(query or status_filter or request.GET.get('page'))

    # Só carrega os registros no grid DEPOIS que o usuário aplicar um filtro
    if busca_realizada:
        dizimistas = TBDIZIMISTAS.objects.all()

        if query:
            dizimistas = dizimistas.filter(
                Q(DIS_nome__icontains=query)
                | Q(DIS_telefone__icontains=query)
                | Q(DIS_email__icontains=query)
                | Q(DIS_cidade__icontains=query)
            )

        if status_filter:
            if status_filter == 'ativo':
                dizimistas = dizimistas.filter(DIS_status=True)
            elif status_filter == 'pendente':
                dizimistas = dizimistas.filter(DIS_status=False)

        # Ordenação
        dizimistas = dizimistas.order_by('DIS_nome')
    else:
        # Queryset vazio até que o usuário faça a primeira busca
        dizimistas = TBDIZIMISTAS.objects.none()
    
    # Paginação
    paginator = Paginator(dizimistas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    total_dizimistas = TBDIZIMISTAS.objects.count()
    ativos = TBDIZIMISTAS.objects.filter(DIS_status=True).count()
    pendentes = TBDIZIMISTAS.objects.filter(DIS_status=False).count()
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
        'total_dizimistas': total_dizimistas,
        'ativos': ativos,
        'pendentes': pendentes,
        'modo_dashboard': True,
        'busca_realizada': busca_realizada,
    }
    
    return render(request, 'admin_area/tpl_dizimistas.html', context)


@login_required
@admin_required
def criar_dizimista(request):
    """
    Cria um novo dizimista
    """
    
    if request.method == 'POST':
        form = DizimistaForm(request.POST, request.FILES)
        
        if form.is_valid():
            dizimista = form.save()
            # Reconstruir URL com filtros preservados do POST (campos hidden)
            params = []
            if request.POST.get('q'):
                params.append(f"q={request.POST.get('q')}")
            if request.POST.get('status'):
                params.append(f"status={request.POST.get('status')}")
            if request.POST.get('page'):
                params.append(f"page={request.POST.get('page')}")
            
            query_string = '&'.join(params)
            if query_string:
                return redirect(f"{reverse('app_igreja:listar_dizimistas')}?{query_string}")
            return redirect('app_igreja:listar_dizimistas')
        else:
            messages.error(request, 'Erro ao cadastrar dizimista. Verifique os dados.')
    else:
        form = DizimistaForm()
    
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_dizimistas')
    context = {
        'form': form,
        'acao': 'incluir',
        'model_verbose_name': 'Dizimista',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_dizimistas.html', context)


@login_required
@admin_required
def detalhar_dizimista(request, dizimista_id):
    """
    Mostra detalhes de um dizimista
    """
    dizimista = get_object_or_404(TBDIZIMISTAS, id=dizimista_id)
    
    # Buscar doações do dizimista
    doacoes = TBDOACAODIZIMO.objects.filter(dizimista=dizimista).order_by('-data_vencimento')
    
    context = {
        'dizimista': dizimista,
        'doacoes': doacoes,
        'acao': 'consultar',
        'model_verbose_name': 'Dizimista',
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_dizimistas.html', context)


@login_required
@admin_required
def editar_dizimista(request, dizimista_id):
    """
    Edita um dizimista existente
    """
    dizimista = get_object_or_404(TBDIZIMISTAS, id=dizimista_id)
    
    if request.method == 'POST':
        form = DizimistaForm(request.POST, request.FILES, instance=dizimista)
        
        if form.is_valid():
            form.save()
            # Reconstruir URL com filtros preservados do POST (campos hidden)
            params = []
            if request.POST.get('q'):
                params.append(f"q={request.POST.get('q')}")
            if request.POST.get('status'):
                params.append(f"status={request.POST.get('status')}")
            if request.POST.get('page'):
                params.append(f"page={request.POST.get('page')}")
            
            query_string = '&'.join(params)
            if query_string:
                return redirect(f"{reverse('app_igreja:listar_dizimistas')}?{query_string}")
            return redirect('app_igreja:listar_dizimistas')
        else:
            messages.error(request, 'Erro ao atualizar dizimista. Verifique os campos.')
    else:
        form = DizimistaForm(instance=dizimista)
    
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_dizimistas')
    context = {
        'form': form,
        'dizimista': dizimista,
        'acao': 'editar',
        'model_verbose_name': 'Dizimista',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_dizimistas.html', context)


@login_required
@admin_required
def excluir_dizimista(request, dizimista_id):
    """
    Exclui um dizimista
    """
    dizimista = get_object_or_404(TBDIZIMISTAS, id=dizimista_id)
    
    if request.method == 'POST':
        dizimista.delete()
        # Reconstruir URL com filtros preservados do POST (campos hidden)
        params = []
        if request.POST.get('q'):
            params.append(f"q={request.POST.get('q')}")
        if request.POST.get('status'):
            params.append(f"status={request.POST.get('status')}")
        if request.POST.get('page'):
            params.append(f"page={request.POST.get('page')}")
        
        query_string = '&'.join(params)
        if query_string:
            return redirect(f"{reverse('app_igreja:listar_dizimistas')}?{query_string}")
        return redirect('app_igreja:listar_dizimistas')
    
    next_url = request.META.get('HTTP_REFERER') or reverse('app_igreja:listar_dizimistas')
    context = {
        'dizimista': dizimista,
        'acao': 'excluir',
        'model_verbose_name': 'Dizimista',
        'next_url': next_url,
        'modo_detalhe': True,
    }
    
    return render(request, 'admin_area/tpl_dizimistas.html', context)


@login_required
@admin_required
def dashboard_dizimistas(request):
    """
    Dashboard com estatísticas dos dizimistas
    """
    
    total_dizimistas = TBDIZIMISTAS.objects.count()
    ativos = TBDIZIMISTAS.objects.filter(DIS_status=True).count()
    pendentes = TBDIZIMISTAS.objects.filter(DIS_status=False).count()
    
    # Dizimistas por cidade
    dizimistas_por_cidade = TBDIZIMISTAS.objects.values('DIS_cidade').annotate(
        count=Count('DIS_id')
    ).order_by('-count')[:5]
    
    # Dizimistas por sexo
    masculinos = TBDIZIMISTAS.objects.filter(DIS_sexo='M').count()
    femininos = TBDIZIMISTAS.objects.filter(DIS_sexo='F').count()
    
    # Dizimistas cadastrados este mês
    hoje = datetime.now()
    inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    novos_mes = TBDIZIMISTAS.objects.filter(DIS_data_cadastro__gte=inicio_mes).count()
    
    context = {
        'total_dizimistas': total_dizimistas,
        'ativos': ativos,
        'pendentes': pendentes,
        'dizimistas_por_cidade': dizimistas_por_cidade,
        'masculinos': masculinos,
        'femininos': femininos,
        'novos_mes': novos_mes,
        'titulo': 'Dashboard de Dizimistas',
        'modo_dashboard': True,
    }
    
    return render(request, 'admin_area/tpl_dizimistas.html', context)


@csrf_exempt
def api_cep(request, cep):
    """API para buscar CEP"""
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Limpar CEP (remover caracteres não numéricos)
        cep_limpo = ''.join(filter(str.isdigit, cep))
        
        if len(cep_limpo) != 8:
            return JsonResponse({'error': 'CEP inválido'}, status=400)
        
        # Tentar buscar via ViaCEP
        import requests
        
        url = f'https://viacep.com.br/ws/{cep_limpo}/json/'
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'erro' not in data:
                return JsonResponse({
                    'cep': data.get('cep', ''),
                    'logradouro': data.get('logradouro', ''),
                    'bairro': data.get('bairro', ''),
                    'cidade': data.get('localidade', ''),
                    'estado': data.get('uf', ''),
                })
        
        return JsonResponse({'error': 'CEP não encontrado'}, status=404)
        
    except Exception as e:
        logger.error(f'Erro ao buscar CEP {cep}: {str(e)}')
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)
