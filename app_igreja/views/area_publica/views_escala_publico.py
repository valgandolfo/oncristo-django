"""
==================== VIEWS PÚBLICAS DE ESCALA ====================
Views para visualização e atribuição de colaboradores nas escalas de missas
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from datetime import date, datetime
import logging

from ...models.area_admin.models_escala import TBESCALA, TBITEM_ESCALA
from ...models.area_admin.models_colaboradores import TBCOLABORADORES

logger = logging.getLogger(__name__)


def limpar_telefone(telefone):
    """Remove caracteres não numéricos do telefone"""
    if not telefone:
        return None
    import re
    return re.sub(r'[^\d]', '', str(telefone))


def escala_publico(request):
    """
    View pública para visualizar escalas de missas
    Permite que colaboradores vejam e se inscrevam em encargos
    """
    # Buscar mês/ano da query string
    mes = request.GET.get('mes', '')
    ano = request.GET.get('ano', '')
    
    # Se não tiver mês/ano, usar mês e ano atual como padrão
    hoje = date.today()
    mes_atual = int(mes) if mes else hoje.month
    ano_atual = int(ano) if ano else hoje.year
    
    # Verificar se veio telefone via URL (do WhatsApp)
    telefone_url = request.GET.get('telefone', '').strip()
    colaborador_logado = None
    colaborador_nome = None
    
    if telefone_url:
        telefone_limpo = limpar_telefone(telefone_url)
        # Remover código do país se existir
        if telefone_limpo and telefone_limpo.startswith('55'):
            telefone_limpo = telefone_limpo[2:]
        
        # Buscar colaborador pelo telefone
        # O telefone no banco pode estar formatado como (18) 99736-6866
        # Precisamos buscar comparando apenas os números
        colaborador_logado = None
        colaborador_nome = None
        
        # Buscar todos os colaboradores e comparar telefones limpos
        todos_colaboradores = TBCOLABORADORES.objects.all()
        
        for colab in todos_colaboradores:
            if colab.COL_telefone:
                # Limpar telefone do banco (remover formatação e 55)
                telefone_banco_limpo = limpar_telefone(colab.COL_telefone)
                if telefone_banco_limpo and telefone_banco_limpo.startswith('55'):
                    telefone_banco_limpo = telefone_banco_limpo[2:]
                
                # Comparar apenas os números
                if telefone_banco_limpo == telefone_limpo:
                    colaborador_logado = colab
                    colaborador_nome = colab.COL_nome_completo
                    logger.info(f"✅ Colaborador logado encontrado: {colaborador_nome} (telefone: {colab.COL_telefone})")
                    break
    
    # Validar mês e ano
    if mes_atual < 1 or mes_atual > 12:
        mes_atual = hoje.month
    if ano_atual < 2000 or ano_atual > 2100:
        ano_atual = hoje.year
    
    # Buscar escala master
    primeiro_dia_mes = date(ano_atual, mes_atual, 1)
    escala_master = TBESCALA.objects.filter(ESC_MESANO=primeiro_dia_mes).first()
    
    itens = []
    if escala_master:
        # Buscar itens da escala
        itens = TBITEM_ESCALA.objects.filter(
            ITE_ESC_ESCALA=escala_master
        ).order_by('ITE_ESC_DATA', 'ITE_ESC_HORARIO')
        
        # Organizar por dia para exibição
        dias_semana_pt = {
            0: 'Segunda-feira',
            1: 'Terça-feira',
            2: 'Quarta-feira',
            3: 'Quinta-feira',
            4: 'Sexta-feira',
            5: 'Sábado',
            6: 'Domingo'
        }
        
        meses_pt = [
            '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        
        # Adicionar informações para cada item
        for item in itens:
            item.dia_semana_nome = dias_semana_pt.get(item.ITE_ESC_DATA.weekday(), '')
            item.dia_semana_abrev = item.dia_semana_nome[:3].upper() if item.dia_semana_nome else ''
            
            # Adicionar informação de bloqueio (ITE_ESC_SITUACAO = False significa bloqueado)
            item.bloqueado = not item.ITE_ESC_SITUACAO
            
            # Buscar nome do colaborador (apelido/primeiro nome)
            if item.ITE_ESC_COLABORADOR:
                try:
                    colaborador = TBCOLABORADORES.objects.get(COL_id=item.ITE_ESC_COLABORADOR)
                    # Pegar primeiro nome como apelido
                    item.colaborador_apelido = colaborador.COL_nome_completo.split()[0] if colaborador.COL_nome_completo else '-'
                    item.colaborador_id = colaborador.COL_id
                except TBCOLABORADORES.DoesNotExist:
                    item.colaborador_apelido = '-'
                    item.colaborador_id = None
            else:
                item.colaborador_apelido = None
                item.colaborador_id = None
    
    meses_pt = [
        '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    
    # Determinar URL de retorno baseada no modo
    from django.urls import reverse
    if request.GET.get('modo') == 'app' or request.session.get('modo_app'):
        url_retorno = reverse('app_igreja:app_info')
    else:
        url_retorno = reverse('home')

    context = {
        'itens': itens,
        'mes': mes_atual,
        'ano': ano_atual,
        'mes_nome': meses_pt[mes_atual] if mes_atual > 0 else '',
        'escala_master': escala_master,
        'colaborador_logado': colaborador_logado,
        'colaborador_nome': colaborador_nome,
        'telefone_url': telefone_url,
        'url_retorno': url_retorno,
    }
    
    return render(request, 'area_publica/bot_escala_publico.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def atribuir_colaborador_escala(request):
    """
    API para atribuir colaborador a um item da escala
    """
    try:
        item_id = request.POST.get('item_id')
        telefone = request.POST.get('telefone', '').strip()
        
        if not item_id:
            return JsonResponse({
                'sucesso': False,
                'mensagem': 'Item da escala não informado.'
            }, status=400)
        
        if not telefone:
            return JsonResponse({
                'sucesso': False,
                'mensagem': 'Telefone não informado.'
            }, status=400)
        
        # Limpar telefone - remover caracteres não numéricos
        telefone_limpo = limpar_telefone(telefone)
        
        # Remover código do país (55) se existir
        if telefone_limpo and telefone_limpo.startswith('55'):
            telefone_limpo = telefone_limpo[2:]
        
        logger.info(f"🔍 Buscando colaborador com telefone limpo: {telefone_limpo}")
        
        # Buscar colaborador pelo telefone
        # O telefone no banco pode estar formatado como (18) 99736-6866
        # Precisamos buscar comparando apenas os números
        
        colaborador = None
        
        # Buscar todos os colaboradores e comparar telefones limpos
        todos_colaboradores = TBCOLABORADORES.objects.all()
        
        for colab in todos_colaboradores:
            if colab.COL_telefone:
                # Limpar telefone do banco (remover formatação e 55)
                telefone_banco_limpo = limpar_telefone(colab.COL_telefone)
                if telefone_banco_limpo and telefone_banco_limpo.startswith('55'):
                    telefone_banco_limpo = telefone_banco_limpo[2:]
                
                # Comparar apenas os números
                if telefone_banco_limpo == telefone_limpo:
                    colaborador = colab
                    logger.info(f"✅ Colaborador encontrado: {colaborador.COL_nome_completo} (telefone banco: {colab.COL_telefone}, limpo: {telefone_banco_limpo})")
                    break
        
        if not colaborador:
            logger.error(f"❌ Colaborador não encontrado com telefone: {telefone_limpo}")
            # Log de todos os telefones no banco para debug
            logger.debug("Telefones no banco:")
            for colab in TBCOLABORADORES.objects.all()[:5]:  # Primeiros 5 para debug
                if colab.COL_telefone:
                    tel_limpo = limpar_telefone(colab.COL_telefone)
                    if tel_limpo and tel_limpo.startswith('55'):
                        tel_limpo = tel_limpo[2:]
                    logger.debug(f"  - {colab.COL_telefone} -> limpo: {tel_limpo}")
            
            return JsonResponse({
                'sucesso': False,
                'mensagem': f'Colaborador não encontrado com o telefone informado. Por favor, cadastre-se primeiro. Telefone buscado: {telefone_limpo}'
            }, status=404)
        
        # Buscar item da escala
        try:
            item = TBITEM_ESCALA.objects.get(ITE_ESC_ID=item_id)
        except TBITEM_ESCALA.DoesNotExist:
            return JsonResponse({
                'sucesso': False,
                'mensagem': 'Item da escala não encontrado.'
            }, status=404)
        
        # Verificar se o item está bloqueado
        if not item.ITE_ESC_SITUACAO:
            return JsonResponse({
                'sucesso': False,
                'mensagem': 'Este período está bloqueado e não permite atribuições.'
            }, status=400)
        
        # Verificar se já tem colaborador atribuído
        if item.ITE_ESC_COLABORADOR:
            return JsonResponse({
                'sucesso': False,
                'mensagem': 'Este encargo já está atribuído a outro colaborador.'
            }, status=400)
        
        # Atribuir colaborador e função (preserva histórico)
        item.ITE_ESC_COLABORADOR = colaborador.COL_id
        item.ITE_ESC_FUNCAO = colaborador.COL_funcao  # Grava a função no momento da atribuição
        item.ITE_ESC_STATUS = 'RESERVADO'
        item.save()
        
        logger.info(f"✅ Colaborador {colaborador.COL_nome_completo} atribuído ao item {item_id}")
        
        return JsonResponse({
            'sucesso': True,
            'mensagem': 'Aguarde nossa equipe entrar em contato ou consulte pelo site.',
            'colaborador_nome': colaborador.COL_nome_completo.split()[0] if colaborador.COL_nome_completo else 'Colaborador'
        })
        
    except Exception as e:
        logger.error(f"Erro ao atribuir colaborador: {str(e)}")
        return JsonResponse({
            'sucesso': False,
            'mensagem': f'Erro ao atribuir colaborador: {str(e)}'
        }, status=500)

