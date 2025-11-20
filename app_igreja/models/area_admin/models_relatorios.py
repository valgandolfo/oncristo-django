from django.db import models
from django.utils import timezone


# ==================== MODELOS DE RELATÓRIOS ====================
# Este arquivo conterá todos os modelos relacionados a relatórios da igreja
# Campos com prefixo REL_

class TBRELATORIO(models.Model):
    """
    Modelo para a tabela TBRELATORIO
    Representa os relatórios da igreja
    """
    REL_id = models.AutoField(primary_key=True)
    REL_nome = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome do Relatório")
    REL_tipo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tipo")
    REL_descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    REL_parametros_json = models.TextField(blank=True, null=True, verbose_name="Parâmetros (JSON)")
    REL_data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    REL_data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")

    class Meta:
        db_table = 'TBRELATORIO'
        verbose_name = 'Relatório'
        verbose_name_plural = 'Relatórios'
        ordering = ['REL_nome']

    def __str__(self):
        return self.REL_nome or f'Relatório ID: {self.REL_id}'


# Adicione aqui outros modelos relacionados a relatórios conforme necessário
# Exemplo: TBRELATORIO_DIOCESE, TBRELATORIO_PAROQUIA, etc.
