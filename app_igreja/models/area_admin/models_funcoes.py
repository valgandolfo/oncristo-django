from django.db import models

class TBFUNCAO(models.Model):
    """
    Tabela de Funções - Define as funções/cargos da igreja
    """
    FUN_id = models.AutoField(primary_key=True, verbose_name="ID da Função")
    FUN_nome_funcao = models.CharField(max_length=255, verbose_name="Nome da Função")

    class Meta:
        db_table = 'TBFUNCAO'
        verbose_name = 'Função'
        verbose_name_plural = 'Funções'
        ordering = ['FUN_nome_funcao']

    def __str__(self):
        return self.FUN_nome_funcao