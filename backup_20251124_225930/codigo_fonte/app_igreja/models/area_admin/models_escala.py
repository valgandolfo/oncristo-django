from django.db import models
from django.utils import timezone


class TBESCALA(models.Model):
    """
    Modelo Master para Escala Mensal de Missas
    Tabela: TBESCALA
    Prefixo: ESC_
    Chave Primária: ESC_MESANO (Mês/Ano)
    O modelo não é gravado, é apenas usado para gerar a escala
    """
    
    ESC_MESANO = models.DateField(
        primary_key=True,
        verbose_name="Mês/Ano",
        help_text="Mês e ano da escala (ex: 01/01/2026 para Janeiro/2026). Chave primária."
    )
    ESC_TEMAMES = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Tema do Mês",
        help_text="Tema do mês para a escala"
    )
    
    class Meta:
        db_table = 'TBESCALA'
        verbose_name = "Escala Mensal"
        verbose_name_plural = "Escalas Mensais"
        ordering = ['-ESC_MESANO']
    
    def __str__(self):
        meses_pt = [
            '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        mes_nome = meses_pt[self.ESC_MESANO.month] if self.ESC_MESANO else ''
        ano = self.ESC_MESANO.year if self.ESC_MESANO else ''
        return f"{mes_nome}/{ano}"
    
    @property
    def id(self):
        """Retorna ESC_MESANO como id para compatibilidade"""
        return self.ESC_MESANO


class TBITEM_ESCALA(models.Model):
    """
    Modelo Detail para Itens da Escala Mensal de Missas
    Tabela: TBITEM_ESCALA
    Prefixo: ITE_ESC_
    """
    
    ITE_ESC_ID = models.AutoField(primary_key=True, verbose_name="ID")
    ITE_ESC_ESCALA = models.ForeignKey(
        TBESCALA,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name="Escala"
    )
    ITE_ESC_DATA = models.DateField(
        verbose_name="Data",
        help_text="Data da missa"
    )
    ITE_ESC_HORARIO = models.TimeField(
        verbose_name="Horário",
        help_text="Horário da missa"
    )
    ITE_ESC_DESCRICAO = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Descrição",
        help_text="Descrição do item"
    )
    ITE_ESC_ENCARGO = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Encargo",
        help_text="Descrição do encargo (do modelo)"
    )
    ITE_ESC_STATUS = models.CharField(
        max_length=20,
        choices=[
            ('DEFINIDO', 'Definido'),
            ('EM_ABERTO', 'Em aberto'),
        ],
        default='EM_ABERTO',
        verbose_name="Status",
        help_text="Status do item da escala"
    )
    ITE_ESC_COLABORADOR = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Colaborador",
        help_text="ID do colaborador (será implementado depois)"
    )
    ITE_ESC_GRUPO = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Grupo",
        help_text="ID do grupo (será implementado depois)"
    )
    
    class Meta:
        db_table = 'TBITEM_ESCALA'
        verbose_name = "Item da Escala"
        verbose_name_plural = "Itens da Escala"
        ordering = ['ITE_ESC_DATA', 'ITE_ESC_HORARIO']
    
    def __str__(self):
        return f"{self.ITE_ESC_DATA.strftime('%d/%m/%Y')} - {self.ITE_ESC_HORARIO.strftime('%H:%M')} - {self.ITE_ESC_DESCRICAO or ''}"
    
    @property
    def id(self):
        return self.ITE_ESC_ID
