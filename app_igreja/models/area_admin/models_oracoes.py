from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User


def _telefone_formatado(telefone):
    if not telefone:
        return ""
    numeros = ''.join(filter(str.isdigit, str(telefone)))
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    if len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    return telefone


limpar_telefone_para_display = _telefone_formatado  # compat área pública


class TBORACOES(models.Model):
    """Pedidos de orações (admin)."""

    TIPO_ORACAO_CHOICES = [
        ('SAUDE', 'Saúde'), ('FAMILIA', 'Família'), ('TRABALHO', 'Trabalho'), ('ESTUDOS', 'Estudos'),
        ('RELACIONAMENTO', 'Relacionamento'), ('FINANCAS', 'Finanças'), ('CONVERSAO', 'Conversão'),
        ('GRATIDAO', 'Gratidão'), ('OUTRO', 'Outro'),
    ]
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'), ('EM_ORACAO', 'Em Oração'), ('ATENDIDO', 'Atendido'), ('CANCELADO', 'Cancelado'),
    ]

    ORA_nome_solicitante = models.CharField(max_length=200, verbose_name="Nome do Solicitante")
    ORA_telefone_pedinte = models.CharField(max_length=20, verbose_name="Telefone do Solicitante")
    ORA_tipo_oracao = models.CharField(max_length=100, verbose_name="Tipo de Oração", choices=TIPO_ORACAO_CHOICES)
    ORA_descricao = models.TextField(verbose_name="Descrição da Oração")
    ORA_status = models.CharField(max_length=20, verbose_name="Status", choices=STATUS_CHOICES, default='PENDENTE')
    ORA_ativo = models.BooleanField(verbose_name="Ativo", default=True)
    ORA_data_pedido = models.DateField(verbose_name="Data do Pedido", default=timezone.now)
    ORA_data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    ORA_data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    ORA_usuario_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuário Responsável")

    class Meta:
        verbose_name = "Pedido de Oração"
        verbose_name_plural = "Pedidos de Orações"
        db_table = 'TBORACOES'
        ordering = ['-ORA_data_pedido', 'ORA_nome_solicitante']

    def __str__(self):
        return f"{self.ORA_nome_solicitante} - {self.get_ORA_tipo_oracao_display()}"

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.ORA_status, self.ORA_status)

    def get_status_class(self):
        d = {'PENDENTE': 'warning', 'EM_ORACAO': 'info', 'ATENDIDO': 'success', 'CANCELADO': 'secondary'}
        return d.get(self.ORA_status, 'info')

    def get_telefone_formatado(self):
        return _telefone_formatado(self.ORA_telefone_pedinte)

    def get_tipo_oracao_display(self):
        return dict(self.TIPO_ORACAO_CHOICES).get(self.ORA_tipo_oracao, self.ORA_tipo_oracao)

    def is_pendente(self):
        return self.ORA_status == 'PENDENTE'

    def is_ativo(self):
        return self.ORA_ativo

    def calcular_dias_pedido(self):
        base = self.ORA_data_pedido.date() if hasattr(self.ORA_data_pedido, 'date') else self.ORA_data_pedido
        return (timezone.now().date() - base).days

    def clean(self):
        if self.ORA_telefone_pedinte:
            n = ''.join(filter(str.isdigit, str(self.ORA_telefone_pedinte)))
            if len(n) < 10:
                raise ValidationError("Telefone deve ter pelo menos 10 dígitos")
        if self.ORA_descricao and len(self.ORA_descricao.strip()) < 10:
            raise ValidationError("A descrição deve ter pelo menos 10 caracteres")

    def save(self, *args, **kwargs):
        if self.ORA_telefone_pedinte and '(' not in str(self.ORA_telefone_pedinte) and '-' not in str(self.ORA_telefone_pedinte):
            self.ORA_telefone_pedinte = _telefone_formatado(self.ORA_telefone_pedinte)
        self.clean()
        super().save(*args, **kwargs)
