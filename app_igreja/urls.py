from django.urls import path
from . import views
from .views.admin_area.views_dioceses import diocese_detail
from .views.admin_area.views_paroquias import paroquia_generic_view

from .views.admin_area.views_visual import visual_generic_view
from .views.admin_area.views_celebrantes import listar_celebrantes, criar_celebrante, editar_celebrante, excluir_celebrante, detalhar_celebrante
from .views.admin_area.views_colaboradores import listar_colaboradores, criar_colaborador, editar_colaborador, excluir_colaborador, detalhar_colaborador
from .views.admin_area.views_dizimistas import listar_dizimistas, criar_dizimista, editar_dizimista, excluir_dizimista, detalhar_dizimista, dashboard_dizimistas, api_cep
from .views.admin_area.views_banners import listar_banners, criar_banner, editar_banner, excluir_banner, detalhar_banner
from .views.admin_area.views_celebracoes import listar_celebracoes, criar_celebracao, editar_celebracao, excluir_celebracao, detalhar_celebracao
from .views.admin_area.views_avisos import listar_avisos, criar_aviso, editar_aviso, detalhar_aviso, excluir_aviso
from .views.admin_area.views_liturgias import listar_liturgias, criar_liturgia, editar_liturgia, detalhar_liturgia, excluir_liturgia
from .views.admin_area.views_grupos import listar_grupos, criar_grupo, editar_grupo, excluir_grupo, detalhar_grupo, dashboard_grupos
from .views.admin_area.views_funcoes import listar_funcoes, criar_funcao, editar_funcao, excluir_funcao, detalhar_funcao, dashboard_funcoes
from .views.admin_area.views_oracoes import listar_oracoes, criar_oracao, editar_oracao, excluir_oracao, detalhar_oracao, dashboard_oracoes, alterar_status_oracao, toggle_ativo_oracao
# URLs antigas de Planos removidas - substituídas por Eventos
# from .views.admin_area.views_planos import listar_planos, criar_plano, editar_plano, excluir_plano, detalhar_plano
# from .views.admin_area.views_planos_master_detail import (
#     MasterDetailPlanoListView, MasterDetailPlanoView, MasterDetailCreateView,
#     MasterDetailDeleteView, MasterDetailItensView
# )
# from .views.admin_area.views_item_plano import listar_itens_plano, criar_item_plano, editar_item_plano, excluir_item_plano, detalhar_item_plano
from .views.admin_area.views_eventos import (
    listar_eventos, criar_evento, editar_evento, excluir_evento, detalhar_evento,
    listar_itens_evento, criar_item_evento, editar_item_evento, excluir_item_evento, detalhar_item_evento
)
from .views.admin_area.views_eventos_master_detail import (
    MasterDetailEventoListView, MasterDetailEventoView, MasterDetailCreateView as MasterDetailEventoCreateView,
    MasterDetailDeleteView as MasterDetailEventoDeleteView, MasterDetailItensView as MasterDetailEventoItensView
)
from .views.admin_area.views_escala_mensal_missa import escala_mensal_form, escala_mensal_gerar, escala_mensal_visualizar, escala_mensal_editar_descricao
from .views.admin_area.views_gerenciar_dizimo import gerar_mensalidade_dizimo_form, gerar_mensalidade_dizimo, listar_mensalidades_dizimo, gerenciar_coleta_dizimo, baixar_dizimo, cancelar_baixa
from .views.admin_area.views_gerenciar_escala import listar_itens_escala, criar_item_escala, detalhar_item_escala, editar_item_escala, excluir_item_escala
from .views.admin_area.views_apontamentos_missas import apontamentos_escala_missa, atribuir_apontamento
from .views.admin_area.views_whatsapp import whatsapp_enviar_mensagem, whatsapp_list, whatsapp_detail, whatsapp_excluir, whatsapp_debug
from .views.admin_area.views_mural import listar_murais, criar_mural, editar_mural, excluir_mural, detalhar_mural
from .views.admin_area.views_modelos_master_detail import (
    MasterDetailModeloListView,
    MasterDetailModeloView,
    MasterDetailModeloCreateView,
    MasterDetailModeloDeleteView,
)
from .views.admin_area.views_agenda_mes import agenda_mes, excluir_agenda_dia, buscar_encargos_modelo
from .views.admin_area.views_extrator_liturgias import extrator_liturgias, extrator_liturgias_api
from .views.admin_area.views_relatorios import relatorio_aniversariantes, relatorio_escala_mensal_missas, relatorio_aniversariantes_pdf, relatorio_escala_mensal_missas_pdf
# inicio das views da área pública
from .views.area_publica.views_liturgias import liturgia_modal, api_liturgia, visualizar_liturgia
from .views.area_publica.views_liturgias_publico import liturgias_publico
from .views.area_publica.views_horarios_missas import horarios_missas_publico, api_horarios_missas, proximas_missas_api
from .views.area_publica.views_contatos import contatos_publico
from .views.area_publica.views_dizimistas import quero_ser_dizimista, verificar_telefone_ajax
from .views.area_publica.views_oracoes import meus_pedidos_oracoes, detalhar_oracao_publico, criar_pedido_oracao_publico
from .views.area_publica.views_avisos import avisos_paroquia
from .views.area_publica.views_calendario_eventos import calendario_eventos_publico, ver_programacao_evento
from .views.area_publica.views_aniversariantes import aniversariantes_mes
from .views.area_publica.views_celebracoes_publico import minhas_celebracaoes_publico, agendar_celebracao_publico, detalhar_celebracao_publico
from .views.area_publica.views_doacoes import doacoes_publico
from .views.area_publica.views_whatsapp_api import whatsapp_webhook, whatsapp_test_webhook, whatsapp_cadastro_dizimista, whatsapp_imagem_principal
from .views.area_publica.views_youtube import verificar_youtube_ao_vivo, obter_url_youtube_canal
from .views.area_publica.views_mural import mural_publico
from .views.area_publica.views_colaboradores_publico import cadastro_colaborador_publico, api_buscar_cep, api_excluir_colaborador, quero_ser_colaborador
from .views.area_publica.views_escala_publico import escala_publico, atribuir_colaborador_escala 

