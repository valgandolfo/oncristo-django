"""
==================== VIEWS CADASTRO DIZIMISTA PÚBLICO ====================
View para cadastro público de dizimistas (nomenclatura: cadastro_dizimista_pub)
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.urls import reverse
import json
import re
import logging

from ...forms.area_publica.forms_cadastro_dizimista_pub import CadastroDizimistaPubForm
from ...models.area_admin.models_dizimistas import TBDIZIMISTAS

logger = logging.getLogger(__name__)


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


def cadastro_dizimista_pub(request):
    """
    View principal para cadastro público de dizimistas (cadastro_dizimista_pub).
    URL: cadastro-dizimista-pub/ ou quero-ser-dizimista/
    Template: tpl_cadastro_dizimista_pub.html
    """
    telefone_url = request.GET.get('telefone', '').strip()
    telefone_readonly = bool(telefone_url)
    if telefone_url:
        logger.info(f"📞 Telefone recebido via URL: {telefone_url}")
    
    if request.method == 'POST':
        form = CadastroDizimistaPubForm(request.POST, request.FILES)
        
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
                logger.error(f"Erro ao cadastrar dizimista: {str(e)}", exc_info=True)
                messages.error(request, f'Erro ao cadastrar: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
            logger.warning(f"Erros no formulário: {form.errors}")
    
    else:
        # GET: Preparar formulário inicial
        initial_data = {}
        if telefone_url:
            telefone_formatado = formatar_telefone_para_salvar(telefone_url)
            initial_data['DIS_telefone'] = telefone_formatado
            
            # Debug: logar o telefone formatado
            logger.info(f"📞 Telefone formatado para o form: {telefone_formatado}")
        
        form = CadastroDizimistaPubForm(initial=initial_data)
    
    # Determinar URL de retorno baseada no modo
    if request.GET.get('modo') == 'app' or request.session.get('modo_app'):
        url_retorno = reverse('app_igreja:app_servicos')
    else:
        url_retorno = reverse('home')

    context = {
        'form': form,
        'titulo': 'Cadastro de Dizimista',
        'subtitulo': 'Cadastre-se para contribuir com nossa paróquia',
        'paroquia': getattr(request, 'paroquia', None),
        'telefone_readonly': telefone_readonly,
        'telefone_url': telefone_url,
        'url_retorno': url_retorno,
    }
    
    return render(request, 'area_publica/tpl_cadastro_dizimista_pub.html', context)


@csrf_exempt
@require_http_methods(["GET"])
def verificar_telefone_cadastro_dizimista_pub(request):
    """
    API para verificar se telefone já está cadastrado (cadastro_dizimista_pub).
    URL: cadastro-dizimista-pub/verificar-telefone/
    """
    telefone = request.GET.get('telefone', '').strip()
    
    if telefone:
        # Normalizar telefone para busca
        telefone_formatado = formatar_telefone_para_salvar(telefone)
        existe = TBDIZIMISTAS.objects.filter(DIS_telefone=telefone_formatado).exists()
        
        logger.debug(f"Verificação de telefone: {telefone} -> {telefone_formatado} -> Existe: {existe}")
        
        return JsonResponse({
            'existe': existe,
            'telefone_formatado': telefone_formatado
        })
    
    return JsonResponse({'existe': False, 'telefone_formatado': ''})


# Alias: quero-ser-dizimista/ usa a mesma view
quero_ser_dizimista = cadastro_dizimista_pub