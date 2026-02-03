from django.shortcuts import render
import logging

from app_igreja.models.area_admin.models_paroquias import TBPAROQUIA
from app_igreja.models.area_admin.models_visual import TBVISUAL

logger = logging.getLogger(__name__)

def get_contatos_paroquia():
    """Busca dados de contato da paróquia"""
    try:
        # Busca a paróquia (assumindo que há apenas uma)
        paroquia = TBPAROQUIA.objects.first()
        
        if not paroquia:
            return None
            
        # Monta endereço completo para o mapa
        endereco_completo = ""
        if paroquia.PAR_endereco:
            endereco_completo += paroquia.PAR_endereco
        if paroquia.PAR_bairro:
            endereco_completo += f", {paroquia.PAR_bairro}"
        if paroquia.PAR_cidade:
            endereco_completo += f", {paroquia.PAR_cidade}"
        if paroquia.PAR_uf:
            endereco_completo += f"/{paroquia.PAR_uf}"
        if paroquia.PAR_cep:
            endereco_completo += f", CEP: {paroquia.PAR_cep}"
            
        return {
            'paroquia': paroquia,
            'endereco_completo': endereco_completo.strip()
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar contatos da paróquia: {e}")
        return None

def contatos_publico(request):
    """Página pública de contatos"""
    try:
        # Busca dados de contato da paróquia
        dados_contato = get_contatos_paroquia()
        
        if not dados_contato:
            return render(request, 'area_publica/error.html', {
                'error_message': "Dados de contato não encontrados."
            }, status=404)
        
        # Busca configurações visuais
        visual = TBVISUAL.objects.first()
        
        # Determinar URL de retorno baseada no modo
        from django.urls import reverse
        if request.GET.get('modo') == 'app' or request.session.get('modo_app'):
            url_retorno = reverse('app_igreja:app_info')
        else:
            url_retorno = reverse('home')

        # Prepara os dados para o template
        context = {
            'paroquia': dados_contato['paroquia'],
            'endereco_completo': dados_contato['endereco_completo'],
            'visual': visual,
            'url_retorno': url_retorno,
        }
        
        # Renderiza o template
        return render(request, 'area_publica/tpl_contato.html', context)

    except Exception as e:
        logger.error(f"Erro na página de contatos: {str(e)}")
        return render(request, 'area_publica/error.html', {
            'error_message': f"Erro ao carregar contatos: {str(e)}"
        }, status=500)