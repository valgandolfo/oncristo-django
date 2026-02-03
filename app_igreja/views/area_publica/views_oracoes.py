from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
import re

from ...models.area_admin.models_oracoes import TBORACOES, limpar_telefone_para_display
from ...models.area_admin.models_paroquias import TBPAROQUIA
from ...forms.area_admin.forms_oracoes import OracaoPublicoForm


def formatar_telefone_para_salvar(telefone):
    """
    Formata telefone para salvar no banco no formato (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
    Remove código do país (55) se existir
    """
    if not telefone:
        return telefone
    
    # Remove caracteres não numéricos
    numeros = ''.join(filter(str.isdigit, str(telefone)))
    
    # Remove código do país (55) se existir
    if numeros.startswith('55') and len(numeros) > 11:
        numeros = numeros[2:]
    
    # Formata conforme o tamanho
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    elif len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    else:
        # Se não tiver tamanho válido, retorna apenas números
        return numeros


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
    
    # Determinar URL de retorno baseada no modo
    from django.urls import reverse
    if request.GET.get('modo') == 'app' or request.session.get('modo_app'):
        url_retorno = reverse('app_igreja:app_servicos')
    else:
        url_retorno = reverse('home')

    context = {
        'paroquia': paroquia,
        'telefone': telefone,
        'page_obj': page_obj,
        'resultados_encontrados': resultados_encontrados,
        'total_encontrado': oracoes.count() if oracoes else 0,
        'acao': 'listar',  # Define a ação
        'url_retorno': url_retorno,
    }
    
    return render(request, 'area_publica/bot_oracoes_publico.html', context)


def criar_pedido_oracao_publico(request):
    """
    Criar novo pedido de oração (área pública - não requer login)
    Aceita parâmetro 'telefone' via query string para pré-preencher (do chatbot)
    """
    # Verificar se veio telefone via URL (do WhatsApp/chatbot)
    telefone_url = request.GET.get('telefone', '').strip()
    telefone_readonly = bool(telefone_url)
    
    if request.method == 'POST':
        form = OracaoPublicoForm(request.POST)
        
        if form.is_valid():
            oracao = form.save(commit=False)
            
            # Formatar telefone antes de salvar (especialmente se veio do chatbot)
            if oracao.ORA_telefone_pedinte:
                oracao.ORA_telefone_pedinte = formatar_telefone_para_salvar(oracao.ORA_telefone_pedinte)
            
            # Se o usuário estiver logado, associar ao usuário, senão deixar None
            if request.user.is_authenticated:
                oracao.ORA_usuario_id = request.user
            else:
                oracao.ORA_usuario_id = None
            oracao.ORA_status = 'PENDENTE'  # Sempre inicia como pendente
            oracao.ORA_ativo = True  # Sempre ativo quando criado
            oracao.save()
            messages.success(request, 'Pedido de oração criado com sucesso!')
            
            # Se estiver no modo app, redirecionar para a home do app
            if request.GET.get('modo') == 'app' or request.session.get('modo_app'):
                return redirect('app_igreja:app_servicos')

            # Se veio do chatbot (com telefone na URL), redirecionar para home
            if telefone_url:
                return redirect('home')
            
            # Redirecionar para home se não estiver logado, senão para lista
            if request.user.is_authenticated:
                return redirect('app_igreja:meus_pedidos_oracoes')
            else:
                return redirect('/')
        else:
            messages.error(request, 'Erro ao criar pedido de oração. Verifique os dados.')
    else:
        # Pré-preencher telefone se vier da URL (do chatbot)
        initial_data = {}
        if telefone_url:
            telefone_formatado = formatar_telefone_para_salvar(telefone_url)
            initial_data['ORA_telefone_pedinte'] = telefone_formatado
        
        form = OracaoPublicoForm(initial=initial_data)
    
    paroquia = TBPAROQUIA.objects.first()
    
    # Determinar URL de retorno baseada no modo
    from django.urls import reverse
    if request.GET.get('modo') == 'app' or request.session.get('modo_app'):
        url_retorno = reverse('app_igreja:app_servicos')
    else:
        url_retorno = reverse('home')

    context = {
        'form': form,
        'paroquia': paroquia,
        'acao': 'criar',  # Define a ação
        'telefone_readonly': telefone_readonly,
        'telefone_url': telefone_url,
        'url_retorno': url_retorno,
    }
    
    return render(request, 'area_publica/bot_oracoes_publico.html', context)


def detalhar_oracao_publico(request, oracao_id):
    """
    Detalhar pedido de oração (área pública)
    """
    oracao = get_object_or_404(TBORACOES, id=oracao_id, ORA_ativo=True)
    paroquia = TBPAROQUIA.objects.first()
    
    # Determinar URL de retorno baseada no modo
    from django.urls import reverse
    if request.GET.get('modo') == 'app' or request.session.get('modo_app'):
        url_retorno = reverse('app_igreja:app_servicos')
    else:
        url_retorno = reverse('home')

    context = {
        'oracao': oracao,
        'paroquia': paroquia,
        'acao': 'consultar',  # Define a ação
        'url_retorno': url_retorno,
    }
    
    return render(request, 'area_publica/bot_oracoes_publico.html', context)
