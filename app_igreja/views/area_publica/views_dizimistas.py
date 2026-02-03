"""
==================== VIEWS PÚBLICAS DE DIZIMISTAS ====================
Arquivo com views específicas para cadastro público de Dizimistas
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json

from ...forms.area_publica.forms_dizimistas import DizimistaPublicoForm
from ...models.area_admin.models_dizimistas import TBDIZIMISTAS, limpar_telefone_para_display
import re


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


def quero_ser_dizimista(request):
    """
    View para cadastro público de dizimistas
    Acesso público - não requer login (especialmente quando vem do chatbot)
    Aceita parâmetro 'telefone' via query string para pré-preencher e tornar readonly
    """
    
    # Verificar se veio telefone via URL (do WhatsApp)
    telefone_url = request.GET.get('telefone', '').strip()
    telefone_readonly = bool(telefone_url)
    
    # Debug: logar o telefone recebido
    if telefone_url:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"📞 Telefone recebido via URL: {telefone_url}")
    
    if request.method == 'POST':
        form = DizimistaPublicoForm(request.POST)
        
        if form.is_valid():
            try:
                dizimista = form.save(commit=False)
                
                # Formatar telefone antes de salvar (especialmente se veio do chatbot)
                if dizimista.DIS_telefone:
                    dizimista.DIS_telefone = formatar_telefone_para_salvar(dizimista.DIS_telefone)
                
                # Definir status como pendente para novos cadastros públicos
                dizimista.DIS_status = False
                dizimista.save()
                
                messages.success(
                    request, 
                    f'Cadastro realizado com sucesso! {dizimista.DIS_nome}, '
                    f'seu telefone {dizimista.DIS_telefone} foi registrado. '
                    f'Em breve entraremos em contato para confirmar seus dados.'
                )
                # Voltar à tela anterior (mesma do botão Voltar)
                url_retorno = reverse('app_igreja:app_servicos') if request.GET.get('modo') == 'app' or request.session.get('modo_app') else reverse('home')
                return redirect(url_retorno)
                
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        # Pré-preencher telefone se vier da URL
        initial_data = {}
        if telefone_url:
            telefone_formatado = formatar_telefone_para_salvar(telefone_url)
            initial_data['DIS_telefone'] = telefone_formatado
            
            # Debug: logar o telefone formatado
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"📞 Telefone formatado para o form: {telefone_formatado}")
        
        form = DizimistaPublicoForm(initial=initial_data)
    
    # Determinar URL de retorno baseada no modo
    if request.GET.get('modo') == 'app' or request.session.get('modo_app'):
        url_retorno = reverse('app_igreja:app_servicos')
    else:
        url_retorno = reverse('home')

    context = {
        'form': form,
        'titulo': 'Quero ser Dizimista',
        'subtitulo': 'Cadastre-se para contribuir com nossa paróquia',
        'paroquia': getattr(request, 'paroquia', None),
        'telefone_readonly': telefone_readonly,
        'telefone_url': telefone_url,
        'url_retorno': url_retorno,
    }
    
    return render(request, 'area_publica/bot_dizimistas_publico.html', context)


# A busca de CEP agora é feita diretamente pelo JavaScript no template
# usando a API ViaCEP via JSONP (sem necessidade de backend)


def verificar_telefone_ajax(request):
    """
    Verifica se o telefone já está cadastrado
    """
    telefone = request.GET.get('telefone', '')
    
    if telefone:
        existe = TBDIZIMISTAS.objects.filter(DIS_telefone=telefone).exists()
        return JsonResponse({'existe': existe})
    
    return JsonResponse({'existe': False})
