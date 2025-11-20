from django.db import models
from django.utils import timezone


class TBPLANO(models.Model):
    """
    Modelo para Planos de Ação
    """
    
    PLA_id = models.AutoField(primary_key=True, verbose_name="ID")
    PLA_titulo_plano = models.CharField(
        max_length=50,
        verbose_name="Título do Plano",
        help_text="Digite o título do plano de ação"
    )
    PLA_data_cadastro = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data de Cadastro",
        help_text="Data de criação do plano"
    )
    PLA_data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Atualização",
        help_text="Data da última atualização"
    )
    PLA_ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Indica se o plano está ativo"
    )
    
    class Meta:
        db_table = 'TBPLANO'
        verbose_name = 'Plano de Ação'
        verbose_name_plural = 'Planos de Ação'
        ordering = ['-PLA_data_cadastro']
    
    def __str__(self):
        return self.PLA_titulo_plano
    
    @property
    def status_display(self):
        """Retorna o status formatado para exibição"""
        return "Ativo" if self.PLA_ativo else "Inativo"
    
    @property
    def status_badge_class(self):
        """Retorna a classe CSS para o badge de status"""
        return "bg-success" if self.PLA_ativo else "bg-danger"


class TBITEMPLANO(models.Model):
    """
    Modelo para Itens do Plano de Ação
    Tabela filha de TBPLANO
    """
    
    ITEM_PLANO_ID = models.AutoField(primary_key=True, verbose_name="ID")
    ITEM_PLANO_PLANO = models.ForeignKey(
        TBPLANO,
        on_delete=models.CASCADE,
        verbose_name="Plano",
        help_text="Plano de ação ao qual este item pertence",
        related_name='itens'
    )
    ITEM_HORA_PLANO = models.TimeField(
        verbose_name="Hora do Plano",
        help_text="Horário para execução da ação"
    )
    ITEM_ACAO_PLANO = models.CharField(
        max_length=100,
        verbose_name="Ação do Plano",
        help_text="Descrição da ação a ser executada"
    )
    
    class Meta:
        db_table = 'TBITEMPLANO'
        verbose_name = 'Item do Plano'
        verbose_name_plural = 'Itens do Plano'
        ordering = ['ITEM_PLANO_PLANO', 'ITEM_HORA_PLANO']
    
    def __str__(self):
        return f"{self.ITEM_PLANO_PLANO.PLA_titulo_plano} - {self.ITEM_HORA_PLANO} - {self.ITEM_ACAO_PLANO}"
