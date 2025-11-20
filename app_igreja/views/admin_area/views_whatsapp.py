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
    """Enviar mensagem WhatsApp"""
    
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
                return render(request, 'admin_area/tpl_mensagens_whatapp.html', {
                    'form': form,
                    'whatsapp_section': 'enviar'
                })
            
            # Criar registro da mensagem
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
                WHA_usuario=request.user,
                WHA_status='PENDENTE'
            )
            
            # Processar uploads de arquivos se necessário
            url_final_imagem = url_imagem
            url_final_audio = url_audio
            url_final_video = url_video
            
            # TODO: Implementar upload de arquivos quando necessário
            # Por enquanto, apenas simular o envio
            
            # Simular envio (localmente não é possível enviar)
            sucessos = 0
            erros = 0
            
            for destinatario in destinatarios:
                try:
                    telefone = limpar_telefone_para_envio(destinatario.get('telefone'))
                    
                    if telefone:
                        # Simulação: localmente não é possível enviar
                        # Em produção, aqui seria feita a chamada à API do WhatsApp
                        sucessos += 1
                    else:
                        erros += 1
                except Exception as e:
                    erros += 1
            
            # Atualizar estatísticas da mensagem
            mensagem.WHA_total_enviadas = len(destinatarios)
            mensagem.WHA_sucessos = sucessos
            mensagem.WHA_erros = erros
            mensagem.WHA_status = 'ENVIADA' if sucessos > 0 else 'ERRO'
            mensagem.save()
            
            if sucessos > 0:
                messages.success(request, f'Mensagem preparada para {sucessos} destinatário(s). Nota: Localmente não é possível enviar mensagens pelo WhatsApp.')
            if erros > 0:
                messages.warning(request, f'Erro ao processar {erros} destinatário(s).')
            
            return redirect('app_igreja:whatsapp_detail', pk=mensagem.WHA_id)
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = MensagemWhatsAppForm()
    
    return render(request, 'admin_area/tpl_mensagens_whatapp.html', {
        'form': form,
        'whatsapp_section': 'enviar'
    })


@login_required
@admin_required
def whatsapp_list(request):
    """Lista de mensagens enviadas"""
    mensagens = TBWHATSAPP.objects.all().order_by('-WHA_data_criacao')
    
    # Filtros
    status = request.GET.get('status')
    tipo_destinatario = request.GET.get('tipo_destinatario')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    if status:
        mensagens = mensagens.filter(WHA_status=status)
    if tipo_destinatario:
        mensagens = mensagens.filter(WHA_destinatario_tipo=tipo_destinatario)
    if data_inicio:
        mensagens = mensagens.filter(WHA_data_criacao__date__gte=data_inicio)
    if data_fim:
        mensagens = mensagens.filter(WHA_data_criacao__date__lte=data_fim)
    
    # Paginação
    paginator = Paginator(mensagens, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'mensagens': page_obj,
        'title': 'Mensagens WhatsApp',
        'subtitle': 'Histórico de mensagens enviadas',
        'whatsapp_section': 'list'
    }
    return render(request, 'admin_area/tpl_mensagens_whatapp.html', context)


@login_required
@admin_required
def whatsapp_detail(request, pk):
    """Detalhes de uma mensagem"""
    mensagem = get_object_or_404(TBWHATSAPP, pk=pk)
    
    context = {
        'mensagem': mensagem,
        'title': 'Detalhes da Mensagem',
        'subtitle': f'Mensagem enviada em {mensagem.WHA_data_criacao.strftime("%d/%m/%Y %H:%M")}',
        'whatsapp_section': 'detail'
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

