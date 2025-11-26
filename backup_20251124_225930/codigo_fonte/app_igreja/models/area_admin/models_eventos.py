from django.db import models
from django.utils import timezone
from .models_celebrantes import TBCELEBRANTES


class TBEVENTO(models.Model):
    """
    Modelo para Eventos
    """
    
    TIPO_CHOICES = [
        ('Missa', 'Missa'),
        ('Celebração', 'Celebração'),
        ('Casamento', 'Casamento'),
        ('Reunião', 'Reunião'),
        ('Formação', 'Formação'),
        ('Festa', 'Festa'),
        ('Retiro', 'Retiro'),
        ('Confissão', 'Confissão'),
        ('Adoração', 'Adoração'),
        ('Novena', 'Novena'),
        ('Outro', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('Ativo', 'Ativo'),
        ('Inativo', 'Inativo'),
        ('Cancelado', 'Cancelado'),
        ('Concluído', 'Concluído'),
        ('Adiado', 'Adiado'),
    ]
    
    EVE_ID = models.AutoField(primary_key=True, verbose_name="ID")
    EVE_TITULO = models.CharField(
        max_length=100,
        verbose_name="Título do Evento",
        help_text="Digite o título do evento"
    )
    EVE_TIPO = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES,
        verbose_name="Tipo do Evento",
        help_text="Selecione o tipo do evento"
    )
    EVE_DESCRICAO = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Descrição",
        help_text="Descrição do evento"
    )
    EVE_DT_INICIAL = models.DateField(
        verbose_name="Data Inicial",
        help_text="Data inicial do evento"
    )
    EVE_DT_FINAL = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data Final",
        help_text="Data final do evento (opcional)"
    )
    EVE_HORA_INICIAL = models.TimeField(
        blank=True,
        null=True,
        verbose_name="Hora Inicial",
        help_text="Horário inicial do evento"
    )
    EVE_HORA_FINAL = models.TimeField(
        blank=True,
        null=True,
        verbose_name="Hora Final",
        help_text="Horário final do evento"
    )
    EVE_LOCAL = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Local",
        help_text="Local do evento"
    )
    EVE_ENDERECO = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Endereço",
        help_text="Endereço do evento"
    )
    EVE_RESPONSAVEL = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Responsável",
        help_text="Responsável pelo evento"
    )
    EVE_CELEBRANTE = models.ForeignKey(
        TBCELEBRANTES,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Celebrante",
        help_text="Celebrante do evento",
        related_name='eventos'
    )
    EVE_PARTICIPANTES = models.IntegerField(
        default=0,
        verbose_name="Participantes",
        help_text="Número de participantes esperados"
    )
    EVE_CONFIRMADOS = models.IntegerField(
        default=0,
        verbose_name="Confirmados",
        help_text="Número de participantes confirmados"
    )
    EVE_RECURSOS = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Recursos",
        help_text="Recursos necessários para o evento"
    )
    EVE_STATUS = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Ativo',
        verbose_name="Status",
        help_text="Status do evento"
    )
    EVE_DTCADASTRO = models.DateField(
        default=timezone.now,
        verbose_name="Data de Cadastro",
        help_text="Data de criação do evento"
    )
    EVE_DTATUALIZACAO = models.DateField(
        auto_now=True,
        verbose_name="Data de Atualização",
        help_text="Data da última atualização"
    )
    
    class Meta:
        db_table = 'TBEVENTO'
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-EVE_DTCADASTRO']
    
    def __str__(self):
        return self.EVE_TITULO
    
    @property
    def status_display(self):
        """Retorna o status formatado para exibição"""
        return dict(self.STATUS_CHOICES).get(self.EVE_STATUS, self.EVE_STATUS)
    
    @property
    def status_badge_class(self):
        """Retorna a classe CSS para o badge de status"""
        status_classes = {
            'Ativo': 'bg-success',
            'Inativo': 'bg-secondary',
            'Cancelado': 'bg-danger',
            'Concluído': 'bg-info',
            'Adiado': 'bg-warning',
        }
        return status_classes.get(self.EVE_STATUS, 'bg-secondary')


class TBITEM_EVENTO(models.Model):
    """
    Modelo para Itens do Evento
    Tabela filha de TBEVENTO
    """
    
    ITEM_EVE_ID = models.AutoField(primary_key=True, verbose_name="ID")
    ITEM_EVE_EVENTO = models.ForeignKey(
        TBEVENTO,
        on_delete=models.CASCADE,
        verbose_name="Evento",
        help_text="Evento ao qual este item pertence",
        related_name='itens'
    )
    ITEM_EVE_DATA_INICIAL = models.DateField(
        verbose_name="Data Inicial",
        help_text="Data inicial do item do evento"
    )
    ITEM_EVE_ACAO = models.CharField(
        max_length=100,
        verbose_name="Ação",
        help_text="Descrição da ação do item do evento"
    )
    ITEM_EVE_DATA_FINAL = models.DateField(
        verbose_name="Data Final",
        help_text="Data final do item do evento",
        blank=True,
        null=True,
        db_column='ITEM_EVE_DATA-FINAL'  # Nome no banco com hífen
    )
    ITEM_EVE_HORA_INICIAL = models.TimeField(
        verbose_name="Hora Inicial",
        help_text="Horário inicial do item do evento"
    )
    ITEM_EVE_HORA_FINAL = models.TimeField(
        verbose_name="Hora Final",
        help_text="Horário final do item do evento",
        blank=True,
        null=True
    )
    
    class Meta:
        db_table = 'TBITEM_EVENTO'
        verbose_name = 'Item do Evento'
        verbose_name_plural = 'Itens do Evento'
        ordering = ['ITEM_EVE_EVENTO', 'ITEM_EVE_DATA_INICIAL', 'ITEM_EVE_HORA_INICIAL']
    
    def __str__(self):
        return f"{self.ITEM_EVE_EVENTO.EVE_TITULO} - {self.ITEM_EVE_ACAO}"

