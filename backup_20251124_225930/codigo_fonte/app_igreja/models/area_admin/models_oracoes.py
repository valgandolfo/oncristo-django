from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import date, datetime


def limpar_telefone_para_display(telefone):
    """Função auxiliar para formatar telefone para exibição"""
    if not telefone:
        return ""
    
    # Remove caracteres não numéricos
    numeros = ''.join(filter(str.isdigit, str(telefone)))
    
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    elif len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    else:
        return telefone


class TBORACOES(models.Model):
    """Modelo para cadastro de pedidos de orações"""
    
    
    TIPO_ORACAO_CHOICES = [
        ('SAUDE', 'Saúde'),
        ('FAMILIA', 'Família'),
        ('TRABALHO', 'Trabalho'),
        ('ESTUDOS', 'Estudos'),
        ('RELACIONAMENTO', 'Relacionamento'),
        ('FINANCAS', 'Finanças'),
        ('CONVERSAO', 'Conversão'),
        ('GRATIDAO', 'Gratidão'),
        ('OUTRO', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('EM_ORACAO', 'Em Oração'),
        ('ATENDIDO', 'Atendido'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    # Campos obrigatórios
    ORA_nome_solicitante = models.CharField(max_length=200, verbose_name="Nome do Solicitante")
    ORA_telefone_pedinte = models.CharField(max_length=20, verbose_name="Telefone do Solicitante")
    ORA_tipo_oracao = models.CharField(max_length=100, verbose_name="Tipo de Oração", choices=TIPO_ORACAO_CHOICES)
    ORA_descricao = models.TextField(verbose_name="Descrição da Oração")
    ORA_status = models.CharField(max_length=20, verbose_name="Status", choices=STATUS_CHOICES, default='PENDENTE')
    ORA_ativo = models.BooleanField(verbose_name="Ativo", default=True)
    ORA_data_pedido = models.DateField(verbose_name="Data do Pedido", default=timezone.now)
    
    # Datas de controle
    ORA_data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    ORA_data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    # Usuário que cadastrou (opcional)
    ORA_usuario_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuário Responsável")
    
    def __str__(self):
        return f"{self.ORA_nome_solicitante} - {self.get_ORA_tipo_oracao_display()}"
    
    class Meta:
        verbose_name = "Pedido de Oração"
        verbose_name_plural = "Pedidos de Orações"
        db_table = 'TBORACOES'
        ordering = ['-ORA_data_pedido', 'ORA_nome_solicitante']
    
    def get_status_display(self):
        """Retorna o status formatado"""
        return dict(self.STATUS_CHOICES).get(self.ORA_status, self.ORA_status)
    
    def get_status_class(self):
        """Retorna a classe CSS para o status"""
        status_classes = {
            'PENDENTE': 'warning',
            'EM_ORACAO': 'info',
            'ATENDIDO': 'success',
            'CANCELADO': 'secondary',
        }
        return status_classes.get(self.ORA_status, 'info')
    
    def get_telefone_formatado(self):
        """Retorna o telefone formatado"""
        return limpar_telefone_para_display(self.ORA_telefone_pedinte)
    
    def get_tipo_oracao_display(self):
        """Retorna o tipo de oração formatado"""
        return dict(self.TIPO_ORACAO_CHOICES).get(self.ORA_tipo_oracao, self.ORA_tipo_oracao)
    
    def is_pendente(self):
        """Verifica se o pedido está pendente"""
        return self.ORA_status == 'PENDENTE'
    
    def is_ativo(self):
        """Verifica se o pedido está ativo"""
        return self.ORA_ativo
    
    def calcular_dias_pedido(self):
        """Calcula quantos dias desde o pedido"""
        base_date = self.ORA_data_pedido.date() if hasattr(self.ORA_data_pedido, 'date') else self.ORA_data_pedido
        return (timezone.now().date() - base_date).days
    
    def clean(self):
        """Validação personalizada"""
        from django.core.exceptions import ValidationError
        
        # Validação do telefone
        if self.ORA_telefone_pedinte:
            # Remove caracteres não numéricos
            telefone_limpo = ''.join(filter(str.isdigit, str(self.ORA_telefone_pedinte)))
            if len(telefone_limpo) < 10:
                raise ValidationError("Telefone deve ter pelo menos 10 dígitos")
        
        # Validação da data do pedido (normaliza para date)
        # Permite datas futuras conforme solicitado
        if self.ORA_data_pedido:
            _ = self.ORA_data_pedido.date() if isinstance(self.ORA_data_pedido, datetime) else self.ORA_data_pedido
        
        # Validação da descrição
        if self.ORA_descricao and len(self.ORA_descricao.strip()) < 10:
            raise ValidationError("A descrição deve ter pelo menos 10 caracteres")
    
    def save(self, *args, **kwargs):
        """Override do save para aplicar validações"""
        self.clean()
        super().save(*args, **kwargs)
