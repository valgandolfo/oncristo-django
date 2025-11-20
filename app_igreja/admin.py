from django.contrib import admin
from .models.area_admin.models_dioceses import TBDIOCESE
from .models.area_admin.models_planos import TBPLANO
from .models.area_publica.models_liturgias import TBLITURGIA
# from .models.area_publica.models_horarios_missas import TBHORARIOMISSA

# Register your models here.

@admin.register(TBDIOCESE)
class TBDIOCESEAdmin(admin.ModelAdmin):
    """
    Configuração do admin para TBDIOCESSE
    """
    
    # Campos exibidos na listagem
    list_display = [
        'DIO_id',
        'DIO_nome_diocese', 
        'DIO_cidade', 
        'DIO_uf', 
        'DIO_nome_bispo', 
        'DIO_data_criacao'
    ]
    
    # Campos para filtros laterais
    list_filter = [
        'DIO_uf',
        'DIO_cidade',
        'DIO_data_criacao'
    ]
    
    # Campos para busca
    search_fields = [
        'DIO_nome_diocese',
        'DIO_cidade',
        'DIO_uf',
        'DIO_nome_bispo',
        'DIO_email'
    ]
    
    # Campos agrupados no formulário
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('DIO_nome_diocese',)
        }),
        ('Endereço', {
            'fields': ('DIO_endereco', 'DIO_cidade', 'DIO_uf', 'DIO_cep'),
            'classes': ('collapse',)
        }),
        ('Contato', {
            'fields': ('DIO_telefone', 'DIO_email', 'DIO_site'),
            'classes': ('collapse',)
        }),
        ('Informações do Bispo', {
            'fields': ('DIO_nome_bispo', 'DIO_foto_bispo'),
            'classes': ('collapse',)
        }),
        ('Controle', {
            'fields': ('DIO_data_criacao', 'DIO_data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    # Campos somente leitura
    readonly_fields = ['DIO_data_criacao', 'DIO_data_atualizacao']
    
    # Ordenação padrão
    ordering = ['DIO_nome_diocese']
    
    # Paginação
    list_per_page = 25

@admin.register(TBPLANO)
class TBPLANOAdmin(admin.ModelAdmin):
    """
    Configuração do admin para TBPLANO
    """
    
    # Campos exibidos na listagem
    list_display = [
        'PLA_id',
        'PLA_titulo_plano',
        'PLA_ativo',
        'PLA_data_cadastro',
        'PLA_data_atualizacao'
    ]
    
    # Campos para filtros laterais
    list_filter = [
        'PLA_ativo',
        'PLA_data_cadastro'
    ]
    
    # Campos para busca
    search_fields = [
        'PLA_titulo_plano'
    ]
    
    # Campos agrupados no formulário
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('PLA_titulo_plano', 'PLA_ativo')
        }),
        ('Controle', {
            'fields': ('PLA_data_cadastro', 'PLA_data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    # Campos somente leitura
    readonly_fields = ['PLA_data_cadastro', 'PLA_data_atualizacao']
    
    # Ordenação padrão
    ordering = ['-PLA_data_cadastro']
    
    # Paginação
    list_per_page = 25

@admin.register(TBLITURGIA)
class TBLITURGIAAdmin(admin.ModelAdmin):
    """
    Configuração do admin para TBLITURGIA
    """
    
    # Campos exibidos na listagem
    list_display = [
        'LIT_id',
        'LIT_DATALIT',
        'LIT_TIPOLIT',
        'LIT_STATUSLIT',
        'LIT_DATA_CADASTRO',
        'LIT_DATA_ATUALIZACAO'
    ]
    
    # Campos para filtros laterais
    list_filter = [
        'LIT_DATALIT',
        'LIT_TIPOLIT',
        'LIT_STATUSLIT',
        'LIT_DATA_CADASTRO'
    ]
    
    # Campos para busca
    search_fields = [
        'LIT_TEXTO',
        'LIT_TIPOLIT'
    ]
    
    # Campos agrupados no formulário
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('LIT_DATALIT', 'LIT_TIPOLIT', 'LIT_STATUSLIT')
        }),
        ('Conteúdo', {
            'fields': ('LIT_TEXTO',)
        }),
        ('Controle', {
            'fields': ('LIT_DATA_CADASTRO', 'LIT_DATA_ATUALIZACAO'),
            'classes': ('collapse',)
        }),
    )
    
    # Campos somente leitura
    readonly_fields = ['LIT_DATA_CADASTRO', 'LIT_DATA_ATUALIZACAO']
    
    # Ordenação padrão
    ordering = ['-LIT_DATALIT', 'LIT_TIPOLIT']
    
    # Paginação
    list_per_page = 25

# @admin.register(TBHORARIOMISSA)
# class TBHORARIOMISSAAdmin(admin.ModelAdmin):
#     """
#     Configuração do admin para TBHORARIOMISSA
#     """
#     
#     # Campos exibidos na listagem
#     list_display = [
#         'HOR_id',
#         'HOR_dia_semana',
#         'HOR_horario',
#         'HOR_tipo_missa',
#         'HOR_local',
#         'HOR_celebrante',
#         'HOR_ativo',
#         'HOR_data_cadastro'
#     ]
#     
#     # Campos para filtros laterais
#     list_filter = [
#         'HOR_dia_semana',
#         'HOR_tipo_missa',
#         'HOR_ativo',
#         'HOR_data_cadastro'
#     ]
#     
#     # Campos para busca
#     search_fields = [
#         'HOR_local',
#         'HOR_celebrante',
#         'HOR_observacoes'
#     ]
#     
#     # Campos agrupados no formulário
#     fieldsets = (
#         ('Informações Básicas', {
#             'fields': ('HOR_dia_semana', 'HOR_horario', 'HOR_tipo_missa', 'HOR_ativo')
#         }),
#         ('Detalhes da Missa', {
#             'fields': ('HOR_local', 'HOR_celebrante', 'HOR_observacoes')
#         }),
#         ('Controle', {
#             'fields': ('HOR_data_cadastro', 'HOR_data_atualizacao'),
#             'classes': ('collapse',)
#         }),
#     )
#     
#     # Campos somente leitura
#     readonly_fields = ['HOR_data_cadastro', 'HOR_data_atualizacao']
#     
#     # Ordenação padrão
#     ordering = ['HOR_dia_semana', 'HOR_horario']
#     
#     # Paginação
#     list_per_page = 25