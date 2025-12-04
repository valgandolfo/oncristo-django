from django.db import models
from django.utils import timezone

class TBCELEBRANTES(models.Model):
    """
    Tabela de Celebrantes - Define os celebrantes da igreja
    """
    CEL_id = models.AutoField(primary_key=True, verbose_name="ID do Celebrante")
    CEL_nome_celebrante = models.CharField(max_length=255, verbose_name="Nome do Celebrante")
    CEL_ordenacao = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ordenação")
    CEL_foto = models.ImageField(upload_to='celebrantes/', blank=True, null=True, verbose_name="Foto")
    CEL_ativo = models.BooleanField(default=True, verbose_name="Ativo")
    CEL_data_cadastro = models.DateTimeField(default=timezone.now, verbose_name="Data de Cadastro")
    CEL_data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        db_table = 'TBCELEBRANTES'
        verbose_name = 'Celebrante'
        verbose_name_plural = 'Celebrantes'
        ordering = ['CEL_ordenacao', 'CEL_nome_celebrante']
    
    def __str__(self):
        return f"{self.CEL_nome_celebrante}"
    
    def save(self, *args, **kwargs):
        """Override save para atualizar CEL_data_atualizacao"""
        self.CEL_data_atualizacao = timezone.now()
        super().save(*args, **kwargs)
