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
from ...forms.area_publica.forms_celebracoes_agendadas_pub import CelebracaoAgendadaPubForm

logger = logging.getLogger(__name__)


def limpar_telefone(telefone):
    """Remove caracteres não numéricos e o código do país (55) do número do telefone"""
    if not telefone:
        return telefone
    
    # Remove caracteres não numéricos
    telefone_limpo = re.sub(r'[^\d]', '', str(telefone))
    
    # Remove código do país (55) se existir
    if telefone_limpo and telefone_limpo.startswith('55'):
        telefone_limpo = telefone_limpo[2:]  # Remove os primeiros 2 dígitos (55)
    
    return telefone_limpo


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


def agendar_celebracoes_agendadas_pub(request):
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
        form = CelebracaoAgendadaPubForm(request.POST, telefone_readonly=telefone_readonly)
        
        if form.is_valid():
            try:
                celebracao = form.save(commit=False)
                
                # Formatar telefone antes de salvar (especialmente se veio do chatbot)
                # IMPORTANTE: Formatar ANTES de salvar para garantir formato consistente
                if celebracao.CEL_telefone:
                    # O form pode ter limpo o telefone, então formatamos novamente
                    celebracao.CEL_telefone = formatar_telefone_para_salvar(celebracao.CEL_telefone)
                
                celebracao.save()
                
                messages.success(
                    request, 
                    f'Celebração agendada com sucesso! {celebracao.CEL_nome_solicitante}, '
                    f'seu agendamento para {celebracao.get_CEL_tipo_celebracao_display()} '
                    f'no dia {celebracao.CEL_data_celebracao.strftime("%d/%m/%Y")} às {celebracao.CEL_horario.strftime("%H:%M")} '
                    f'foi registrado. Em breve entraremos em contato para confirmar.'
                )
                
                # Se estiver no modo app, redirecionar para a home do app
                if request.GET.get('modo') == 'app' or request.session.get('modo_app'):
                    return redirect('app_igreja:app_servicos')

                # Se veio do chatbot (com telefone na URL), redirecionar para home
                if telefone_url:
                    return redirect('home')
                
                # Se não veio do chatbot, permanecer na mesma página para permitir novo agendamento
                # Criar novo formulário limpo, mantendo o telefone se vier da URL
                initial_data = {}
                if telefone_url:
                    telefone_formatado = formatar_telefone_para_salvar(telefone_url)
                    initial_data['CEL_telefone'] = telefone_formatado
                
                form = CelebracaoAgendadaPubForm(initial=initial_data, telefone_readonly=telefone_readonly, telefone_initial=initial_data.get('CEL_telefone'))
                
            except Exception as e:
                logger.error(f"Erro ao agendar celebração: {str(e)}")
                messages.error(request, f'Erro ao agendar celebração: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        # Pré-preencher telefone se vier da URL
        initial_data = {}
        if telefone_url:
            telefone_formatado = formatar_telefone_para_salvar(telefone_url)
            initial_data['CEL_telefone'] = telefone_formatado
            
            # Debug: logar o telefone formatado
            logger.info(f"📞 Telefone formatado para o form: {telefone_formatado}")
        
        form = CelebracaoAgendadaPubForm(initial=initial_data, telefone_readonly=telefone_readonly, telefone_initial=initial_data.get('CEL_telefone'))
    
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
    
    # Determinar URL de retorno baseada no modo
    from django.urls import reverse
    if request.GET.get('modo') == 'app' or request.session.get('modo_app'):
        url_retorno = reverse('app_igreja:app_servicos')
    else:
        url_retorno = reverse('home')

    context = {
        'form': form,
        'paroquia': paroquia,
        'telefone_readonly': telefone_readonly,
        'telefone_url': telefone_url,
        'celebracaoes_agendadas': celebracaoes_agendadas,
        'url_retorno': url_retorno,
    }
    
    return render(request, 'area_publica/bot_agendar_celebracao_publico.html', context)


def list_celebracoes_agendadas_pub(request):
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
            # Formatar telefone para busca (pode estar formatado no banco)
            telefone_formatado = formatar_telefone_para_salvar(telefone_limpo)
            
            # Buscar por telefone de várias formas para garantir que encontre
            # 1. Busca pelos últimos 9 dígitos (sem DDD) - mais flexível
            ultimos_9_digitos = telefone_limpo[-9:] if len(telefone_limpo) >= 9 else telefone_limpo
            # 2. Busca pelos últimos 8 dígitos (sem DDD e sem 9 inicial) - para celular
            ultimos_8_digitos = telefone_limpo[-8:] if len(telefone_limpo) >= 8 else telefone_limpo
            
            # Buscar por telefone (tanto formatado quanto não formatado)
            celebracaoes = TBCELEBRACOES.objects.filter(
                Q(CEL_telefone__icontains=telefone_limpo) |  # Busca pelo telefone limpo completo
                Q(CEL_telefone__icontains=telefone_formatado) |  # Busca pelo telefone formatado
                Q(CEL_telefone__icontains=ultimos_9_digitos) |  # Busca pelos últimos 9 dígitos
                Q(CEL_telefone__icontains=ultimos_8_digitos)  # Busca pelos últimos 8 dígitos
            ).order_by('-CEL_data_celebracao', 'CEL_horario')
            
            resultados_encontrados = celebracaoes.exists()
            
            # Log para debug
            logger.info(f"🔍 Busca de celebrações - Telefone: {telefone}, Limpo: {telefone_limpo}, Formatado: {telefone_formatado}, Encontrados: {celebracaoes.count()}")
            
            if not resultados_encontrados:
                messages.info(request, f'Nenhuma celebração encontrada para o telefone {telefone}')
        else:
            messages.warning(request, 'Digite um telefone válido com pelo menos 10 dígitos')
    
    # Determinar URL de retorno baseada no modo
    from django.urls import reverse
    if request.GET.get('modo') == 'app' or request.session.get('modo_app'):
        url_retorno = reverse('app_igreja:app_servicos')
    else:
        url_retorno = reverse('home')

    context = {
        'paroquia': paroquia,
        'telefone': telefone,
        'celebracaoes': celebracaoes,
        'resultados_encontrados': resultados_encontrados,
        'total_encontrado': celebracaoes.count() if celebracaoes else 0,
        'url_retorno': url_retorno,
    }
    
    return render(request, 'area_publica/tpl_celebracoes_agendadas_pub.html', context)


def detalhe_celebracoes_agendadas_pub(request, celebracao_id):
    """
    Redireciona para a listagem de celebrações agendadas (sem página de detalhe).
    """
    return redirect('app_igreja:celebracoes_agendadas_pub')

