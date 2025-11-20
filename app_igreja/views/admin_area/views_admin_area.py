# ==================== VIEWS DA ÁREA ADMINISTRATIVA ====================
# Views principais da área administrativa

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
    """Decorator para verificar se o usuário é administrador"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Apenas superusuários podem acessar área admin
        if not request.user.is_superuser:
            messages.error(request, 'Acesso negado. Apenas administradores podem acessar esta área.')
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
@admin_required
def admin_area(request):
    """
    View para renderizar o dashboard da área administrativa.
    """
    context = {
        'page_title': 'Área do Administrador',
        'user': request.user,
    }
    return render(request, 'admin_area/admin_area.html', context)
