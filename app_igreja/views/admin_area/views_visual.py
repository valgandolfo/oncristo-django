"""Configurações visuais (registro único): imagens capa, brasão, padroeiro, principal (admin)."""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ...models.area_admin.models_visual import TBVISUAL
from ...forms.area_admin.forms_visual import VisualForm


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.is_superuser or request.user.is_staff):
            messages.error(request, 'Acesso negado. Apenas administradores podem acessar esta área.')
            return redirect('app_igreja:admin_area')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_required
@admin_required
def visual_generic_view(request):
    """Single-record CRUD: GET sem ?edit=1 = visualização; GET ?edit=1 = edição; POST = salvar."""
    visual = TBVISUAL.objects.first()
    if not visual:
        visual = TBVISUAL.objects.create()
        messages.info(request, 'Configurações visuais criadas automaticamente. Adicione as imagens.')

    modo_edicao = request.GET.get('edit') == '1'
    modo_visualizacao = not modo_edicao

    if request.method == 'POST':
        form = VisualForm(request.POST, request.FILES, instance=visual)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Configurações visuais atualizadas com sucesso! As imagens foram salvas no Wasabi.')
                return redirect('app_igreja:visual_generic')
            except Exception as e:
                messages.error(request, f'Erro ao salvar imagens no Wasabi: {str(e)}')
                context = {'visual': visual, 'form': form, 'modo_edicao': True, 'modo_visualizacao': False}
                return render(request, 'admin_area/tpl_visual.html', context)
        messages.error(request, f'Erro ao salvar dados. Verifique os campos: {form.errors}')
    else:
        form = VisualForm(instance=visual) if modo_edicao else None

    context = {
        'visual': visual,
        'form': form,
        'modo_edicao': modo_edicao,
        'modo_visualizacao': modo_visualizacao,
    }
    return render(request, 'admin_area/tpl_visual.html', context)
