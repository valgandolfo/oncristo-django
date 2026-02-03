from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import json

@login_required
def perfil_usuario(request):
    """
    Página de perfil do usuário no modo app
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Aqui você pode processar as atualizações do perfil
            # Por enquanto, apenas retorna sucesso
            return JsonResponse({'success': True, 'message': 'Perfil atualizado com sucesso!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    context = {
        'modo_app': request.GET.get('modo') == 'app',
    }
    return render(request, 'area_flutter/flu_perfil_usuario.html', context)

@login_required
def configuracoes_usuario(request):
    """
    Página de configurações do usuário no modo app
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Processar configurações (futuramente)
            return JsonResponse({'success': True, 'message': 'Configurações salvas!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    context = {
        'modo_app': request.GET.get('modo') == 'app',
    }
    return render(request, 'area_flutter/flu_configuracoes_usuarios.html', context)