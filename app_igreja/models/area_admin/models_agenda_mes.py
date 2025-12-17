"""
==================== MODELO AGENDA DO MÊS ====================
Modelo para armazenar agenda mensal com estrutura master-detail
"""

from django.db import models
from django.utils import timezone


class TBAGENDAMES(models.Model):
    """
    Modelo Master para Agenda do Mês
    """
    AGE_ID = models.AutoField(primary_key=True, verbose_name="ID")
    AGE_MES = models.DateField(verbose_name="Mês", unique=True, help_text="Data do primeiro dia do mês")

    class Meta:
        db_table = 'TBAGENDAMES'
        verbose_name = 'Agenda do Mês'
        verbose_name_plural = 'Agendas do Mês'
        ordering = ['-AGE_MES']

    def __str__(self):
        return f"Agenda - {self.AGE_MES.strftime('%m/%Y')}"


class TBITEAGENDAMES(models.Model):
    """
    Modelo Detail para Itens da Agenda do Mês
    """
    AGE_ITE_ID = models.AutoField(primary_key=True, verbose_name="ID")
    AGE_ITE_MES = models.ForeignKey(
        TBAGENDAMES,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Agenda do Mês',
        db_column='AGE_ITE_MES'
    )
    AGE_ITE_DIA = models.IntegerField(verbose_name="Dia", help_text="Dia do mês (1-31)")
    AGE_ITE_MODELO = models.IntegerField(
        verbose_name="Modelo",
        null=True,
        blank=True,
        help_text="ID do modelo selecionado"
    )
    AGE_ITE_ENCARGOS = models.TextField(
        verbose_name="Encargos",
        blank=True,
        null=True,
        help_text="Encargos do dia"
    )
    AGE_ITE_DATA_CRIACAO = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    AGE_ITE_DATA_ATUALIZACAO = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")

    class Meta:
        db_table = 'TBITEAGENDAMES'
        verbose_name = 'Item da Agenda do Mês'
        verbose_name_plural = 'Itens da Agenda do Mês'
        unique_together = [['AGE_ITE_MES', 'AGE_ITE_DIA']]  # Um registro por dia/mês
        ordering = ['AGE_ITE_MES', 'AGE_ITE_DIA']

    def __str__(self):
        from ...models.area_admin.models_modelo import TBMODELO
        modelo_nome = "Sem modelo"
        if self.AGE_ITE_MODELO:
            try:
                modelo_obj = TBMODELO.objects.get(pk=self.AGE_ITE_MODELO)
                modelo_nome = modelo_obj.MOD_DESCRICAO
            except TBMODELO.DoesNotExist:
                pass
        return f"Dia {self.AGE_ITE_DIA} - {modelo_nome}"
