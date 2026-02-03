"""
==================== VIEWS DE REGISTRO ====================
Arquivo com views para registro de usuários
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError
import re


@csrf_protect
def register_view(request):
    """
    View para registro de novos usuários
    """
    
    if request.method == 'POST':
        # Dados do formulário
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        
        # Validações
        errors = []
        
        # Validar email
        if not email:
            errors.append('E-mail é obrigatório')
        elif User.objects.filter(email=email).exists():
            errors.append('Este e-mail já está cadastrado')
        elif User.objects.filter(username=email).exists():
            errors.append('Este e-mail já está cadastrado')
        
        # Validar senha
        if not password1:
            errors.append('Senha é obrigatória')
        elif len(password1) < 8:
            errors.append('Senha deve ter pelo menos 8 caracteres')
        elif not re.search(r'[A-Z]', password1):
            errors.append('Senha deve ter pelo menos uma letra maiúscula')
        elif not re.search(r'[a-z]', password1):
            errors.append('Senha deve ter pelo menos uma letra minúscula')
        elif not re.search(r'\d', password1):
            errors.append('Senha deve ter pelo menos um número')
        
        # Validar confirmação de senha
        if password1 != password2:
            errors.append('As senhas não coincidem')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                # Criar usuário
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password1,
                    is_active=True
                )
                
                # Fazer login automático - especificar backend quando há múltiplos
                from django.contrib.auth import get_backends
                backend = 'app_igreja.backends.EmailBackend'
                login(request, user, backend=backend)
                
                # Mensagem de boas-vindas
                messages.success(
                    request,
                    f'Conta criada com sucesso! Bem-vindo(a)!'
                )
                
                # Redirecionar para página inicial ou próxima página
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
                
            except Exception as e:
                messages.error(request, f'Erro ao criar conta: {str(e)}')
    
    # Contexto mínimo para o formulário de registro
    context = {
        'paroquia': None
    }
    
    return render(request, 'registration/register.html', context)
