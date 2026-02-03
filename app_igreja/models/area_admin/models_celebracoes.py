from django.db import models
from django.utils import timezone


class TBCELEBRACOES(models.Model):
    """Celebrações agendadas (admin)."""

    TIPO_CELEBRACAO_CHOICES = [
        ('batismo', 'Batismo'),
        ('casamento', 'Casamento'),
        ('primeira_comunhao', '1ª Comunhão'),
        ('crisma', 'Crisma'),
        ('missa_setimo_dia', 'Missa 7º Dia'),
        ('bodas', 'Bodas'),
        ('outras', 'Outras'),
    ]
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmada', 'Confirmada'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
    ]

    CEL_tipo_celebracao = models.CharField(max_length=50, choices=TIPO_CELEBRACAO_CHOICES, verbose_name="Tipo de Celebração")
    CEL_data_celebracao = models.DateField(verbose_name="Data da Celebração")
    CEL_horario = models.TimeField(verbose_name="Horário")
    CEL_local = models.CharField(max_length=100, verbose_name="Local")
    CEL_nome_solicitante = models.CharField(max_length=200, verbose_name="Nome do Solicitante")
    CEL_telefone = models.CharField(max_length=20, verbose_name="Telefone", db_index=True)
    CEL_email = models.EmailField(max_length=254, blank=True, null=True, verbose_name="E-mail")
    CEL_participantes = models.PositiveIntegerField(verbose_name="Número de Participantes")
    CEL_observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    CEL_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    CEL_data_cadastro = models.DateTimeField(default=timezone.now, verbose_name="Data de Cadastro")
    CEL_data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")

    class Meta:
        db_table = 'tbcelebracoes'
        verbose_name = 'Celebração'
        verbose_name_plural = 'Celebrações'
        ordering = ['CEL_data_celebracao', 'CEL_horario']

    def __str__(self):
        return f"{self.CEL_tipo_celebracao} - {self.CEL_nome_solicitante} ({self.CEL_data_celebracao})"

    @property
    def status_badge_class(self):
        d = {'pendente': 'bg-warning', 'confirmada': 'bg-info', 'realizada': 'bg-success', 'cancelada': 'bg-danger'}
        return d.get(self.CEL_status, 'bg-secondary')

    @property
    def status_display(self):
        return dict(self.STATUS_CHOICES).get(self.CEL_status, self.CEL_status)

    @property
    def tipo_celebracao_display(self):
        return dict(self.TIPO_CELEBRACAO_CHOICES).get(self.CEL_tipo_celebracao, self.CEL_tipo_celebracao)

    def save(self, *args, **kwargs):
        if self.CEL_telefone and '(' not in str(self.CEL_telefone) and '-' not in str(self.CEL_telefone):
            numeros = ''.join(filter(str.isdigit, str(self.CEL_telefone)))
            if numeros.startswith('55') and len(numeros) > 11:
                numeros = numeros[2:]
            if len(numeros) == 11:
                self.CEL_telefone = f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
            elif len(numeros) == 10:
                self.CEL_telefone = f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
        super().save(*args, **kwargs)
