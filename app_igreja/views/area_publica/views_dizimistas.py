"""
==================== VIEWS PÚBLICAS DE DIZIMISTAS ====================
Arquivo com views específicas para cadastro público de Dizimistas
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json

from ...forms.area_publica.forms_dizimistas import DizimistaPublicoForm
from ...models.area_admin.models_dizimistas import TBDIZIMISTAS


@login_required
def quero_ser_dizimista(request):
    """
    View para cadastro público de dizimistas
    Requer que o usuário esteja logado
    """
    
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
        form = DizimistaPublicoForm()
    
    context = {
        'form': form,
        'titulo': 'Quero ser Dizimista',
        'subtitulo': 'Cadastre-se para contribuir com nossa paróquia',
        'paroquia': getattr(request, 'paroquia', None)
    }
    
    return render(request, 'area_publica/tpl_dizimistas_publico.html', context)


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
