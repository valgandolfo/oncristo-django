from django.urls import path
from . import views

# WhatsApp API (webhook + imagem otimizada)
from app_igreja.views.area_publica.views_whatsapp_api import whatsapp_webhook, whatsapp_imagem_principal


# Área Administrativa - Configurações e Dashboards
from .views.admin_area.views_dioceses import diocese_crud_unico
from .views.admin_area.views_paroquias import paroquia_crud_unico
# Área Administrativa - Grupos e Funções
from .views.admin_area.views_grupos import listar_grupos, criar_grupo, editar_grupo, excluir_grupo, detalhar_grupo, dashboard_grupos
from .views.admin_area.views_funcoes import listar_funcoes, criar_funcao, editar_funcao, excluir_funcao, detalhar_funcao, dashboard_funcoes
# Área Administrativa - celebrantes
from .views.admin_area.views_celebrantes import (
    listar_celebrantes, criar_celebrante, editar_celebrante, excluir_celebrante, detalhar_celebrante
)



from .views.admin_area.views_visual import visual_generic_view

from .views.admin_area.views_colaboradores import (
    listar_colaboradores, criar_colaborador, editar_colaborador, excluir_colaborador, detalhar_colaborador
)
from .views.admin_area.views_dizimistas import (
    gerenciar_dizimistas, criar_dizimista, editar_dizimista, excluir_dizimista, detalhar_dizimista, dashboard_dizimistas, api_cep
)

# Área Administrativa - Conteúdo e Comunicação
from .views.admin_area.views_banners import listar_banners, criar_banner, editar_banner, excluir_banner, detalhar_banner
from .views.admin_area.views_celebracoes import listar_celebracoes, criar_celebracao, editar_celebracao, excluir_celebracao, detalhar_celebracao
from .views.admin_area.views_avisos import listar_avisos, criar_aviso, editar_aviso, detalhar_aviso, excluir_aviso
from .views.admin_area.views_liturgias import listar_liturgias, criar_liturgia, editar_liturgia, detalhar_liturgia, excluir_liturgia
from .views.admin_area.views_mural import listar_murais, criar_mural, editar_mural, excluir_mural, detalhar_mural
from .views.admin_area.views_oracoes import (
    listar_oracoes, criar_oracao, editar_oracao, excluir_oracao, detalhar_oracao, 
    dashboard_oracoes, alterar_status_oracao, toggle_ativo_oracao
)


# Área Administrativa - Eventos e Escalas
from .views.admin_area.views_eventos import (
    listar_eventos, criar_evento, editar_evento, excluir_evento, detalhar_evento,
    listar_itens_evento, criar_item_evento, editar_item_evento, excluir_item_evento, detalhar_item_evento
)
from .views.admin_area.views_eventos_master_detail import (
    MasterDetailEventoListView, MasterDetailEventoView, MasterDetailCreateView,
    MasterDetailDeleteView, MasterDetailItensView
)
from .views.admin_area.views_modelos_master_detail import (
    MasterDetailModeloListView, MasterDetailModeloView, MasterDetailModeloCreateView, MasterDetailModeloDeleteView
)
from .views.admin_area.views_escala_mensal_missa import escala_mensal_form, escala_mensal_gerar, escala_mensal_visualizar, escala_mensal_editar_descricao
from .views.admin_area.views_gerenciar_escala import listar_itens_escala, criar_item_escala, detalhar_item_escala, editar_item_escala, excluir_item_escala
from .views.admin_area.views_apontamentos_missas import apontamentos_escala_missa, atribuir_apontamento
from .views.admin_area.views_agenda_mes import agenda_mes, buscar_encargos_modelo

# Área Administrativa - Financeiro e Relatórios
from .views.admin_area.views_gerenciar_dizimo import (
    gerar_mensalidade_dizimo_form, gerar_mensalidade_dizimo, listar_mensalidades_dizimo, 
    gerenciar_coleta_dizimo, baixar_dizimo, cancelar_baixa
)
from .views.admin_area.views_relatorios import relatorio_aniversariantes, relatorio_escala_mensal_missas, relatorio_aniversariantes_pdf, relatorio_escala_mensal_missas_pdf
from .views.admin_area.views_extrator_liturgias import extrator_liturgias, extrator_liturgias_api