app_name = 'app_igreja'

urlpatterns = [
    # URL para área administrativa principal (dashboard)
    path('admin-area/', views.admin_area, name='admin_area'),
    
    # URLs para Dioceses - Estrutura mais lógica (apenas uma diocese)
    path('admin-area/dioceses/', diocese_detail, name='diocese_detail'),
    
           # URLs para Paróquias - Sistema Genérico
           path('admin-area/paroquias/', paroquia_generic_view, name='paroquia_generic'),
           
           # URLs para Configurações Visuais
           path('admin-area/configuracao-visual/', visual_generic_view, name='visual_generic'),
    
    
    
    # URLs para Celebrantes - Sistema Funcional
    path('admin-area/celebrantes/', listar_celebrantes, name='listar_celebrantes'),
    path('admin-area/celebrantes/novo/', criar_celebrante, name='criar_celebrante'),
    path('admin-area/celebrantes/<int:celebrante_id>/', detalhar_celebrante, name='detalhar_celebrante'),
    path('admin-area/celebrantes/<int:celebrante_id>/editar/', editar_celebrante, name='editar_celebrante'),
    path('admin-area/celebrantes/<int:celebrante_id>/excluir/', excluir_celebrante, name='excluir_celebrante'),
    
    # URLs para Celebrantes - Sistema Genérico (removidas na reversão)
    
    # URLs para Colaboradores - CRUD completo
    path('admin-area/colaboradores/', listar_colaboradores, name='listar_colaboradores'),
    path('admin-area/colaboradores/novo/', criar_colaborador, name='criar_colaborador'),
    path('admin-area/colaboradores/<int:colaborador_id>/', detalhar_colaborador, name='detalhar_colaborador'),
    path('admin-area/colaboradores/<int:colaborador_id>/editar/', editar_colaborador, name='editar_colaborador'),
    path('admin-area/colaboradores/<int:colaborador_id>/excluir/', excluir_colaborador, name='excluir_colaborador'),
    
    # URLs para Dizimistas - CRUD completo
    path('admin-area/dizimistas/', listar_dizimistas, name='listar_dizimistas'),
    path('admin-area/dizimistas/novo/', criar_dizimista, name='criar_dizimista'),
    path('admin-area/dizimistas/<int:dizimista_id>/', detalhar_dizimista, name='detalhar_dizimista'),
    path('admin-area/dizimistas/<int:dizimista_id>/editar/', editar_dizimista, name='editar_dizimista'),
    path('admin-area/dizimistas/<int:dizimista_id>/excluir/', excluir_dizimista, name='excluir_dizimista'),
    path('admin-area/dizimistas/dashboard/', dashboard_dizimistas, name='dashboard_dizimistas'),
    path('api/cep/<str:cep>/', api_cep, name='api_cep'),
    
    # URLs para Banners de Patrocinadores - CRUD completo
    path('admin-area/banners/', listar_banners, name='listar_banners'),
    path('admin-area/banners/novo/', criar_banner, name='criar_banner'),
    path('admin-area/banners/<int:banner_id>/', detalhar_banner, name='detalhar_banner'),
    path('admin-area/banners/<int:banner_id>/editar/', editar_banner, name='editar_banner'),
    path('admin-area/banners/<int:banner_id>/excluir/', excluir_banner, name='excluir_banner'),
    
    # URLs para Celebrações - CRUD completo
    path('admin-area/celebracoes/', listar_celebracoes, name='listar_celebracoes'),
    path('admin-area/celebracoes/novo/', criar_celebracao, name='criar_celebracao'),
    path('admin-area/celebracoes/<int:celebracao_id>/', detalhar_celebracao, name='detalhar_celebracao'),
    path('admin-area/celebracoes/<int:celebracao_id>/editar/', editar_celebracao, name='editar_celebracao'),
    path('admin-area/celebracoes/<int:celebracao_id>/excluir/', excluir_celebracao, name='excluir_celebracao'),
    
    # URLs para Avisos - CRUD completo
    path('admin-area/avisos/', listar_avisos, name='listar_avisos'),
    path('admin-area/avisos/novo/', criar_aviso, name='criar_aviso'),
    path('admin-area/avisos/<int:aviso_id>/', detalhar_aviso, name='detalhar_aviso'),
    path('admin-area/avisos/<int:aviso_id>/editar/', editar_aviso, name='editar_aviso'),
    path('admin-area/avisos/<int:aviso_id>/excluir/', excluir_aviso, name='excluir_aviso'),
    
    # URLs para Liturgias - CRUD completo
    path('admin-area/liturgias/', listar_liturgias, name='listar_liturgias'),
    path('admin-area/liturgias/novo/', criar_liturgia, name='criar_liturgia'),
    path('admin-area/liturgias/<int:liturgia_id>/', detalhar_liturgia, name='detalhar_liturgia'),
    path('admin-area/liturgias/<int:liturgia_id>/editar/', editar_liturgia, name='editar_liturgia'),
    path('admin-area/liturgias/<int:liturgia_id>/excluir/', excluir_liturgia, name='excluir_liturgia'),
    
    # URLs para Grupos Litúrgicos
    path('admin-area/grupos/', listar_grupos, name='listar_grupos'),
    path('admin-area/grupos/novo/', criar_grupo, name='criar_grupo'),
    path('admin-area/grupos/<int:grupo_id>/', detalhar_grupo, name='detalhar_grupo'),
    path('admin-area/grupos/<int:grupo_id>/editar/', editar_grupo, name='editar_grupo'),
    path('admin-area/grupos/<int:grupo_id>/excluir/', excluir_grupo, name='excluir_grupo'),
    path('admin-area/grupos/dashboard/', dashboard_grupos, name='dashboard_grupos'),
    
    # URLs para Funções
    path('admin-area/funcoes/', listar_funcoes, name='listar_funcoes'),
    path('admin-area/funcoes/novo/', criar_funcao, name='criar_funcao'),
    path('admin-area/funcoes/<int:funcao_id>/', detalhar_funcao, name='detalhar_funcao'),
    path('admin-area/funcoes/<int:funcao_id>/editar/', editar_funcao, name='editar_funcao'),
    path('admin-area/funcoes/<int:funcao_id>/excluir/', excluir_funcao, name='excluir_funcao'),
    path('admin-area/funcoes/dashboard/', dashboard_funcoes, name='dashboard_funcoes'),
    
    # URLs para Pedidos de Orações - CRUD completo
    path('admin-area/oracoes/', listar_oracoes, name='listar_oracoes'),
    path('admin-area/oracoes/novo/', criar_oracao, name='criar_oracao'),
    path('admin-area/oracoes/<int:oracao_id>/', detalhar_oracao, name='detalhar_oracao'),
    path('admin-area/oracoes/<int:oracao_id>/editar/', editar_oracao, name='editar_oracao'),
    path('admin-area/oracoes/<int:oracao_id>/excluir/', excluir_oracao, name='excluir_oracao'),
    path('admin-area/oracoes/dashboard/', dashboard_oracoes, name='dashboard_oracoes'),
    
    
    # URLs antigas de Planos de Ação - REMOVIDAS (substituídas por Eventos)
    # path('admin-area/planos/', listar_planos, name='listar_planos'),
    # path('admin-area/planos/novo/', criar_plano, name='criar_plano'),
    # path('admin-area/planos/<int:plano_id>/', detalhar_plano, name='detalhar_plano'),
    # path('admin-area/planos/<int:plano_id>/editar/', editar_plano, name='editar_plano'),
    # path('admin-area/planos/<int:plano_id>/excluir/', excluir_plano, name='excluir_plano'),
    # 
    # # URLs para Planos Master-Detail - CRUD unificado
    # path('admin-area/planos-master-detail/', MasterDetailPlanoListView.as_view(), name='planos_master_detail_list'),
    # path('admin-area/planos-master-detail/create/', MasterDetailCreateView.as_view(), name='planos_master_detail_create'),
    # path('admin-area/planos-master-detail/create/<int:pk>/', MasterDetailCreateView.as_view(), name='planos_master_detail_create_pk'),
    # path('admin-area/planos-master-detail/<int:pk>/', MasterDetailPlanoView.as_view(), name='planos_master_detail_view'),
    # path('admin-area/planos-master-detail/<int:pk>/delete/', MasterDetailDeleteView.as_view(), name='planos_master_detail_delete'),
    # path('admin-area/planos-master-detail/<int:pk>/itens/', MasterDetailItensView.as_view(), name='planos_master_detail_itens'),
    # 
    # # URLs para Itens do Plano - CRUD completo
    # path('admin-area/itens-plano/', listar_itens_plano, name='listar_itens_plano'),
    # path('admin-area/itens-plano/plano/<int:plano_id>/', listar_itens_plano, name='listar_itens_plano_por_plano'),
    # path('admin-area/itens-plano/novo/', criar_item_plano, name='criar_item_plano'),
    # path('admin-area/itens-plano/novo/plano/<int:plano_id>/', criar_item_plano, name='criar_item_plano_por_plano'),
    # path('admin-area/itens-plano/<int:item_id>/', detalhar_item_plano, name='detalhar_item_plano'),
    # path('admin-area/itens-plano/<int:item_id>/editar/', editar_item_plano, name='editar_item_plano'),
    # path('admin-area/itens-plano/<int:item_id>/excluir/', excluir_item_plano, name='excluir_item_plano'),
    
    # URLs para Eventos - CRUD completo
    path('admin-area/eventos/', listar_eventos, name='listar_eventos'),
    path('admin-area/eventos/novo/', criar_evento, name='criar_evento'),
    path('admin-area/eventos/<int:evento_id>/', detalhar_evento, name='detalhar_evento'),
    path('admin-area/eventos/<int:evento_id>/editar/', editar_evento, name='editar_evento'),
    path('admin-area/eventos/<int:evento_id>/excluir/', excluir_evento, name='excluir_evento'),
    
    # URLs para Eventos Master-Detail - CRUD unificado
    path('admin-area/eventos-master-detail/', MasterDetailEventoListView.as_view(), name='eventos_master_detail_list'),
    path('admin-area/eventos-master-detail/create/', MasterDetailEventoCreateView.as_view(), name='eventos_master_detail_create'),
    path('admin-area/eventos-master-detail/create/<int:pk>/', MasterDetailEventoCreateView.as_view(), name='eventos_master_detail_create_pk'),
    path('admin-area/eventos-master-detail/<int:pk>/', MasterDetailEventoView.as_view(), name='eventos_master_detail_view'),
    path('admin-area/eventos-master-detail/<int:pk>/delete/', MasterDetailEventoDeleteView.as_view(), name='eventos_master_detail_delete'),
    path('admin-area/eventos-master-detail/<int:pk>/itens/', MasterDetailEventoItensView.as_view(), name='eventos_master_detail_itens'),
    
    # URLs para Itens do Evento - CRUD completo
    path('admin-area/itens-evento/', listar_itens_evento, name='listar_itens_evento'),
    path('admin-area/itens-evento/evento/<int:evento_id>/', listar_itens_evento, name='listar_itens_evento_por_evento'),
    path('admin-area/itens-evento/novo/', criar_item_evento, name='criar_item_evento'),
    path('admin-area/itens-evento/novo/evento/<int:evento_id>/', criar_item_evento, name='criar_item_evento_por_evento'),
    path('admin-area/itens-evento/<int:item_id>/', detalhar_item_evento, name='detalhar_item_evento'),
    path('admin-area/itens-evento/<int:item_id>/editar/', editar_item_evento, name='editar_item_evento'),
    path('admin-area/itens-evento/<int:item_id>/excluir/', excluir_item_evento, name='excluir_item_evento'),
    
    # URLs para Escala Mensal
    path('admin-area/escala-mensal/', escala_mensal_form, name='escala_mensal_form'),
    path('admin-area/escala-mensal/gerar/<int:mes>/<int:ano>/', escala_mensal_gerar, name='escala_mensal_gerar'),
    path('admin-area/escala-mensal/<int:mes>/<int:ano>/', escala_mensal_visualizar, name='escala_mensal_visualizar'),
    path('admin-area/escala-mensal/editar-descricao/<int:pk>/', escala_mensal_editar_descricao, name='escala_mensal_editar_descricao'),
    
    # URLs para Gerenciar Escala de Missas
    path('admin-area/gerenciar-escala/', listar_itens_escala, name='listar_itens_escala'),
    
    # URLs para Apontamentos Escala Missa
    path('admin-area/apontamentos-escala-missa/', apontamentos_escala_missa, name='apontamentos_escala_missa'),
    path('admin-area/apontamentos-escala-missa/<int:item_id>/atribuir/', atribuir_apontamento, name='atribuir_apontamento'),
    
    # URLs para Gerenciar Mensalidades de Dizimistas
    path('admin-area/gerar-mensalidade-dizimo/', gerar_mensalidade_dizimo_form, name='gerar_mensalidade_dizimo_form'),
    path('admin-area/gerar-mensalidade-dizimo/<int:mes>/<int:ano>/<int:dizimista_id>/', gerar_mensalidade_dizimo, name='gerar_mensalidade_dizimo'),
    path('admin-area/listar-mensalidades-dizimo/', listar_mensalidades_dizimo, name='listar_mensalidades_dizimo'),
    path('admin-area/listar-mensalidades-dizimo/<int:mes>/<int:ano>/', listar_mensalidades_dizimo, name='listar_mensalidades_dizimo'),
    path('admin-area/gerenciar-coleta-dizimo/', gerenciar_coleta_dizimo, name='gerenciar_coleta_dizimo'),
    path('admin-area/baixar-dizimo/', baixar_dizimo, name='baixar_dizimo'),
    path('admin-area/cancelar-baixa/', cancelar_baixa, name='cancelar_baixa'),
    path('admin-area/gerenciar-escala/novo/', criar_item_escala, name='criar_item_escala'),
    path('admin-area/gerenciar-escala/<int:pk>/', detalhar_item_escala, name='detalhar_item_escala'),
    path('admin-area/gerenciar-escala/<int:pk>/editar/', editar_item_escala, name='editar_item_escala'),
    path('admin-area/gerenciar-escala/<int:pk>/excluir/', excluir_item_escala, name='excluir_item_escala'),
    
    # URLs para WhatsApp
    path('admin-area/whatsapp/enviar/', whatsapp_enviar_mensagem, name='whatsapp_enviar_mensagem'),
    path('admin-area/whatsapp/', whatsapp_list, name='whatsapp_list'),
    path('admin-area/whatsapp/<int:pk>/', whatsapp_detail, name='whatsapp_detail'),
    path('admin-area/whatsapp/<int:pk>/excluir/', whatsapp_excluir, name='whatsapp_excluir'),
    path('admin-area/whatsapp/debug/', whatsapp_debug, name='whatsapp_debug'),
    
    # URLs para Mural da Paróquia - CRUD completo
    path('admin-area/mural/', listar_murais, name='listar_murais'),
    path('admin-area/mural/novo/', criar_mural, name='criar_mural'),
    path('admin-area/mural/<int:mural_id>/', detalhar_mural, name='detalhar_mural'),
    path('admin-area/mural/<int:mural_id>/editar/', editar_mural, name='editar_mural'),
    path('admin-area/mural/<int:mural_id>/excluir/', excluir_mural, name='excluir_mural'),
    
    # URLs para Extrator de Liturgias
    path('admin-area/extrator-liturgias/', extrator_liturgias, name='extrator_liturgias'),
    path('admin-area/extrator-liturgias/api/', extrator_liturgias_api, name='extrator_liturgias_api'),
    
    # URLs para Relatórios - Área Administrativa
    path('admin-area/relatorios/aniversariantes/', relatorio_aniversariantes, name='relatorio_aniversariantes'),
    path('admin-area/relatorios/aniversariantes/pdf/', relatorio_aniversariantes_pdf, name='relatorio_aniversariantes_pdf'),
    path('admin-area/relatorios/escala-mensal-missas/', relatorio_escala_mensal_missas, name='relatorio_escala_mensal_missas'),
    path('admin-area/relatorios/escala-mensal-missas/pdf/', relatorio_escala_mensal_missas_pdf, name='relatorio_escala_mensal_missas_pdf'),
    
    # URLs para Modelos - CRUD master-detail
    path('admin-area/modelos-master-detail/', MasterDetailModeloListView.as_view(), name='modelos_master_detail_list'),
    path('admin-area/modelos-master-detail/create/', MasterDetailModeloCreateView.as_view(), name='modelos_master_detail_create'),
    path('admin-area/modelos-master-detail/create/<int:pk>/', MasterDetailModeloCreateView.as_view(), name='modelos_master_detail_create_pk'),
    path('admin-area/modelos-master-detail/<int:pk>/', MasterDetailModeloView.as_view(), name='modelos_master_detail_view'),
    path('admin-area/modelos-master-detail/<int:pk>/delete/', MasterDetailModeloDeleteView.as_view(), name='modelos_master_detail_delete'),
    
    # URLs para Agenda do Mês
    path('admin-area/agenda-mes/', agenda_mes, name='agenda_mes'),
    path('admin-area/agenda-mes/<int:agenda_id>/excluir/', excluir_agenda_dia, name='excluir_agenda_dia'),
    path('admin-area/agenda-mes/modelo/<int:modelo_id>/encargos/', buscar_encargos_modelo, name='buscar_encargos_modelo'),
    
    # URLs para Área Pública
    path('horarios-missas/', horarios_missas_publico, name='horarios_missas_publico'),
    # Redirecionamento do singular para o plural por compatibilidade
    path('contato/', contatos_publico, name='contato_publico_redirect'),
    path('contatos/', contatos_publico, name='contatos_publico'),
    # URLs para Liturgias - Área Pública
    path('liturgias/', liturgias_publico, name='liturgias_publico'),
    # URLs antigas mantidas para compatibilidade (API)
    path('api/liturgia/<str:data>/', api_liturgia, name='api_liturgia'),
    path('liturgias/visualizar/<str:data>/', visualizar_liturgia, name='visualizar_liturgia'),
    
    # URLs para Cadastro Público de Dizimistas
    path('quero-ser-dizimista/', quero_ser_dizimista, name='quero_ser_dizimista'),
    path('verificar-telefone/', verificar_telefone_ajax, name='verificar_telefone_ajax'),
    
    # URLs para Cadastro Público de Colaboradores
    path('quero-ser-colaborador/', quero_ser_colaborador, name='quero_ser_colaborador'),
    path('colaboradores/cadastro/<str:telefone>/', cadastro_colaborador_publico, name='cadastro_colaborador_publico'),
    path('colaboradores/api/cep/<str:cep>/', api_buscar_cep, name='api_buscar_cep_colaborador'),
    path('colaboradores/api/excluir/<str:telefone>/', api_excluir_colaborador, name='api_excluir_colaborador'),
    
    # URLs para Consulta Pública de Pedidos de Orações
    path('meus-pedidos-oracoes/', meus_pedidos_oracoes, name='meus_pedidos_oracoes'),
    path('meus-pedidos-oracoes/novo/', criar_pedido_oracao_publico, name='criar_pedido_oracao_publico'),
    path('meus-pedidos-oracoes/<int:oracao_id>/', detalhar_oracao_publico, name='detalhar_oracao_publico'),
    
    # URLs para Avisos da Paróquia
    path('avisos-paroquia/', avisos_paroquia, name='avisos_paroquia'),
    
    # URLs para Calendário de Eventos - Área Pública
    path('calendario-eventos/', calendario_eventos_publico, name='calendario_eventos_publico'),
    path('calendario-eventos/<int:evento_id>/programacao/', ver_programacao_evento, name='ver_programacao_evento'),
    
    # URLs para Aniversariantes do Mês - Área Pública
    path('aniversariantes-mes/', aniversariantes_mes, name='aniversariantes_mes'),
    
    # URLs para Agendar Celebrações
    path('agendar-celebracao/', agendar_celebracao_publico, name='agendar_celebracao_publico'),
    path('agendar-celebracaoes/', minhas_celebracaoes_publico, name='minhas_celebracaoes_publico'),
    path('celebracao/<int:celebracao_id>/detalhe/', detalhar_celebracao_publico, name='detalhar_celebracao_publico'),
    
    # URLs para Doações
    path('doacoes/', doacoes_publico, name='doacoes_publico'),
    
    # URLs para Escala de Missas (Área Pública)
    path('escala-missas/', escala_publico, name='escala_publico'),
    path('escala-missas/atribuir/', atribuir_colaborador_escala, name='atribuir_colaborador_escala'),
    
    # URLs para Mural (Área Pública)
    path('mural/<int:mural_id>/', mural_publico, name='mural_publico'),
    
    # URLs para API WhatsApp - Chatbot
    path('api/whatsapp/webhook/', whatsapp_webhook, name='whatsapp_webhook'),
    path('api/whatsapp/test/', whatsapp_test_webhook, name='whatsapp_test_webhook'),
    path('api/whatsapp/cadastro-dizimista/', whatsapp_cadastro_dizimista, name='whatsapp_cadastro_dizimista'),
    path('api/whatsapp/imagem-principal/', whatsapp_imagem_principal, name='whatsapp_imagem_principal'),
    
    # URLs para YouTube - Transmissão ao Vivo
    path('api/youtube/verificar-ao-vivo/', verificar_youtube_ao_vivo, name='verificar_youtube_ao_vivo'),
    path('api/youtube/canal/', obter_url_youtube_canal, name='obter_url_youtube_canal'),
]