from django.db import models
from django.utils import timezone

class TBLITURGIA(models.Model):
    """
    Modelo para cadastro de Liturgias
    """
    
    TIPO_LITURGIA_CHOICES = [
        ('Primeira Leitura', 'Primeira Leitura'),
        ('Segunda Leitura', 'Segunda Leitura'),
        ('Salmo Responsorial', 'Salmo Responsorial'),
        ('Evangelho', 'Evangelho'),
        ('Oração do Dia', 'Oração do Dia'),
        ('Outras', 'Outras'),
    ]
    
    LIT_id = models.AutoField(primary_key=True, verbose_name="ID")
    LIT_DATALIT = models.DateField(verbose_name="Data da Liturgia", db_index=True)
    LIT_TIPOLIT = models.CharField(
        max_length=50, 
        verbose_name="Tipo de Liturgia",
        choices=TIPO_LITURGIA_CHOICES
    )
    LIT_TEXTO = models.TextField(verbose_name="Texto da Liturgia")
    LIT_STATUSLIT = models.BooleanField(default=True, verbose_name="Status da Liturgia")
    LIT_DATA_CADASTRO = models.DateTimeField(default=timezone.now, verbose_name="Data de Cadastro")
    LIT_DATA_ATUALIZACAO = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        db_table = 'TBLITURGIA'
        verbose_name = 'Liturgia'
        verbose_name_plural = 'Liturgias'
        ordering = ['-LIT_DATALIT', 'LIT_TIPOLIT']
    
    def __str__(self):
        return f"{self.LIT_TIPOLIT} - {self.LIT_DATALIT}"
