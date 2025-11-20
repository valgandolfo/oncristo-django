# ==================== VIEWS DE RELATÓRIOS ====================
# Este arquivo conterá todas as views relacionadas a relatórios
# Exemplo: relatorio_dioceses, relatorio_membros, etc.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from functools import wraps
import inspect

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

# ==================== VIEWS DE RELATÓRIOS ====================
# Adicionar views de relatórios aqui quando necessário

# def relatorio_dioceses(request):
#     pass

# def relatorio_membros(request):
#     pass

# def relatorio_eventos(request):
#     pass
