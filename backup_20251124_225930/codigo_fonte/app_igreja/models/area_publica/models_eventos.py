from django.db import models
from django.utils import timezone


# ==================== MODELOS DE EVENTOS ====================
# Este arquivo conterá todos os modelos relacionados a eventos da igreja
# Campos com prefixo EVE_

class TBEVENTO(models.Model):
    """
    Modelo para a tabela TBEVENTO
    Representa os eventos da igreja
    """
    EVE_id = models.AutoField(primary_key=True)
    EVE_nome = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome do Evento")
    EVE_descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    EVE_data_inicio = models.DateTimeField(blank=True, null=True, verbose_name="Data de Início")
    EVE_data_fim = models.DateTimeField(blank=True, null=True, verbose_name="Data de Fim")
    EVE_local = models.CharField(max_length=255, blank=True, null=True, verbose_name="Local")
    EVE_data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    EVE_data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")

    class Meta:
        db_table = 'TBEVENTO'
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['EVE_data_inicio']

    def __str__(self):
        return self.EVE_nome or f'Evento ID: {self.EVE_id}'


# Adicione aqui outros modelos relacionados a eventos conforme necessário
# Exemplo: TBMISSA, TBCELEBRACAO, TBFESTA, etc.
