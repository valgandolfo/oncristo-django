from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def admin_required(view_func):
    """Decorator para verificar se o usuário é admin"""
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            from django.contrib import messages
            from django.shortcuts import redirect
            messages.error(request, 'Acesso negado. Apenas administradores podem acessar esta área.')
            return redirect('app_igreja:admin_area')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_required
@admin_required
def configuracao_visual(request):
    """
    View para configuração visual da área administrativa
    """
    return render(request, 'admin_area/configuracao_visual.html')
