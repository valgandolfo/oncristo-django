"""
==================== VIEWS DE PARÓQUIAS ====================
Arquivo de views específicas para Paróquias

🔗 HERDA COMPONENTES DE:
├── Models: app_igreja.models.area_admin.models_paroquias.TBPAROQUIA
├── Forms: app_igreja.forms.area_admin.forms_paroquias.ParoquiaForm, ParoquiaHorariosForm
├── Templates: templates.admin_area.tpl_paroquia.html
├── CSS: static/css/configuracoes-visuais.css (cores e layout)
└── Tags: app_igreja.templatetags.paroquia_extras (get_horario_dia, format_horarios)

📋 FUNCIONALIDADES:
├── Visualização de dados da paróquia (registro único)
├── Edição inline dos dados principais
├── Gerenciamento de horários fixos de celebração em JSON
└── Controle de acesso apenas para administradores
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Imports específicos com comentários de origem
from ...models.area_admin.models_paroquias import TBPAROQUIA  # Model: dados da paróquia
from ...forms.area_admin.forms_paroquias import ParoquiaForm, ParoquiaHorariosForm  # Forms: validação de dados


def admin_required(view_func):
    """Decorator para verificar se o usuário é admin"""
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, 'Acesso negado. Apenas administradores podem acessar esta área.')
            return redirect('app_igreja:admin_area')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_required
@admin_required
def paroquia_generic_view(request):
    """
    View principal para Paróquia - Sistema Single-Record CRUD
    
    🎯 FUNCIONAMENTO:
    ├── GET sem '?edit=1': Modo VISUALIZAÇÃO (somente leitura)
    ├── GET com '?edit=1': Modo EDIÇÃO (formulários ativos)
    ├── POST: Salva dados principais + horários em JSON
    └── Template: tpl_paroquia.html (visualização + edição na mesma tela)
    
    🔄 FLUXO DE DADOS:
    ├── TBPAROQUIA (Database) ⟷ ParoquiaForm (Validation)
    ├── PAR_horarios_fixos_json ⟷ ParoquiaHorariosForm (7 campos → JSON)
    └── Template Tags: formatação de horários para exibição
    
    ⚙️ REQUIRED:
    ├── Login: @login_required (usuário autenticado)
    ├── Admin: @admin_required (superuser apenas)
    └── Decorators: admin_required customizado neste arquivo
    """
    # Buscar paróquia existente ou criar nova
    paroquia = TBPAROQUIA.objects.first()
    if not paroquia:
        paroquia = TBPAROQUIA.objects.create(
            PAR_nome_paroquia="Nova Paróquia",
            PAR_diocese=None,  # ForeignKey deve ser None, não string vazia
            PAR_paroco="",
            PAR_secretario="",
            PAR_cep="",
            PAR_endereco="",
            PAR_numero="",
            PAR_cidade="",
            PAR_uf="",
            PAR_bairro="",
            PAR_telefone="",
            PAR_email="",
            PAR_cnpj="",
            PAR_banco="",
            PAR_agencia="",
            PAR_conta="",
            PAR_pix_chave="",
            PAR_pix_tipo="",
            PAR_pix_beneficiario="",
            PAR_pix_cidade="",
            PAR_pix_uf=""
        )
        messages.info(request, 'Paróquia criada automaticamente. Preencha os dados.')
    
    # Determinar modo de operação
    modo_edicao = request.GET.get('edit') == '1'
    modo_visualizacao = not modo_edicao
    
    if request.method == 'POST':
        # Processar dados principais
        form = ParoquiaForm(request.POST, request.FILES, instance=paroquia)
        if form.is_valid():
            form.save()
            
            # Processar horários separadamente
            form_horarios = ParoquiaHorariosForm(request.POST, instance=paroquia)
            if form_horarios.is_valid():
                # Salvar horários no formato JSON
                horarios_data = {}
                for dia in ['domingo', 'segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado']:
                    campo_horarios = form_horarios.cleaned_data.get(f'{dia}_horarios', '')
                    if campo_horarios:
                        # Converter string separada por vírgulas em lista
                        horarios_data[dia] = [h.strip() for h in campo_horarios.split(',') if h.strip()]
                    else:
                        horarios_data[dia] = []
                
                paroquia.set_horarios_fixos(horarios_data)
                paroquia.save()
            
            messages.success(request, 'Dados da paróquia atualizados com sucesso!')
            # Redirecionar para modo consulta (sem ?edit=1)
            return redirect('app_igreja:paroquia_generic')
        else:
            messages.error(request, 'Erro ao salvar dados. Verifique os campos.')
    
    # Preparar formulários
    if modo_edicao:
        form = ParoquiaForm(instance=paroquia)
    else:
        form = None
    
    # Sempre preparar formulário de horários (com tratamento de erro)
    try:
        form_horarios = ParoquiaHorariosForm(instance=paroquia)
    except Exception as e:
        # Se houver erro ao criar form_horarios, criar um vazio sem instance
        form_horarios = ParoquiaHorariosForm()
    
    context = {
        'paroquia': paroquia,
        'form': form,
        'form_horarios': form_horarios,
        'modo_edicao': modo_edicao,
        'modo_visualizacao': modo_visualizacao,
    }
    
    return render(request, 'admin_area/tpl_paroquia.html', context)
