from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from ...models.area_admin.models_oracoes import TBORACOES
from ...models.area_admin.models_paroquias import TBPAROQUIA
from ...forms.area_admin.forms_oracoes import OracaoPublicoForm


def meus_pedidos_oracoes(request):
    """
    Área pública para consultar pedidos de orações pelo telefone
    """
    # Buscar paróquia
    paroquia = TBPAROQUIA.objects.first()
    
    # Busca por telefone
    telefone = request.GET.get('telefone', '').strip()
    oracoes = None
    resultados_encontrados = False
    
    if telefone:
        # Remove caracteres não numéricos para busca
        telefone_limpo = ''.join(filter(str.isdigit, telefone))
        
        if len(telefone_limpo) >= 10:
            # Buscar por telefone (com e sem formatação)
            oracoes = TBORACOES.objects.filter(
                Q(ORA_telefone_pedinte__icontains=telefone_limpo) | 
                Q(ORA_telefone_pedinte__icontains=telefone)
            ).filter(ORA_ativo=True).order_by('-ORA_data_pedido')
            
            resultados_encontrados = oracoes.exists()
            
            if not resultados_encontrados:
                messages.info(request, f'Nenhum pedido de oração encontrado para o telefone {telefone}')
        else:
            messages.warning(request, 'Digite um telefone válido com pelo menos 10 dígitos')
    
    # Paginação (se houver resultados)
    page_obj = None
    if oracoes:
        paginator = Paginator(oracoes, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    
    context = {
        'paroquia': paroquia,
        'telefone': telefone,
        'page_obj': page_obj,
        'resultados_encontrados': resultados_encontrados,
        'total_encontrado': oracoes.count() if oracoes else 0,
        'acao': 'listar',  # Define a ação
    }
    
    return render(request, 'area_publica/tpl_oracoes_publico.html', context)


@login_required(login_url='/login/')
def criar_pedido_oracao_publico(request):
    """
    Criar novo pedido de oração (requer login)
    """
    if request.method == 'POST':
        form = OracaoPublicoForm(request.POST)
        
        if form.is_valid():
            oracao = form.save(commit=False)
            oracao.ORA_usuario_id = request.user
            oracao.ORA_status = 'PENDENTE'  # Sempre inicia como pendente
            oracao.ORA_ativo = True  # Sempre ativo quando criado
            oracao.save()
            messages.success(request, 'Pedido de oração criado com sucesso!')
            return redirect('app_igreja:meus_pedidos_oracoes')
        else:
            messages.error(request, 'Erro ao criar pedido de oração. Verifique os dados.')
    else:
        form = OracaoPublicoForm()
    
    paroquia = TBPAROQUIA.objects.first()
    
    context = {
        'form': form,
        'paroquia': paroquia,
        'acao': 'criar',  # Define a ação
    }
    
    return render(request, 'area_publica/tpl_oracoes_publico.html', context)


def detalhar_oracao_publico(request, oracao_id):
    """
    Detalhar pedido de oração (área pública)
    """
    oracao = get_object_or_404(TBORACOES, id=oracao_id, ORA_ativo=True)
    paroquia = TBPAROQUIA.objects.first()
    
    context = {
        'oracao': oracao,
        'paroquia': paroquia,
        'acao': 'consultar',  # Define a ação
    }
    
    return render(request, 'area_publica/tpl_oracoes_publico.html', context)
