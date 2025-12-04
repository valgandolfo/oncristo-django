"""
==================== VIEWS PÚBLICAS DE COLABORADORES ====================
Views para cadastro público de colaboradores usando telefone como chave
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.contrib import messages
import requests
import re

from ...models.area_admin.models_colaboradores import TBCOLABORADORES
from ...forms.area_publica.forms_colaboradores_publico import ColaboradorPublicoForm


def limpar_telefone(telefone):
    """Remove caracteres não numéricos do telefone"""
    if not telefone:
        return None
    return re.sub(r'[^\d]', '', str(telefone))


def formatar_telefone(telefone):
    """Formata telefone para exibição"""
    telefone_limpo = limpar_telefone(telefone)
    if telefone_limpo and len(telefone_limpo) >= 10:
        if len(telefone_limpo) == 11:
            return f"({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}"
        else:
            return f"({telefone_limpo[:2]}) {telefone_limpo[2:6]}-{telefone_limpo[6:]}"
    return telefone


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


def quero_ser_colaborador(request):
    """
    View pública para cadastro de colaborador via WhatsApp
    Aceita parâmetro 'telefone' via query string para pré-preencher e tornar readonly
    Não requer login
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
        form = ColaboradorPublicoForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                colaborador = form.save(commit=False)
                
                # Formatar telefone antes de salvar (especialmente se veio do chatbot)
                if colaborador.COL_telefone:
                    colaborador.COL_telefone = formatar_telefone_para_salvar(colaborador.COL_telefone)
                
                # Definir status como PENDENTE
                colaborador.COL_status = 'PENDENTE'
                colaborador.COL_membro_ativo = False
                colaborador.save()
                
                # Redirecionar para home com mensagem de sucesso
                messages.success(
                    request, 
                    f'Cadastro realizado com sucesso! {colaborador.COL_nome_completo}, '
                    f'seu telefone {colaborador.COL_telefone} foi registrado. '
                    f'Em breve entraremos em contato para confirmar seus dados.'
                )
                # Redirecionar para a home (raiz do app)
                return redirect('/')
                
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        # Pré-preencher telefone se vier da URL
        initial_data = {}
        if telefone_url:
            telefone_formatado = formatar_telefone_para_salvar(telefone_url)
            initial_data['COL_telefone'] = telefone_formatado
            
            # Debug: logar o telefone formatado
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"📞 Telefone formatado para o form: {telefone_formatado}")
        
        form = ColaboradorPublicoForm(initial=initial_data)
    
    context = {
        'form': form,
        'titulo': 'Quero ser Colaborador',
        'subtitulo': 'Cadastre-se para colaborar com nossa paróquia',
        'paroquia': getattr(request, 'paroquia', None),
        'telefone_readonly': telefone_readonly,
        'telefone_url': telefone_url
    }
    
    # Usar template específico para WhatsApp se vier telefone via URL
    template = 'area_publica/bot_colaboradores_publico.html' if telefone_readonly else 'area_publica/tpl_colaboradores_publico.html'
    return render(request, template, context)


def cadastro_colaborador_publico(request, telefone):
    """
    Página pública de cadastro de colaborador usando telefone como chave
    Similar ao Flask app_membros.py
    """
    # Limpa o telefone
    telefone_limpo = limpar_telefone(telefone)
    
    if not telefone_limpo or len(telefone_limpo) < 10:
        raise Http404("Telefone inválido")
    
    # Busca se já existe colaborador com este telefone
    colaborador = None
    try:
        colaborador = TBCOLABORADORES.objects.get(COL_telefone=telefone_limpo)
    except TBCOLABORADORES.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = ColaboradorPublicoForm(request.POST, request.FILES, instance=colaborador)
        
        if form.is_valid():
            # Garante que o telefone está correto
            instance = form.save(commit=False)
            instance.COL_telefone = telefone_limpo
            instance.COL_status = 'PENDENTE'
            instance.save()
            
            messages.success(request, 'Dados salvos com sucesso!')
            return render(request, 'area_publica/tpl_colaboradores_publico.html', {
                'form': form,
                'colaborador': instance,
                'telefone': formatar_telefone(telefone_limpo),
                'telefone_limpo': telefone_limpo,
                'sucesso': True
            })
        else:
            messages.error(request, 'Erro ao salvar dados. Verifique os campos.')
    else:
        form = ColaboradorPublicoForm(instance=colaborador)
        # Define o telefone no formulário
        form.fields['COL_telefone'].initial = formatar_telefone(telefone_limpo)
    
    context = {
        'form': form,
        'colaborador': colaborador,
        'telefone': formatar_telefone(telefone_limpo),
        'telefone_limpo': telefone_limpo,
        'status': colaborador.COL_status if colaborador else None,
    }
    
    return render(request, 'area_publica/tpl_colaboradores_publico.html', context)


@require_http_methods(["GET"])
def api_buscar_cep(request, cep):
    """
    API para buscar endereço por CEP usando ViaCEP
    Similar ao Flask app_membros.py
    """
    try:
        # Remove caracteres não numéricos
        cep_limpo = re.sub(r'[^\d]', '', str(cep))
        
        if not cep_limpo or len(cep_limpo) != 8:
            return JsonResponse({
                'sucesso': False,
                'erro': 'CEP inválido'
            })
        
        # Busca na API ViaCEP
        url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            dados = response.json()
            
            if 'erro' in dados:
                return JsonResponse({
                    'sucesso': False,
                    'erro': 'CEP não encontrado'
                })
            
            # Formata CEP
            cep_formatado = f"{cep_limpo[:5]}-{cep_limpo[5:]}"
            
            return JsonResponse({
                'sucesso': True,
                'cep': cep_formatado,
                'endereco': dados.get('logradouro', ''),
                'bairro': dados.get('bairro', ''),
                'cidade': dados.get('localidade', ''),
                'estado': dados.get('uf', '')
            })
        else:
            return JsonResponse({
                'sucesso': False,
                'erro': f'Erro na consulta: {response.status_code}'
            })
            
    except requests.exceptions.Timeout:
        return JsonResponse({
            'sucesso': False,
            'erro': 'Timeout na consulta'
        })
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'sucesso': False,
            'erro': 'Erro na conexão'
        })
    except Exception as e:
        return JsonResponse({
            'sucesso': False,
            'erro': 'Erro inesperado'
        })


@require_http_methods(["DELETE"])
def api_excluir_colaborador(request, telefone):
    """
    API para excluir colaborador pelo telefone
    Similar ao Flask app_membros.py
    """
    try:
        telefone_limpo = limpar_telefone(telefone)
        
        if not telefone_limpo:
            return JsonResponse({
                'sucesso': False,
                'erro': 'Telefone inválido'
            })
        
        colaborador = get_object_or_404(TBCOLABORADORES, COL_telefone=telefone_limpo)
        colaborador.delete()
        
        return JsonResponse({
            'sucesso': True,
            'mensagem': 'Colaborador excluído com sucesso'
        })
        
    except Exception as e:
        return JsonResponse({
            'sucesso': False,
            'erro': str(e)
        })