# Área Administrativa - WhatsApp (Envio Manual e Debug)
from .views.admin_area.views_whatsapp import whatsapp_enviar_mensagem, whatsapp_list, whatsapp_detail, whatsapp_excluir, whatsapp_debug

# Área Pública
from .views.area_publica.views_liturgias_publico import liturgias_publico
from .views.area_publica.views_contato import contatos_publico
from .views.area_publica.views_cadastro_dizimista_pub import cadastro_dizimista_pub, quero_ser_dizimista, verificar_telefone_cadastro_dizimista_pub
from .views.area_publica.views_oracoes import meus_pedidos_oracoes, detalhar_oracao_publico, criar_pedido_oracao_publico
from .views.area_publica.views_avisos_paroquia_pub import avisos_paroquia_pub
from .views.area_publica.views_calendario_eventos_pub import calendario_eventos_publico, ver_programacao_evento
from .views.area_publica.views_aniversariantes_pub import aniversariantes_publico
from .views.area_publica.views_celebracoes_agendadas_pub import list_celebracoes_agendadas_pub, agendar_celebracoes_agendadas_pub, detalhe_celebracoes_agendadas_pub
from .views.area_publica.views_doacoes import doacoes_publico
from .views.area_publica.views_mural import mural_publico, mural_publico_redirect
from .views.area_publica.views_escala_publico import escala_publico, atribuir_colaborador_escala 
from .views.area_publica.views_cadastro_colaborador import cadastro_colaborador, quero_ser_colaborador, cadastro_colaborador_por_telefone, api_buscar_cep_colaborador, verificar_telefone_colaborador_ajax
from .views.area_publica.views_youtube import verificar_youtube_ao_vivo, obter_url_youtube_canal

# Área Flutter / Mobile
from .views.area_flutter.flu_horarios_missas import horarios_missas_publico, api_horarios_missas, proximas_missas_api
from .views.area_publica.views_app import app_home, app_info, app_servicos, app_medias, app_config_api
from .views.area_publica.views_auth_api import api_login, api_register, api_password_reset
from .views.area_flutter.views_perfil import perfil_usuario, configuracoes_usuario

app_name = 'app_igreja'

# ==============================================================================
# 3. URL PATTERNS (Rotas Limpas)
# ==============================================================================

