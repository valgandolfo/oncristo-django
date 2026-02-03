from django.http import JsonResponse
from django.contrib.auth import authenticate, login as django_login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json

@csrf_exempt
def api_login(request):
    """
    API de login para o App Flutter.
    Retorna tokens fake (sessão) para compatibilidade.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            biometric_token = data.get('biometric_token')

            # Se for biometria, por enquanto vamos apenas validar se o token existe (simulado)
            if biometric_token:
                # Aqui você implementaria a lógica real de token biométrico
                # Por ora, vamos buscar o último usuário logado ou algo assim
                # Para simplificar, vamos pedir login por senha primeiro
                return JsonResponse({
                    'detail': 'Biometria ainda não configurada no backend. Use e-mail e senha.'
                }, status=400)

            # Autenticação por e-mail/senha
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                django_login(request, user)
                
                # Gerar um "token" (usaremos o ID da sessão por simplicidade sem DRF/JWT)
                session_id = request.session.session_key or ""
                
                return JsonResponse({
                    'access': session_id, # Usando session_key como access token fake
                    'refresh': 'fake-refresh-token',
                    'isAdmin': user.is_staff or user.is_superuser
                })
            else:
                return JsonResponse({'detail': 'E-mail ou senha inválidos.'}, status=401)
                
        except Exception as e:
            return JsonResponse({'detail': str(e)}, status=400)
            
    return JsonResponse({'detail': 'Método não permitido.'}, status=405)

@csrf_exempt
def api_register(request):
    """
    API de registro para o App Flutter.
    Aceita password2 (confirmação) mas não é obrigatório.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            password2 = data.get('password2')  # Opcional, mas se fornecido deve coincidir
            
            if not email or not password:
                return JsonResponse({'detail': 'E-mail e senha são obrigatórios.'}, status=400)
            
            # Validar confirmação de senha se fornecida
            if password2 and password != password2:
                return JsonResponse({'detail': 'As senhas não coincidem.'}, status=400)
                
            if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
                return JsonResponse({'detail': 'Este e-mail já está cadastrado.'}, status=400)
                
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                is_active=True
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Conta criada com sucesso!'
            }, status=201)
            
        except Exception as e:
            return JsonResponse({'detail': str(e)}, status=400)
            
    return JsonResponse({'detail': 'Método não permitido.'}, status=405)

@csrf_exempt
def api_password_reset(request):
    """
    API de solicitação de reset de senha para o App Flutter.
    """
    if request.method == 'POST':
        try:
            from django.contrib.auth.views import PasswordResetView
            from django.contrib.auth.forms import PasswordResetForm
            
            data = json.loads(request.body)
            email = data.get('email')
            
            if not email:
                return JsonResponse({'error': 'E-mail é obrigatório.'}, status=400)
            
            # Usar o formulário padrão do Django para reset de senha
            form = PasswordResetForm({'email': email})
            
            if form.is_valid():
                # Enviar email de reset
                form.save(
                    request=request,
                    use_https=request.is_secure(),
                    email_template_name='registration/password_reset_email.html',
                    subject_template_name='registration/password_reset_subject.txt',
                )
                return JsonResponse({
                    'success': True,
                    'message': 'E-mail de recuperação enviado com sucesso! Verifique sua caixa de entrada.'
                }, status=200)
            else:
                # Se o formulário não for válido, pode ser que o email não exista
                # Mas por segurança, sempre retornamos sucesso (para não expor emails)
                return JsonResponse({
                    'success': True,
                    'message': 'Se o e-mail estiver cadastrado, você receberá instruções para redefinir sua senha.'
                }, status=200)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
            
    return JsonResponse({'error': 'Método não permitido.'}, status=405)
