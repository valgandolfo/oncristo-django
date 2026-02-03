"""
==================== VIEWS CADASTRO DE COLABORADOR ====================
View para cadastro público de colaboradores (rota: cadastro-colaborador/)
Nova nomenclatura baseada na funcionalidade/rota para melhor organização
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.urls import reverse
import json
import re
import logging
import requests

from ...forms.area_publica.form_cadastro_colaborador import CadastroColaboradorForm
from ...models.area_admin.models_colaboradores import TBCOLABORADORES

logger = logging.getLogger(__name__)


def limpar_telefone(telefone):
    """Remove caracteres não numéricos do telefone"""
    if not telefone:
        return None
    return re.sub(r'[^\d]', '', str(telefone))


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


def cadastro_colaborador(request):
    """
    View principal para cadastro público de colaboradores
    
    Funcionalidades:
    - Cadastro público de novos colaboradores
    - Pré-preenchimento via telefone na URL (integração WhatsApp)
    - Suporte ao modo app (WebView)
    - Validação completa de dados
    - Sistema de status: PENDENTE → APROVADO → ATIVO
    
    URL: cadastro-colaborador/
    Template: bot_colaboradores_publico.html
    """
    
    # Verificar se veio telefone via URL (do WhatsApp)
    telefone_url = request.GET.get('telefone', '').strip()
    telefone_readonly = bool(telefone_url)
    
    # Debug: logar o telefone recebido
    if telefone_url:
        logger.info(f"📞 Telefone recebido via URL: {telefone_url}")
    
    if request.method == 'POST':
        form = CadastroColaboradorForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                colaborador = form.save(commit=False)
                
                # Formatar telefone antes de salvar
                if colaborador.COL_telefone:
                    colaborador.COL_telefone = formatar_telefone_para_salvar(colaborador.COL_telefone)
                
                # Definir status inicial como PENDENTE para novos cadastros públicos
                colaborador.COL_status = 'PENDENTE'
                colaborador.COL_membro_ativo = False
                colaborador.save()
                
                messages.success(
                    request, 
                    f'Cadastro realizado com sucesso! {colaborador.COL_nome_completo}, '
                    f'seu telefone {colaborador.COL_telefone} foi registrado. '
                    f'Em breve entraremos em contato para confirmar seus dados e definir '
                    f'sua função: {colaborador.COL_funcao_pretendida or "A definir"}.'
                )
                
                # Redirecionar baseado no contexto
                if request.GET.get('modo') == 'app' or request.session.get('modo_app'):
                    return redirect('app_igreja:app_servicos')
                
                if telefone_url:
                    return redirect('home')
                
                return redirect('app_igreja:cadastro_colaborador')
                
            except Exception as e:
                logger.error(f"Erro ao cadastrar colaborador: {str(e)}", exc_info=True)
                messages.error(request, f'Erro ao cadastrar: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
            logger.warning(f"Erros no formulário: {form.errors}")
    
    else:
        # GET: Preparar formulário inicial
        initial_data = {}
        if telefone_url:
            telefone_formatado = formatar_telefone_para_salvar(telefone_url)
            initial_data['COL_telefone'] = telefone_formatado
            
            # Debug: logar o telefone formatado
            logger.info(f"📞 Telefone formatado para o form: {telefone_formatado}")
        
        form = CadastroColaboradorForm(initial=initial_data)
    
    # Determinar URL de retorno baseada no modo
    if request.GET.get('modo') == 'app' or request.session.get('modo_app'):
        url_retorno = reverse('app_igreja:app_servicos')
    else:
        url_retorno = reverse('home')

    context = {
        'form': form,
        'titulo': 'Cadastro de Colaborador',
        'subtitulo': 'Cadastre-se para colaborar com nossa paróquia',
        'paroquia': getattr(request, 'paroquia', None),
        'telefone_readonly': telefone_readonly,
        'telefone_url': telefone_url,
        'url_retorno': url_retorno,
    }
    
    return render(request, 'area_publica/bot_colaboradores_publico.html', context)


def cadastro_colaborador_por_telefone(request, telefone):
    """
    View específica para cadastro com telefone na URL
    Compatibilidade com sistema existente
    
    URL: cadastro-colaborador/<str:telefone>/
    """
    # Redirecionar para view principal com telefone como parâmetro
    return redirect(f"{reverse('app_igreja:cadastro_colaborador')}?telefone={telefone}")


@csrf_exempt
@require_http_methods(["GET"])
def api_buscar_cep_colaborador(request, cep):
    """
    API para buscar CEP e preencher endereço automaticamente
    Integração com ViaCEP para melhor UX
    
    URL: cadastro-colaborador/api/cep/<str:cep>/
    """
    try:
        # Limpar CEP (remover caracteres não numéricos)
        cep_limpo = re.sub(r'[^\d]', '', cep)
        
        if len(cep_limpo) != 8:
            return JsonResponse({
                'success': False,
                'error': 'CEP deve ter 8 dígitos'
            }, status=400)
        
        # Buscar CEP na API ViaCEP
        response = requests.get(f'https://viacep.com.br/ws/{cep_limpo}/json/', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('erro'):
                return JsonResponse({
                    'success': False,
                    'error': 'CEP não encontrado'
                }, status=404)
            
            return JsonResponse({
                'success': True,
                'data': {
                    'logradouro': data.get('logradouro', ''),
                    'bairro': data.get('bairro', ''),
                    'localidade': data.get('localidade', ''),
                    'uf': data.get('uf', ''),
                    'complemento': data.get('complemento', ''),
                    'cep': data.get('cep', '')
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Erro ao consultar CEP'
            }, status=500)
            
    except requests.Timeout:
        return JsonResponse({
            'success': False,
            'error': 'Timeout ao consultar CEP'
        }, status=408)
    except Exception as e:
        logger.error(f"Erro na API de CEP: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Erro interno do servidor'
        }, status=500)


@csrf_exempt  
@require_http_methods(["POST"])
def api_excluir_colaborador(request, telefone):
    """
    API para excluir colaborador por telefone
    Usado em casos específicos de limpeza de dados
    
    URL: cadastro-colaborador/api/excluir/<str:telefone>/
    """
    try:
        telefone_formatado = formatar_telefone_para_salvar(telefone)
        
        colaborador = get_object_or_404(TBCOLABORADORES, COL_telefone=telefone_formatado)
        
        # Só permite excluir se estiver PENDENTE (não confirmado ainda)
        if colaborador.COL_status != 'PENDENTE':
            return JsonResponse({
                'success': False,
                'error': 'Só é possível excluir colaboradores pendentes'
            }, status=400)
        
        nome = colaborador.COL_nome_completo
        colaborador.delete()
        
        logger.info(f"Colaborador excluído: {nome} - {telefone_formatado}")
        
        return JsonResponse({
            'success': True,
            'message': f'Colaborador {nome} excluído com sucesso'
        })
        
    except Http404:
        return JsonResponse({
            'success': False,
            'error': 'Colaborador não encontrado'
        }, status=404)
    except Exception as e:
        logger.error(f"Erro ao excluir colaborador: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Erro interno do servidor'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def verificar_telefone_colaborador_ajax(request):
    """
    API para verificar se telefone já está cadastrado
    Usada pelo JavaScript no formulário para validação em tempo real
    
    URL: cadastro-colaborador/verificar-telefone/
    """
    telefone = request.GET.get('telefone', '').strip()
    
    if telefone:
        telefone_formatado = formatar_telefone_para_salvar(telefone)
        existe = TBCOLABORADORES.objects.filter(COL_telefone=telefone_formatado).exists()
        
        logger.debug(f"Verificação de telefone colaborador: {telefone} -> {telefone_formatado} -> Existe: {existe}")
        
        if existe:
            # Buscar dados básicos para mostrar informação útil
            colaborador = TBCOLABORADORES.objects.filter(COL_telefone=telefone_formatado).first()
            return JsonResponse({
                'existe': True,
                'telefone_formatado': telefone_formatado,
                'nome': colaborador.COL_nome_completo if colaborador else '',
                'status': colaborador.COL_status if colaborador else '',
                'funcao': colaborador.COL_funcao_pretendida if colaborador else ''
            })
        else:
            return JsonResponse({
                'existe': False,
                'telefone_formatado': telefone_formatado
            })
    
    return JsonResponse({'existe': False, 'telefone_formatado': ''})


# Aliases para compatibilidade com código existente
# TODO: Remover após migração completa
quero_ser_colaborador = cadastro_colaborador
cadastro_colaborador_publico = cadastro_colaborador_por_telefone
api_buscar_cep = api_buscar_cep_colaborador
api_excluir_colaborador_old = api_excluir_colaborador