urlpatterns = [
    # Painel Administrativo
    path('admin-area/', views.admin_area, name='admin_area'),
    path('admin-area/dioceses/', diocese_crud_unico, name='diocese_crud_unico'),
    path('admin-area/paroquias/', paroquia_crud_unico, name='paroquia_crud_unico'),
    # Grupos
    path('admin-area/grupos/', listar_grupos, name='grupos_crud_mais'),
    path('admin-area/grupos/novo/', criar_grupo, name='criar_grupo'),
    path('admin-area/grupos/dashboard/', dashboard_grupos, name='dashboard_grupos'),
    path('admin-area/grupos/<int:grupo_id>/', detalhar_grupo, name='detalhar_grupo'),
    path('admin-area/grupos/<int:grupo_id>/editar/', editar_grupo, name='editar_grupo'),
    path('admin-area/grupos/<int:grupo_id>/excluir/', excluir_grupo, name='excluir_grupo'),
    # Funções
    path('admin-area/funcoes/', listar_funcoes, name='funcoes_crud_mais'),
    path('admin-area/funcoes/novo/', criar_funcao, name='criar_funcao'),
    path('admin-area/funcoes/dashboard/', dashboard_funcoes, name='dashboard_funcoes'),
    path('admin-area/funcoes/<int:funcao_id>/', detalhar_funcao, name='detalhar_funcao'),
    path('admin-area/funcoes/<int:funcao_id>/editar/', editar_funcao, name='editar_funcao'),
    path('admin-area/funcoes/<int:funcao_id>/excluir/', excluir_funcao, name='excluir_funcao'),
    # Celebrantes e Celebrantes
    path('admin-area/celebrantes/', listar_celebrantes, name='celebrantes_crud_mais'),
    path('admin-area/celebrantes/novo/', criar_celebrante, name='criar_celebrante'),
    path('admin-area/celebrantes/<int:celebrante_id>/', detalhar_celebrante, name='detalhar_celebrante'),
    path('admin-area/celebrantes/<int:celebrante_id>/editar/', editar_celebrante, name='editar_celebrante'),
    path('admin-area/celebrantes/<int:celebrante_id>/excluir/', excluir_celebrante, name='excluir_celebrante'),
    
    path('admin-area/colaboradores/', listar_colaboradores, name='listar_colaboradores'),
    path('admin-area/colaboradores/novo/', criar_colaborador, name='criar_colaborador'),
    path('admin-area/colaboradores/<int:colaborador_id>/', detalhar_colaborador, name='detalhar_colaborador'),
    path('admin-area/colaboradores/<int:colaborador_id>/editar/', editar_colaborador, name='editar_colaborador'),
    path('admin-area/colaboradores/<int:colaborador_id>/excluir/', excluir_colaborador, name='excluir_colaborador'),

    path('admin-area/configuracao-visual/', visual_generic_view, name='visual_generic'),
    
    # Orações (admin)
    path('admin-area/oracoes/', listar_oracoes, name='listar_oracoes'),
    path('admin-area/oracoes/novo/', criar_oracao, name='criar_oracao'),
    path('admin-area/oracoes/dashboard/', dashboard_oracoes, name='dashboard_oracoes'),
    path('admin-area/oracoes/<int:oracao_id>/', detalhar_oracao, name='detalhar_oracao'),
    path('admin-area/oracoes/<int:oracao_id>/editar/', editar_oracao, name='editar_oracao'),
    path('admin-area/oracoes/<int:oracao_id>/excluir/', excluir_oracao, name='excluir_oracao'),
    path('admin-area/oracoes/<int:oracao_id>/alterar-status/', alterar_status_oracao, name='alterar_status_oracao'),
    path('admin-area/oracoes/<int:oracao_id>/toggle-ativo/', toggle_ativo_oracao, name='toggle_ativo_oracao'),
    
    # Celebrações (admin)
    path('admin-area/celebracoes/', listar_celebracoes, name='listar_celebracoes'),
    path('admin-area/celebracoes/novo/', criar_celebracao, name='criar_celebracao'),
    path('admin-area/celebracoes/<int:celebracao_id>/', detalhar_celebracao, name='detalhar_celebracao'),
    path('admin-area/celebracoes/<int:celebracao_id>/editar/', editar_celebracao, name='editar_celebracao'),
    path('admin-area/celebracoes/<int:celebracao_id>/excluir/', excluir_celebracao, name='excluir_celebracao'),
    
    # Gestão de Dizimistas
    path('gerenciar-dizimistas/', gerenciar_dizimistas, name='gerenciar_dizimistas'),
    path('gerenciar-dizimistas/novo/', criar_dizimista, name='criar_dizimista'),
    path('gerenciar-dizimistas/dashboard/', dashboard_dizimistas, name='dashboard_dizimistas'),
    path('gerenciar-dizimistas/<int:dizimista_id>/', detalhar_dizimista, name='detalhar_dizimista'),
    path('gerenciar-dizimistas/<int:dizimista_id>/editar/', editar_dizimista, name='editar_dizimista'),
    path('gerenciar-dizimistas/<int:dizimista_id>/excluir/', excluir_dizimista, name='excluir_dizimista'),
    path('gerenciar-dizimistas/api/cep/<str:cep>/', api_cep, name='api_cep_dizimistas'),
    
    # Conteúdo (Liturgias, Avisos, Mural, Banners)
    path('admin-area/liturgias/', listar_liturgias, name='listar_liturgias'),
    path('admin-area/avisos/', listar_avisos, name='listar_avisos'),
    path('admin-area/avisos/novo/', criar_aviso, name='criar_aviso'),
    path('admin-area/avisos/<int:aviso_id>/', detalhar_aviso, name='detalhar_aviso'),
    path('admin-area/avisos/<int:aviso_id>/editar/', editar_aviso, name='editar_aviso'),
    path('admin-area/avisos/<int:aviso_id>/excluir/', excluir_aviso, name='excluir_aviso'),
    path('admin-area/mural/', listar_murais, name='listar_murais'),
    path('admin-area/mural/criar/', criar_mural, name='criar_mural'),
    path('admin-area/mural/<int:mural_id>/', detalhar_mural, name='detalhar_mural'),
    path('admin-area/mural/<int:mural_id>/editar/', editar_mural, name='editar_mural'),
    path('admin-area/mural/<int:mural_id>/excluir/', excluir_mural, name='excluir_mural'),
    path('admin-area/banners/', listar_banners, name='listar_banners'),
    path('admin-area/banners/novo/', criar_banner, name='criar_banner'),
    path('admin-area/banners/<int:banner_id>/', detalhar_banner, name='detalhar_banner'),
    path('admin-area/banners/<int:banner_id>/editar/', editar_banner, name='editar_banner'),
    path('admin-area/banners/<int:banner_id>/excluir/', excluir_banner, name='excluir_banner'),
    
    # Eventos Master-Detail
    path('admin-area/eventos/', listar_eventos, name='listar_eventos'),
    path('admin-area/eventos-master-detail/', MasterDetailEventoListView.as_view(), name='eventos_master_detail_list'),
    path('admin-area/eventos-master-detail/create/', MasterDetailCreateView.as_view(), name='eventos_master_detail_create'),
    path('admin-area/eventos-master-detail/create/<int:pk>/', MasterDetailCreateView.as_view(), name='eventos_master_detail_create_pk'),
    path('admin-area/eventos-master-detail/<int:pk>/delete/', MasterDetailDeleteView.as_view(), name='eventos_master_detail_delete'),
    path('admin-area/eventos-master-detail/<int:pk>/', MasterDetailEventoView.as_view(), name='eventos_master_detail_view'),
    
    # Modelos (master-detail)
    path('admin-area/modelos-master-detail/', MasterDetailModeloListView.as_view(), name='modelos_master_detail_list'),
    path('admin-area/modelos-master-detail/create/', MasterDetailModeloCreateView.as_view(), name='modelos_master_detail_create'),
    path('admin-area/modelos-master-detail/create/<int:pk>/', MasterDetailModeloCreateView.as_view(), name='modelos_master_detail_create_pk'),
    path('admin-area/modelos-master-detail/<int:pk>/delete/', MasterDetailModeloDeleteView.as_view(), name='modelos_master_detail_delete'),
    path('admin-area/modelos-master-detail/<int:pk>/', MasterDetailModeloView.as_view(), name='modelos_master_detail_view'),
    
    # Escalas e Apontamentos
    path('admin-area/escala-mensal/', escala_mensal_form, name='escala_mensal_form'),
    path('admin-area/escala-mensal/gerar/<int:mes>/<int:ano>/', escala_mensal_gerar, name='escala_mensal_gerar'),
    path('admin-area/escala-mensal/<int:mes>/<int:ano>/', escala_mensal_visualizar, name='escala_mensal_visualizar'),
    path('admin-area/escala-mensal/item/<int:pk>/editar-descricao/', escala_mensal_editar_descricao, name='escala_mensal_editar_descricao'),
    path('admin-area/gerenciar-escala/', listar_itens_escala, name='listar_itens_escala'),
    path('admin-area/gerenciar-escala/criar/', criar_item_escala, name='criar_item_escala'),
    path('admin-area/gerenciar-escala/<int:pk>/', detalhar_item_escala, name='detalhar_item_escala'),
    path('admin-area/gerenciar-escala/<int:pk>/editar/', editar_item_escala, name='editar_item_escala'),
    path('admin-area/gerenciar-escala/<int:pk>/excluir/', excluir_item_escala, name='excluir_item_escala'),
    path('admin-area/apontamentos-escala-missa/', apontamentos_escala_missa, name='apontamentos_escala_missa'),
    path('admin-area/apontamentos-escala-missa/<int:item_id>/atribuir/', atribuir_apontamento, name='atribuir_apontamento'),
    path('admin-area/agenda-mes/', agenda_mes, name='agenda_mes'),
    path('admin-area/agenda-mes/modelo/<int:modelo_id>/encargos/', buscar_encargos_modelo, name='buscar_encargos_modelo'),
    
    # Financeiro
    path('admin-area/gerar-mensalidade-dizimo/', gerar_mensalidade_dizimo_form, name='gerar_mensalidade_dizimo_form'),
    path('admin-area/gerar-mensalidade-dizimo/<int:mes>/<int:ano>/<int:dizimista_id>/', gerar_mensalidade_dizimo, name='gerar_mensalidade_dizimo'),
    path('admin-area/gerenciar-coleta-dizimo/', gerenciar_coleta_dizimo, name='gerenciar_coleta_dizimo'),
    path('admin-area/baixar-dizimo/', baixar_dizimo, name='baixar_dizimo'),
    path('admin-area/cancelar-baixa/', cancelar_baixa, name='cancelar_baixa'),
    
    # Relatórios
    path('admin-area/relatorios/aniversariantes/', relatorio_aniversariantes, name='relatorio_aniversariantes'),
    path('admin-area/relatorios/aniversariantes/pdf/', relatorio_aniversariantes_pdf, name='relatorio_aniversariantes_pdf'),
    path('admin-area/relatorios/escala-mensal-missas/', relatorio_escala_mensal_missas, name='relatorio_escala_mensal_missas'),
    path('admin-area/relatorios/escala-mensal-missas/pdf/', relatorio_escala_mensal_missas_pdf, name='relatorio_escala_mensal_missas_pdf'),
    path('admin-area/extrator-liturgias/', extrator_liturgias, name='extrator_liturgias'),
    path('admin-area/extrator-liturgias/api/', extrator_liturgias_api, name='extrator_liturgias_api'),

    # --- CHATBOT WHATSAPP (A ESTRUTURA NOVA) ---
    path('api/whatsapp/webhook/', whatsapp_webhook, name='whatsapp_webhook'),
    path('api/whatsapp/imagem-principal/', whatsapp_imagem_principal, name='whatsapp_imagem_principal'),
    path('admin-area/whatsapp/', whatsapp_list, name='whatsapp_list'),
    path('admin-area/whatsapp/enviar/', whatsapp_enviar_mensagem, name='whatsapp_enviar_mensagem'),
    path('admin-area/whatsapp/debug/', whatsapp_debug, name='whatsapp_debug'),
    path('admin-area/whatsapp/<int:pk>/', whatsapp_detail, name='whatsapp_detail'),
    path('admin-area/whatsapp/<int:pk>/excluir/', whatsapp_excluir, name='whatsapp_excluir'),
    
    # Área Pública (Front-end do Site)
    path('horarios-missas/', horarios_missas_publico, name='horarios_missas_publico'),
    path('liturgia-diaria/', liturgias_publico, name='liturgia_diaria'),
    path('contatos/', contatos_publico, name='contatos_publico'),
    path('quero-ser-dizimista/', quero_ser_dizimista, name='quero_ser_dizimista'),
    path('cadastro-dizimista/', cadastro_dizimista_pub, name='cadastro_dizimista_pub'),
    path('cadastro-dizimista/verificar-telefone/', verificar_telefone_cadastro_dizimista_pub, name='verificar_telefone_ajax'),
    path('avisos/', avisos_paroquia_pub, name='avisos_paroquia_pub'),
    path('cadastro-colaborador/', cadastro_colaborador, name='cadastro_colaborador'),
    path('quero-ser-colaborador/', quero_ser_colaborador, name='quero_ser_colaborador'),
    path('doacoes/', doacoes_publico, name='doacoes_publico'),
    path('escala-missas/', escala_publico, name='escala_publico'),
    path('escala-missas/atribuir/', atribuir_colaborador_escala, name='atribuir_colaborador_escala'),
    path('mural/', mural_publico_redirect, name='mural_publico_index'),
    path('mural/<int:mural_id>/', mural_publico, name='mural_publico'),
    path('aniversariantes-mes/', aniversariantes_publico, name='aniversariantes_publico'),
    path('calendario-eventos/', calendario_eventos_publico, name='calendario_eventos_publico'),
    path('calendario-eventos/<int:evento_id>/programacao/', ver_programacao_evento, name='ver_programacao_evento'),
    path('celebracoes-agendadas-pub/', list_celebracoes_agendadas_pub, name='celebracoes_agendadas_pub'),
    path('celebracoes-agendadas-pub/agendar/', agendar_celebracoes_agendadas_pub, name='celebracoes_agendadas_pub_agendar'),
    path('agendar-celebracao/', agendar_celebracoes_agendadas_pub, name='agendar_celebracao'),
    path('meus-pedidos-oracoes/', meus_pedidos_oracoes, name='meus_pedidos_oracoes'),
    path('meus-pedidos-oracoes/novo/', criar_pedido_oracao_publico, name='criar_pedido_oracao_publico'),
    path('celebracoes-agendadas-pub/<int:celebracao_id>/', detalhe_celebracoes_agendadas_pub, name='celebracoes_agendadas_pub_detalhe'),
    # App Flutter e API de Autenticação
    path('app/home/', app_home, name='app_home'),
    path('api/auth/login/', api_login, name='api_login'),
    path('perfil/', perfil_usuario, name='perfil_usuario'),
]
