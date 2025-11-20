"""
==================== VIEWS DE CONFIGURAÇÕES VISUAIS ====================
Arquivo de views específicas para Configurações Visuais

🔗 HERDA COMPONENTES DE:
├── Models: app_igreja.models.area_admin.models_visual.TBVISUAL
├── Forms: app_igreja.forms.area_admin.forms_visual.VisualForm
├── Templates: templates.admin_area.tpl_visual.html
└── CSS: static/css/configuracoes-visuais.css (cores e layout)

📋 FUNCIONALIDADES:
├── Visualização de imagens (registro único)
├── Edição inline das imagens
└── Controle de acesso apenas para administradores
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Imports específicos
from ...models.area_admin.models_visual import TBVISUAL
from ...forms.area_admin.forms_visual import VisualForm


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
def visual_generic_view(request):
    """
    View principal para Configurações Visuais - Sistema Single-Record CRUD
    
    🎯 FUNCIONAMENTO:
    ├── GET sem '?edit=1': Modo VISUALIZAÇÃO (somente leitura)
    ├── GET com '?edit=1': Modo EDIÇÃO (formulários ativos)
    ├── POST: Salva imagens
    └── Template: tpl_visual.html (visualização + edição na mesma tela)
    
    🔄 FLUXO DE DADOS:
    ├── TBVISUAL (Database) ⟷ VisualForm (Validation)
    └── Campos: 4 imagens (capa, brasão, padroeiro, principal)
    
    ⚙️ REQUIRED:
    ├── Login: @login_required (usuário autenticado)
    ├── Admin: @admin_required (superuser apenas)
    └── Single Record: apenas um registro no sistema
    """
    # Buscar registro existente ou criar novo
    visual = TBVISUAL.objects.first()
    if not visual:
        visual = TBVISUAL.objects.create()
        messages.info(request, 'Configurações visuais criadas automaticamente. Adicione as imagens.')
    
    # Determinar modo de operação
    modo_edicao = request.GET.get('edit') == '1'
    modo_visualizacao = not modo_edicao
    
    if request.method == 'POST':
        # Processar dados
        form = VisualForm(request.POST, request.FILES, instance=visual)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Configurações visuais atualizadas com sucesso! As imagens foram salvas no AWS S3.')
            except Exception as e:
                messages.error(request, f'Erro ao salvar imagens no S3: {str(e)}')
                return render(request, 'admin_area/tpl_visual.html', {
                    'visual': visual,
                    'form': form,
                    'modo_edicao': True,
                    'modo_visualizacao': False,
                })
            # Redirecionar para modo consulta (sem ?edit=1)
            return redirect('app_igreja:visual_generic')
        else:
            messages.error(request, 'Erro ao salvar dados. Verifique os campos.')
    
    # Preparar formulário
    if modo_edicao:
        form = VisualForm(instance=visual)
    else:
        form = None
    
    context = {
        'visual': visual,
        'form': form,
        'modo_edicao': modo_edicao,
        'modo_visualizacao': modo_visualizacao,
    }
    
    return render(request, 'admin_area/tpl_visual.html', context)

