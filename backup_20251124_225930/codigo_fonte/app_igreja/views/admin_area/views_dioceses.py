"""
==================== VIEWS DE DIOCESES ====================
Arquivo de views específicas para Dioceses

🔗 HERDA COMPONENTES DE:
├── Models: app_igreja.models.area_admin.models_dioceses.TBDIOCESE
├── Forms: app_igreja.forms.area_admin.forms_dioceses.DioceseForm
├── Templates: templates/admin_area/tpl_dioceses.html
├── CSS: static/css/configuracoes-visuais.css (cores por seção)
└── Commons: app_igreja.forms.area_admin.forms_commons.BaseAdminForm

📋 FUNCIONALIDADES:
├── Visualização de dados da diocese (registro único)
├── Edição de informações básicas (nome, bispo, endereço)
└── Controle de acesso administrador
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from functools import wraps

# Imports específicos com comentários de origem
from ...models.area_admin.models_dioceses import TBDIOCESE  # Model: dados da diocese
from ...forms.area_admin.forms_dioceses import DioceseForm  # Form: validação com BaseAdminForm

def admin_required(view_func):
    """Decorator para verificar se o usuário é administrador"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, 'Acesso negado. Apenas administradores podem acessar esta área.')
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# ==================== VIEWS DE DIOCESES ====================

@login_required
@admin_required
def diocese_detail(request):
    """
    View unificada para Diocese - Sistema Single-Record CRUD
    
    🎯 FUNCIONAMENTO:
    ├── GET sem '?edit=1': Modo VISUALIZAÇÃO (somente leitura)
    ├── GET com '?edit=1': Modo EDIÇÃO (formulários ativos)
    ├── POST: Salva dados da diocese
    └── Template: tpl_diocese.html (visualização + edição na mesma tela)
    
    🔄 FLUXO DE DADOS:
    ├── TBDIOCESE (Database) ⟷ DioceseForm (Validation)
    ├── Campos: nome, bispo, foto, endereço, contatos
    └── Estilo: herança de static/css/configuracoes-visuais.css
    
    ⚙️ REQUIRED:
    ├── Login: @login_required (usuário autenticado)
    ├── Admin: @admin_required (superuser apenas)
    └── Single Record: apenas uma diocese no sistema
    """
    
    # Buscar diocese existente ou criar uma nova
    diocese = TBDIOCESE.objects.first()
    if not diocese:
        diocese = TBDIOCESE.objects.create(
            DIO_nome_diocese="Nova Diocese",
            DIO_nome_bispo="",
            DIO_foto_bispo=None,
            DIO_cep="",
            DIO_endereco="",
            DIO_numero="",
            DIO_complemento="",
            DIO_bairro="",
            DIO_cidade="",
            DIO_uf="",
            DIO_telefone="",
            DIO_email="",
            DIO_site=""
        )
        messages.info(request, 'Diocese criada automaticamente. Preencha os dados.')
    
    # Determinar modo de operação
    modo_edicao = request.GET.get('edit') == '1'
    modo_visualizacao = not modo_edicao
    
    if request.method == 'POST':
        form = DioceseForm(request.POST, request.FILES, instance=diocese)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados da Diocese atualizados com sucesso!')
            # Redirecionar para modo consulta (sem ?edit=1)
            return redirect('app_igreja:diocese_detail')
        else:
            messages.error(request, 'Erro ao salvar dados. Verifique os campos.')
    
    # Preparar formulários
    if modo_edicao:
        form = DioceseForm(instance=diocese)
    else:
        form = None
    
    context = {
        'diocese': diocese,
        'form': form,
        'modo_edicao': modo_edicao,
        'modo_visualizacao': modo_visualizacao,
    }
    
    return render(request, 'admin_area/tpl_dioceses.html', context)