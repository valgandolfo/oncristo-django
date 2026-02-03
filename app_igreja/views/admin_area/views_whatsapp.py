"""
==================== VIEWS DE WHATSAPP ====================
Arquivo com views específicas para envio de mensagens WhatsApp
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime, date
from django.core.paginator import Paginator

from ...models.area_admin.models_whatsapp import TBWHATSAPP
from ...models.area_admin.models_dizimistas import TBDIZIMISTAS
from ...models.area_admin.models_colaboradores import TBCOLABORADORES
from ...models.area_admin.models_grupos import TBGRUPOS
from ...forms.area_admin.forms_whatsapp import MensagemWhatsAppForm
# from ...views.area_publica.views_whatsapp_api import send_whatsapp_message, send_whatsapp_image
import logging

logger = logging.getLogger(__name__)


def admin_required(view_func):
    """Decorator para verificar se o usuário é admin"""
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, 'Você não tem permissão para acessar esta página.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_required
@admin_required
def whatsapp_enviar_mensagem(request):
    """Enviar mensagem WhatsApp - Versão simplificada com abas"""
    
    # Verificar se é edição
    editar_id = request.GET.get('editar')
    mensagem_editando = None
    if editar_id:
        try:
            mensagem_editando = get_object_or_404(TBWHATSAPP, pk=editar_id)
            # Só permitir editar se o status for ERRO
            if mensagem_editando.WHA_status != 'ERRO':
                messages.warning(request, 'Apenas mensagens com erro podem ser editadas.')
                return redirect('app_igreja:whatsapp_list')
        except:
            messages.error(request, 'Mensagem não encontrada.')
            return redirect('app_igreja:whatsapp_list')
    
    # Definir modo para usar o template PAI
    modo_detalhe = True
    modo_criacao = not bool(editar_id)
    modo_edicao_crud = bool(editar_id)
    acao = 'editar' if editar_id else 'incluir'
    
    if request.method == 'POST':
        form = MensagemWhatsAppForm(request.POST, request.FILES)
        if form.is_valid():
            # Extrair dados do formulário
            texto = form.cleaned_data.get('texto', '')
            tipo_destinatario = form.cleaned_data['tipo_destinatario']
            tipo_midia = form.cleaned_data['tipo_midia']
            
            # Extrair dados específicos
            dizimista_especifico = form.cleaned_data.get('dizimista_especifico')
            colaborador_especifico = form.cleaned_data.get('colaborador_especifico')
            
            # Extrair filtros
            filtrar_dizimista = form.cleaned_data.get('filtrar_dizimista')
            filtrar_colaborador = form.cleaned_data.get('filtrar_colaborador')
            grupo_colaborador = form.cleaned_data.get('grupo_colaborador')
            
            # Extrair dados de mídia
            url_imagem = form.cleaned_data.get('url_imagem', '')
            arquivo_imagem = form.cleaned_data.get('arquivo_imagem')
            legenda_imagem = form.cleaned_data.get('legenda_imagem', '')
            url_audio = form.cleaned_data.get('url_audio', '')
            arquivo_audio = form.cleaned_data.get('arquivo_audio')
            url_video = form.cleaned_data.get('url_video', '')
            arquivo_video = form.cleaned_data.get('arquivo_video')
            legenda_video = form.cleaned_data.get('legenda_video', '')
            
            # Determinar destinatários
            destinatarios = []
            
            if tipo_destinatario == 'DIZIMISTAS':
                if dizimista_especifico:
                    if dizimista_especifico.DIS_telefone:
                        destinatarios = [{
                            'nome': dizimista_especifico.DIS_nome,
                            'telefone': dizimista_especifico.DIS_telefone
                        }]
                else:
                    destinatarios = obter_destinatarios_dizimistas(
                        filtrar_dizimista=filtrar_dizimista,
                        data_inicial=form.cleaned_data.get('data_nascimento_dizimista_inicio'),
                        data_final=form.cleaned_data.get('data_nascimento_dizimista_fim')
                    )
                    
            elif tipo_destinatario == 'COLABORADORES':
                if colaborador_especifico:
                    if colaborador_especifico.COL_telefone:
                        destinatarios = [{
                            'nome': colaborador_especifico.COL_nome_completo,
                            'telefone': colaborador_especifico.COL_telefone
                        }]
                else:
                    destinatarios = obter_destinatarios_colaboradores(
                        filtrar_colaborador=filtrar_colaborador,
                        grupo_colaborador=grupo_colaborador,
                        data_inicial=form.cleaned_data.get('data_nascimento_colaborador_inicio'),
                        data_final=form.cleaned_data.get('data_nascimento_colaborador_fim')
                    )
            
            elif tipo_destinatario == 'TODOS':
                # Combinar dizimistas e colaboradores
                dizimistas = obter_destinatarios_dizimistas()
                colaboradores = obter_destinatarios_colaboradores()
                
                telefones_existentes = {d['telefone'] for d in dizimistas}
                for colab in colaboradores:
                    if colab['telefone'] not in telefones_existentes:
                        dizimistas.append(colab)
                        telefones_existentes.add(colab['telefone'])
                
                destinatarios = dizimistas
            
            if not destinatarios:
                messages.error(request, 'Nenhum destinatário encontrado com os critérios especificados.')
                # Carregar listagem apenas se não estiver em modo de criar/editar
                if acao != 'incluir' and acao != 'editar':
                    mensagens = TBWHATSAPP.objects.all().order_by('-WHA_data_criacao')[:20]
                    paginator = Paginator(mensagens, 20)
                    page_obj = paginator.get_page(1)
                else:
                    page_obj = None
                return render(request, 'admin_area/tpl_mensagens_whatapp.html', {
                    'form': form,
                    'modo_detalhe': modo_detalhe,
                    'modo_criacao': modo_criacao,
                    'modo_edicao_crud': modo_edicao_crud,
                    'acao': acao,
                    'page_obj': page_obj,
                    'modo_dashboard': acao != 'incluir' and acao != 'editar',
                    'mensagem': mensagem_editando,
                })
            
            # Processar uploads de arquivos se necessário
            url_final_imagem = url_imagem
            url_final_audio = url_audio
            url_final_video = url_video
            
            # TODO: Implementar upload de arquivos quando necessário
            
            # ENVIAR MENSAGENS PRIMEIRO (antes de salvar no banco)
            sucessos = 0
            erros = 0
            erros_detalhes = []
            
            for destinatario in destinatarios:
                try:
                    telefone = limpar_telefone_para_envio(destinatario.get('telefone'))
                    nome = destinatario.get('nome', 'Destinatário')
                    
                    if not telefone:
                        erros += 1
                        erros_detalhes.append(f"{nome}: Telefone inválido")
                        continue
                    
                    # Montar mensagem com texto
                    mensagem_texto = texto
                    if tipo_midia == 'TEXTO':
                        # Enviar mensagem de texto
                        resultado = send_whatsapp_message(telefone, mensagem_texto)
                        if resultado.get("error"):
                            erros += 1
                            erros_detalhes.append(f"{nome}: {resultado.get('error')}")
                            logger.error(f"Erro ao enviar mensagem para {nome} ({telefone}): {resultado.get('error')}")
                        else:
                            sucessos += 1
                            logger.info(f"Mensagem enviada com sucesso para {nome} ({telefone})")
                    
                    elif tipo_midia == 'IMAGEM':
                        # Enviar imagem
                        if url_final_imagem:
                            resultado = send_whatsapp_image(telefone, url_final_imagem, legenda_imagem or mensagem_texto)
                            if resultado.get("error"):
                                erros += 1
                                erros_detalhes.append(f"{nome}: {resultado.get('error')}")
                                logger.error(f"Erro ao enviar imagem para {nome} ({telefone}): {resultado.get('error')}")
                            else:
                                sucessos += 1
                                logger.info(f"Imagem enviada com sucesso para {nome} ({telefone})")
                        else:
                            erros += 1
                            erros_detalhes.append(f"{nome}: URL da imagem não fornecida")
                    
                    elif tipo_midia == 'AUDIO':
                        # TODO: Implementar envio de áudio
                        erros += 1
                        erros_detalhes.append(f"{nome}: Envio de áudio ainda não implementado")
                    
                    elif tipo_midia == 'VIDEO':
                        # TODO: Implementar envio de vídeo
                        erros += 1
                        erros_detalhes.append(f"{nome}: Envio de vídeo ainda não implementado")
                    
                    else:
                        # Tipo não suportado, enviar como texto
                        resultado = send_whatsapp_message(telefone, mensagem_texto)
                        if resultado.get("error"):
                            erros += 1
                            erros_detalhes.append(f"{nome}: {resultado.get('error')}")
                        else:
                            sucessos += 1
                    
                    # Pequeno delay entre envios para não sobrecarregar a API
                    import time
                    time.sleep(0.5)
                    
                except Exception as e:
                    erros += 1
                    nome = destinatario.get('nome', 'Destinatário')
                    erros_detalhes.append(f"{nome}: {str(e)}")
                    logger.error(f"Erro ao processar destinatário {nome}: {str(e)}", exc_info=True)
            
            # SALVAR NO BANCO APENAS DEPOIS DE ENVIAR
            if editar_id and mensagem_editando:
                # Atualizar mensagem existente
                mensagem_editando.WHA_texto = texto
                mensagem_editando.WHA_destinatario_tipo = tipo_destinatario
                mensagem_editando.WHA_tipo_midia = tipo_midia
                mensagem_editando.WHA_url_imagem = url_imagem
                mensagem_editando.WHA_legenda_imagem = legenda_imagem
                mensagem_editando.WHA_url_audio = url_audio
                mensagem_editando.WHA_url_video = url_video
                mensagem_editando.WHA_legenda_video = legenda_video
                mensagem_editando.WHA_total_enviadas = len(destinatarios)
                mensagem_editando.WHA_sucessos = sucessos
                mensagem_editando.WHA_erros = erros
                mensagem_editando.WHA_usuario = request.user
                mensagem_editando.WHA_status = 'ENVIADA' if sucessos > 0 else 'ERRO'
                mensagem_editando.save()
                mensagem = mensagem_editando
            else:
                # Criar nova mensagem
                mensagem = TBWHATSAPP.objects.create(
                    WHA_texto=texto,
                    WHA_destinatario_tipo=tipo_destinatario,
                    WHA_tipo_midia=tipo_midia,
                    WHA_url_imagem=url_imagem,
                    WHA_legenda_imagem=legenda_imagem,
                    WHA_url_audio=url_audio,
                    WHA_url_video=url_video,
                    WHA_legenda_video=legenda_video,
                    WHA_total_enviadas=len(destinatarios),
                    WHA_sucessos=sucessos,
                    WHA_erros=erros,
                    WHA_usuario=request.user,
                    WHA_status='ENVIADA' if sucessos > 0 else 'ERRO'
                )
            
            if sucessos > 0:
                messages.success(request, f'Mensagem enviada com sucesso para {sucessos} destinatário(s)!')
            if erros > 0:
                mensagem_erro = f'Erro ao enviar para {erros} destinatário(s).'
                if erros_detalhes:
                    mensagem_erro += f' Detalhes: {"; ".join(erros_detalhes[:5])}'  # Mostrar apenas os 5 primeiros erros
                    if len(erros_detalhes) > 5:
                        mensagem_erro += f'... e mais {len(erros_detalhes) - 5} erro(s).'
                messages.warning(request, mensagem_erro)
            
            return redirect('app_igreja:whatsapp_list')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
            # Carregar listagem apenas se não estiver em modo de criar/editar
            if acao != 'incluir' and acao != 'editar':
                mensagens = TBWHATSAPP.objects.all().order_by('-WHA_data_criacao')
                paginator = Paginator(mensagens, 20)
                page_number = request.GET.get('page', 1)
                page_obj = paginator.get_page(page_number)
            else:
                page_obj = None
            return render(request, 'admin_area/tpl_mensagens_whatapp.html', {
                'form': form,
                'modo_detalhe': modo_detalhe,
                'modo_criacao': modo_criacao,
                'modo_edicao_crud': modo_edicao_crud,
                'acao': acao,
                'model_verbose_name': 'Mensagem WhatsApp',
                'mensagem': mensagem_editando,
                'page_obj': page_obj,
                'modo_dashboard': acao != 'incluir' and acao != 'editar',
            })
    else:
        # Se for edição, preencher o form com os dados existentes
        if mensagem_editando:
            initial_data = {
                'texto': mensagem_editando.WHA_texto,
                'tipo_destinatario': mensagem_editando.WHA_destinatario_tipo,
                'tipo_midia': mensagem_editando.WHA_tipo_midia,
                'url_imagem': mensagem_editando.WHA_url_imagem,
                'legenda_imagem': mensagem_editando.WHA_legenda_imagem,
                'url_audio': mensagem_editando.WHA_url_audio,
                'url_video': mensagem_editando.WHA_url_video,
                'legenda_video': mensagem_editando.WHA_legenda_video,
            }
            form = MensagemWhatsAppForm(initial=initial_data)
        else:
            form = MensagemWhatsAppForm()
    
    # Carregar listagem apenas se não estiver em modo de criar/editar
    if acao != 'incluir' and acao != 'editar':
        mensagens = TBWHATSAPP.objects.all().order_by('-WHA_data_criacao')
        paginator = Paginator(mensagens, 20)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = None
    
    return render(request, 'admin_area/tpl_mensagens_whatapp.html', {
        'form': form,
        'modo_detalhe': modo_detalhe,
        'modo_criacao': modo_criacao,
        'modo_edicao_crud': modo_edicao_crud,
        'acao': acao,
        'model_verbose_name': 'Mensagem WhatsApp',
        'mensagem': mensagem_editando,
        'page_obj': page_obj,
        'modo_dashboard': acao != 'incluir' and acao != 'editar',
    })


@login_required
@admin_required
def whatsapp_list(request):
    """Lista de mensagens enviadas usando formulário PAI"""
    from datetime import datetime
    
    # Filtros
    status_filter = request.GET.get('status', '').strip()
    tipo_filter = request.GET.get('tipo_destinatario', '').strip()
    data_inicio = request.GET.get('data_inicio', '').strip()
    data_fim = request.GET.get('data_fim', '').strip()
    
    # Controla se o usuário já executou uma busca (preencheu algum filtro ou navegou na paginação)
    busca_realizada = bool(status_filter or tipo_filter or data_inicio or data_fim or request.GET.get('page'))
    
    # Só carrega os registros no grid DEPOIS que o usuário aplicar um filtro
    if busca_realizada:
        mensagens = TBWHATSAPP.objects.all().order_by('-WHA_data_criacao')
        
        if status_filter:
            mensagens = mensagens.filter(WHA_status=status_filter)
        
        if tipo_filter:
            mensagens = mensagens.filter(WHA_destinatario_tipo=tipo_filter)
        
        # Filtro por data
        if data_inicio:
            try:
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                mensagens = mensagens.filter(WHA_data_criacao__date__gte=data_inicio_obj)
            except ValueError:
                pass
        
        if data_fim:
            try:
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
                mensagens = mensagens.filter(WHA_data_criacao__date__lte=data_fim_obj)
            except ValueError:
                pass
        
        # Ordenação
        mensagens = mensagens.order_by('-WHA_data_criacao')
    else:
        # Queryset vazio até que o usuário faça a primeira busca
        mensagens = TBWHATSAPP.objects.none()
    
    # Paginação
    paginator = Paginator(mensagens, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'tipo_filter': tipo_filter,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'modo_dashboard': True,
        'busca_realizada': busca_realizada,
    }
    
    return render(request, 'admin_area/tpl_mensagens_whatapp.html', context)


@login_required
@admin_required
def whatsapp_detail(request, pk):
    """Detalhes de uma mensagem"""
    mensagem = get_object_or_404(TBWHATSAPP, pk=pk)
    
    context = {
        'mensagem': mensagem,
        'acao': 'consultar',
        'modo_visualizacao_crud': True,
        'modo_detalhe': True,
        'modo_dashboard': False,
        'model_verbose_name': 'Mensagem WhatsApp',
    }
    
    return render(request, 'admin_area/tpl_mensagens_whatapp.html', context)


@login_required
@admin_required
def whatsapp_excluir(request, pk):
    """Excluir uma mensagem"""
    mensagem = get_object_or_404(TBWHATSAPP, pk=pk)
    
    if request.method == 'POST':
        mensagem.delete()
        messages.success(request, 'Mensagem excluída com sucesso!')
        return redirect('app_igreja:whatsapp_list')
    
    context = {
        'mensagem': mensagem,
        'acao': 'excluir',
        'modo_detalhe': True,
        'modo_dashboard': False,
        'model_verbose_name': 'Mensagem WhatsApp',
    }
    
    return render(request, 'admin_area/tpl_mensagens_whatapp.html', context)


@login_required
@admin_required
def whatsapp_debug(request):
    """Página de debug para WhatsApp"""
    from django.conf import settings
    
    # Configurações da API (simuladas)
    api_key = getattr(settings, 'WHAPI_KEY', 'Não configurado')
    channel_id = getattr(settings, 'CHANNEL_ID', 'Não configurado')
    api_base_url = getattr(settings, 'API_BASE_URL', 'Não configurado')
    
    # Status da conta (simulado)
    conta_status = {
        'tipo': 'Desenvolvedor Premium',
        'status': 'Ativa',
        'dias_restantes': 287,
        'validade': '13.05.2026',
        'problema': 'Número WhatsApp bloqueado (ambiente local)'
    }
    
    # Últimas mensagens
    mensagens = TBWHATSAPP.objects.all().order_by('-WHA_data_criacao')[:10]
    
    # Logs de erro atualizados
    logs_erro = [
        {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error_type': 'Ambiente Local',
            'details': 'Localmente não é possível enviar mensagens pelo WhatsApp. Configure a API em produção.'
        },
    ]
    
    context = {
        'api_key': api_key,
        'api_base_url': api_base_url,
        'channel_id': channel_id,
        'conta_status': conta_status,
        'mensagens': mensagens,
        'logs_erro': logs_erro,
        'whatsapp_section': 'debug'
    }
    
    return render(request, 'admin_area/tpl_mensagens_whatapp.html', context)


# Funções auxiliares

def obter_destinatarios_dizimistas(filtrar_dizimista=None, data_inicial=None, data_final=None):
    """Obtém lista de dizimistas baseado nos filtros fornecidos"""
    queryset = TBDIZIMISTAS.objects.all()
    
    if filtrar_dizimista:
        if filtrar_dizimista == 'ATIVO':
            queryset = queryset.filter(DIS_status=True)
        elif filtrar_dizimista == 'INATIVO':
            queryset = queryset.filter(DIS_status=False)
    
    if data_inicial and data_final:
        # Filtrar por período de aniversário
        queryset = queryset.filter(
            Q(DIS_data_nascimento__month__gte=data_inicial.month, DIS_data_nascimento__day__gte=data_inicial.day) |
            Q(DIS_data_nascimento__month__lte=data_final.month, DIS_data_nascimento__day__lte=data_final.day)
        )
    
    destinatarios = []
    for dizimista in queryset:
        if dizimista.DIS_telefone:
            destinatarios.append({
                'nome': dizimista.DIS_nome,
                'telefone': dizimista.DIS_telefone
            })
    
    return destinatarios


def obter_destinatarios_colaboradores(filtrar_colaborador=None, grupo_colaborador=None, data_inicial=None, data_final=None):
    """Obtém lista de colaboradores baseado nos filtros fornecidos"""
    queryset = TBCOLABORADORES.objects.all()
    
    if filtrar_colaborador:
        if filtrar_colaborador == 'ATIVO':
            queryset = queryset.filter(COL_status='ATIVO')
        elif filtrar_colaborador == 'INATIVO':
            queryset = queryset.filter(COL_status='INATIVO')
        elif filtrar_colaborador == 'PENDENTE':
            queryset = queryset.filter(COL_status='PENDENTE')
    
    if grupo_colaborador:
        # Filtrar por grupo específico (se houver relação)
        # Por enquanto, não há relação direta, então pulamos
        pass
    
    if data_inicial and data_final:
        # Filtrar por período de aniversário
        queryset = queryset.filter(
            Q(COL_data_nascimento__month__gte=data_inicial.month, COL_data_nascimento__day__gte=data_inicial.day) |
            Q(COL_data_nascimento__month__lte=data_final.month, COL_data_nascimento__day__lte=data_final.day)
        )
    
    destinatarios = []
    for colaborador in queryset:
        if colaborador.COL_telefone:
            destinatarios.append({
                'nome': colaborador.COL_nome_completo,
                'telefone': colaborador.COL_telefone
            })
    
    return destinatarios


def limpar_telefone_para_envio(telefone):
    """Formata telefone para o formato da API"""
    if not telefone:
        return None
    
    # Remove caracteres não numéricos
    telefone_limpo = ''.join(filter(str.isdigit, str(telefone)))
    
    # Adiciona código do país se não tiver
    if len(telefone_limpo) == 11 and telefone_limpo.startswith('0'):
        telefone_limpo = '55' + telefone_limpo[1:]
    elif len(telefone_limpo) == 10:
        telefone_limpo = '55' + telefone_limpo
    elif len(telefone_limpo) == 11:
        telefone_limpo = '55' + telefone_limpo
    
    return telefone_limpo

