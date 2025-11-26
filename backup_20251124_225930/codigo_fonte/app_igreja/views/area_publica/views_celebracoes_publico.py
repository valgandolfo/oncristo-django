"""
==================== VIEWS PÚBLICAS DE CELEBRAÇÕES ====================
Views para agendamento público de celebrações via WhatsApp
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from datetime import date
import re
import logging

from ...models.area_admin.models_celebracoes import TBCELEBRACOES
from ...models.area_admin.models_paroquias import TBPAROQUIA
from ...forms.area_publica.forms_celebracoes_publico import CelebracaoPublicoForm

logger = logging.getLogger(__name__)


def limpar_telefone(telefone):
    """Remove caracteres não numéricos do telefone"""
    if not telefone:
        return None
    return re.sub(r'[^\d]', '', str(telefone))


def agendar_celebracao_publico(request):
    """
    View pública para agendar celebrações
    Aceita parâmetro 'telefone' via query string para pré-preencher
    Permite agendar múltiplas celebrações
    """
    # Verificar se veio telefone via URL (do WhatsApp)
    telefone_url = request.GET.get('telefone', '').strip()
    telefone_readonly = bool(telefone_url)
    
    # Debug: logar o telefone recebido
    if telefone_url:
        logger.info(f"📞 Telefone recebido via URL: {telefone_url}")
    
    if request.method == 'POST':
        form = CelebracaoPublicoForm(request.POST, telefone_readonly=telefone_readonly)
        
        if form.is_valid():
            try:
                celebracao = form.save()
                
                messages.success(
                    request, 
                    f'Celebração agendada com sucesso! {celebracao.CEL_nome_solicitante}, '
                    f'seu agendamento para {celebracao.get_CEL_tipo_celebracao_display()} '
                    f'no dia {celebracao.CEL_data_celebracao.strftime("%d/%m/%Y")} às {celebracao.CEL_horario.strftime("%H:%M")} '
                    f'foi registrado. Em breve entraremos em contato para confirmar.'
                )
                
                # Não redirecionar - permanecer na mesma página para permitir novo agendamento
                # Criar novo formulário limpo, mantendo o telefone se vier da URL
                initial_data = {}
                if telefone_url:
                    telefone_limpo = limpar_telefone(telefone_url)
                    if telefone_limpo and telefone_limpo.startswith('55'):
                        telefone_limpo = telefone_limpo[2:]
                    initial_data['CEL_telefone'] = telefone_limpo
                
                form = CelebracaoPublicoForm(initial=initial_data, telefone_readonly=telefone_readonly, telefone_initial=initial_data.get('CEL_telefone'))
                
            except Exception as e:
                logger.error(f"Erro ao agendar celebração: {str(e)}")
                messages.error(request, f'Erro ao agendar celebração: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        # Pré-preencher telefone se vier da URL
        initial_data = {}
        if telefone_url:
            # Limpar telefone
            telefone_limpo = limpar_telefone(telefone_url)
            # Remover código do país se existir
            if telefone_limpo and telefone_limpo.startswith('55'):
                telefone_limpo = telefone_limpo[2:]
            
            initial_data['CEL_telefone'] = telefone_limpo
            
            # Debug: logar o telefone formatado
            logger.info(f"📞 Telefone formatado para o form: {telefone_limpo}")
        
        form = CelebracaoPublicoForm(initial=initial_data, telefone_readonly=telefone_readonly, telefone_initial=initial_data.get('CEL_telefone'))
    
    # Buscar paróquia
    paroquia = TBPAROQUIA.objects.first()
    
    # Buscar celebrações agendadas pelo mesmo telefone (para mostrar histórico)
    celebracaoes_agendadas = None
    if telefone_url:
        telefone_limpo = limpar_telefone(telefone_url)
        if telefone_limpo and telefone_limpo.startswith('55'):
            telefone_limpo = telefone_limpo[2:]
        
        # Buscar todas as celebrações deste telefone (com e sem formatação)
        celebracaoes_agendadas = TBCELEBRACOES.objects.filter(
            Q(CEL_telefone__icontains=telefone_limpo)
        ).order_by('-CEL_data_celebracao', 'CEL_horario')[:10]  # Últimas 10
    
    context = {
        'form': form,
        'paroquia': paroquia,
        'telefone_readonly': telefone_readonly,
        'telefone_url': telefone_url,
        'celebracaoes_agendadas': celebracaoes_agendadas,
    }
    
    return render(request, 'area_publica/bot_agendar_celebracao_publico.html', context)


def minhas_celebracaoes_publico(request):
    """
    Área pública para consultar celebrações agendadas pelo telefone
    """
    # Buscar paróquia
    paroquia = TBPAROQUIA.objects.first()
    
    # Busca por telefone
    telefone = request.GET.get('telefone', '').strip()
    celebracaoes = None
    resultados_encontrados = False
    
    if telefone:
        # Remove caracteres não numéricos para busca
        telefone_limpo = limpar_telefone(telefone)
        # Remover código do país se existir
        if telefone_limpo and telefone_limpo.startswith('55'):
            telefone_limpo = telefone_limpo[2:]
        
        if len(telefone_limpo) >= 10:
            # Buscar por telefone (com e sem formatação)
            celebracaoes = TBCELEBRACOES.objects.filter(
                Q(CEL_telefone__icontains=telefone_limpo)
            ).order_by('-CEL_data_celebracao', 'CEL_horario')
            
            resultados_encontrados = celebracaoes.exists()
            
            if not resultados_encontrados:
                messages.info(request, f'Nenhuma celebração encontrada para o telefone {telefone}')
        else:
            messages.warning(request, 'Digite um telefone válido com pelo menos 10 dígitos')
    
    context = {
        'paroquia': paroquia,
        'telefone': telefone,
        'celebracaoes': celebracaoes,
        'resultados_encontrados': resultados_encontrados,
        'total_encontrado': celebracaoes.count() if celebracaoes else 0,
    }
    
    return render(request, 'area_publica/bot_celebracoes_publico.html', context)

