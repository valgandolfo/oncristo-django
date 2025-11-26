from django.db import models
from django.utils import timezone

class TBCELEBRACOES(models.Model):
    """
    Modelo para Celebrações Agendadas via WhatsApp
    """
    
    TIPO_CELEBRACAO_CHOICES = [
        ('batismo', 'Batismo'),
        ('casamento', 'Casamento'),
        ('primeira_comunhao', '1ª Comunhão'),
        ('crisma', 'Crisma'),
        ('missa_setimo_dia', 'Missa 7º Dia'),
        ('bodas', 'Bodas'),
        ('outras', 'Outras'),
    ]
    
    CEL_tipo_celebracao = models.CharField(
        max_length=50,
        choices=TIPO_CELEBRACAO_CHOICES,
        verbose_name="Tipo de Celebração",
        help_text="Selecione o tipo de celebração"
    )
    
    CEL_data_celebracao = models.DateField(
        verbose_name="Data da Celebração",
        help_text="Data em que será realizada a celebração"
    )
    
    CEL_horario = models.TimeField(
        verbose_name="Horário",
        help_text="Horário da celebração"
    )
    
    CEL_local = models.CharField(
        max_length=100,
        verbose_name="Local",
        help_text="Local onde será realizada a celebração"
    )
    
    CEL_nome_solicitante = models.CharField(
        max_length=200,
        verbose_name="Nome do Solicitante",
        help_text="Nome completo da pessoa que solicitou"
    )
    
    CEL_telefone = models.CharField(
        max_length=20,
        verbose_name="Telefone",
        help_text="Telefone para contato",
        db_index=True  # Índice para otimizar buscas
    )
    
    CEL_email = models.EmailField(
        max_length=254,
        blank=True,
        null=True,
        verbose_name="E-mail",
        help_text="E-mail para contato (opcional)"
    )
    
    CEL_participantes = models.PositiveIntegerField(
        verbose_name="Número de Participantes",
        help_text="Quantidade estimada de participantes"
    )
    
    CEL_observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações",
        help_text="Observações adicionais sobre a celebração"
    )
    
    CEL_status = models.CharField(
        max_length=20,
        choices=[
            ('pendente', 'Pendente'),
            ('confirmada', 'Confirmada'),
            ('realizada', 'Realizada'),
            ('cancelada', 'Cancelada'),
        ],
        default='pendente',
        verbose_name="Status",
        help_text="Status atual da celebração"
    )
    
    CEL_data_cadastro = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data de Cadastro",
        help_text="Data e hora do cadastro"
    )
    
    CEL_data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Atualização",
        help_text="Data e hora da última atualização"
    )

    class Meta:
        db_table = 'tbcelebracoes'
        verbose_name = 'Celebração'
        verbose_name_plural = 'Celebrações'
        ordering = ['CEL_data_celebracao', 'CEL_horario']

    def __str__(self):
        return f"{self.CEL_tipo_celebracao} - {self.CEL_nome_solicitante} ({self.CEL_data_celebracao})"

    @property
    def status_badge_class(self):
        """Retorna a classe CSS para o badge de status"""
        status_classes = {
            'pendente': 'bg-warning',
            'confirmada': 'bg-info',
            'realizada': 'bg-success',
            'cancelada': 'bg-danger',
        }
        return status_classes.get(self.CEL_status, 'bg-secondary')

    @property
    def status_display(self):
        """Retorna o status formatado para exibição"""
        status_display = {
            'pendente': 'Pendente',
            'confirmada': 'Confirmada',
            'realizada': 'Realizada',
            'cancelada': 'Cancelada',
        }
        return status_display.get(self.CEL_status, self.CEL_status)

    def get_CEL_tipo_celebracao_display(self):
        """Retorna o tipo de celebração formatado para exibição"""
        return dict(self.TIPO_CELEBRACAO_CHOICES).get(self.CEL_tipo_celebracao, self.CEL_tipo_celebracao)
    
    @property
    def tipo_celebracao_display(self):
        """Retorna o tipo de celebração formatado para exibição"""
        tipo_display = {
            'batismo': 'Batismo',
            'casamento': 'Casamento',
            'primeira_comunhao': '1ª Comunhão',
            'crisma': 'Crisma',
            'missa_setimo_dia': 'Missa 7º Dia',
            'bodas': 'Bodas',
            'outras': 'Outras',
        }
        return tipo_display.get(self.CEL_tipo_celebracao, self.CEL_tipo_celebracao)
