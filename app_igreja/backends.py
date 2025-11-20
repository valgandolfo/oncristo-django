"""
Backend de autenticação customizado para permitir login por email
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Backend de autenticação que permite login por email ou username
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('username')
        
        if username is None or password is None:
            return None
        
        try:
            # Tentar encontrar usuário por email ou username
            user = User.objects.get(
                Q(email=username) | Q(username=username)
            )
        except User.DoesNotExist:
            # Executar hash da senha para evitar timing attacks
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Se houver múltiplos usuários com o mesmo email, pegar o primeiro
            user = User.objects.filter(
                Q(email=username) | Q(username=username)
            ).first()
        
        # Verificar senha e se o usuário pode autenticar
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None

