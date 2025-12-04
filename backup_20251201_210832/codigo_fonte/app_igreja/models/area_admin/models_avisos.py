from django.db import models
from django.utils import timezone

class TBAVISO(models.Model):
    AVI_id = models.AutoField(primary_key=True, verbose_name="ID")
    AVI_titulo = models.CharField(max_length=255, verbose_name="Título do Aviso")
    AVI_texto = models.CharField(max_length=255, verbose_name="Texto do Aviso")
    AVI_data = models.DateField(default=timezone.now, verbose_name="Data Cadastro Aviso")
    
    class Meta:
        db_table = 'TBAVISO'
        verbose_name = 'Aviso'
        verbose_name_plural = 'Avisos'
        ordering = ['-AVI_data', 'AVI_titulo']
    
    def __str__(self):
        return self.AVI_titulo
