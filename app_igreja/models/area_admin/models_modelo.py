from django.db import models
from django.utils import timezone


class TBMODELO(models.Model):
    MOD_ID = models.AutoField(primary_key=True, verbose_name="ID")
    MOD_DESCRICAO = models.CharField(max_length=100, verbose_name="Descrição do Modelo")
    MOD_DATA_CRIACAO = models.DateField(default=timezone.now, verbose_name="Data de Criação")
    MOD_DATA_ALTERACAO = models.DateField(auto_now=True, verbose_name="Data de Alteração")

    class Meta:
        db_table = 'TBMODELO'
        verbose_name = 'Modelo'
        verbose_name_plural = 'Modelos'
        ordering = ['MOD_DESCRICAO']

    def __str__(self):
        return self.MOD_DESCRICAO


class TBITEM_MODELO(models.Model):
    ITEM_MOD_ID = models.AutoField(primary_key=True, verbose_name="ID")
    ITEM_MOD_MODELO = models.ForeignKey(
        TBMODELO,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Modelo'
    )
    ITEM_MOD_ENCARGO = models.CharField(max_length=100, verbose_name='Encargo')
    ITEM_MOD_OCORRENCIA = models.CharField(max_length=100, verbose_name='Ocorrências')

    class Meta:
        db_table = 'TBITEM_MODELO'
        verbose_name = 'Item do Modelo'
        verbose_name_plural = 'Itens do Modelo'
        ordering = ['ITEM_MOD_MODELO', 'ITEM_MOD_ID']

    def __str__(self):
        return f"{self.ITEM_MOD_MODELO.MOD_DESCRICAO} - {self.ITEM_MOD_ENCARGO}"

    def ocorrencias_list(self):
        return [valor for valor in (self.ITEM_MOD_OCORRENCIA or '').split(',') if valor]

    @property
    def ocorrencias_verbose_list(self):
        return [OCORRENCIA_DICT.get(valor, valor) for valor in self.ocorrencias_list()]

    @property
    def ocorrencias_display(self):
        ocorrencias = self.ocorrencias_verbose_list
        return ', '.join(ocorrencias)

OCORRENCIA_CHOICES = [
    ('todos', 'Todos os dias'),
    ('domingo', 'Domingo'),
    ('segunda', 'Segunda-feira'),
    ('terca', 'Terça-feira'),
    ('quarta', 'Quarta-feira'),
    ('quinta', 'Quinta-feira'),
    ('sexta', 'Sexta-feira'),
    ('sabado', 'Sábado'),
]
OCORRENCIA_DICT = dict(OCORRENCIA_CHOICES)
