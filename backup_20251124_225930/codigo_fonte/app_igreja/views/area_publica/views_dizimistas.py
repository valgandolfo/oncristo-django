"""
==================== VIEWS PÚBLICAS DE DIZIMISTAS ====================
Arquivo com views específicas para cadastro público de Dizimistas
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json

from ...forms.area_publica.forms_dizimistas import DizimistaPublicoForm
from ...models.area_admin.models_dizimistas import TBDIZIMISTAS


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
                # Definir status como pendente para novos cadastros públicos
                dizimista.DIS_status = False
                dizimista.save()
                
                messages.success(
                    request, 
                    f'Cadastro realizado com sucesso! {dizimista.DIS_nome}, '
                    f'seu telefone {dizimista.DIS_telefone} foi registrado. '
                    f'Em breve entraremos em contato para confirmar seus dados.'
                )
                return redirect('app_igreja:quero_ser_dizimista')
                
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        # Pré-preencher telefone se vier da URL
        initial_data = {}
        if telefone_url:
            # O telefone vem da URL já limpo (sem código do país, apenas números)
            # Remover qualquer caractere não numérico
            telefone_limpo = ''.join(filter(str.isdigit, telefone_url))
            
            # O telefone deve vir do DDD em diante (sem código do país)
            # Remover código do país se existir
            if telefone_limpo.startswith('55'):
                telefone_formatado = telefone_limpo[2:]  # Remove os primeiros 2 dígitos (55)
            else:
                telefone_formatado = telefone_limpo
            
            initial_data['DIS_telefone'] = telefone_formatado
            
            # Debug: logar o telefone formatado
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"📞 Telefone formatado para o form: {telefone_formatado}")
        
        form = DizimistaPublicoForm(initial=initial_data)
    
    context = {
        'form': form,
        'titulo': 'Quero ser Dizimista',
        'subtitulo': 'Cadastre-se para contribuir com nossa paróquia',
        'paroquia': getattr(request, 'paroquia', None),
        'telefone_readonly': telefone_readonly,
        'telefone_url': telefone_url
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
