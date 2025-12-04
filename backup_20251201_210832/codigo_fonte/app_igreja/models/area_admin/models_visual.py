from django.db import models


class TBVISUAL(models.Model):
    """
    Modelo para Configurações Visuais - Sistema Single-Record
    Armazena as imagens principais do site (capa, brasão, padroeiro, principal)
    """
    
    VIS_ID = models.AutoField(primary_key=True, verbose_name="ID")
    
    # Campos de imagem
    VIS_FOTO_CAPA = models.ImageField(
        upload_to='visual/capa/',
        verbose_name="Foto de Capa",
        blank=True,
        null=True,
        help_text="Imagem de capa do site"
    )
    
    VIS_FOTO_BRASAO = models.ImageField(
        upload_to='visual/brasao/',
        verbose_name="Foto do Brasão",
        blank=True,
        null=True,
        help_text="Brasão da paróquia/diocese"
    )
    
    VIS_FOTO_PADROEIRO = models.ImageField(
        upload_to='visual/padroeiro/',
        verbose_name="Foto do Padroeiro",
        blank=True,
        null=True,
        help_text="Imagem do padroeiro"
    )
    
    VIS_FOTO_PRINCIPAL = models.ImageField(
        upload_to='visual/principal/',
        verbose_name="Foto Principal",
        blank=True,
        null=True,
        help_text="Imagem principal do site"
    )
    
    class Meta:
        db_table = 'TBVISUAL'
        verbose_name = 'Configuração Visual'
        verbose_name_plural = 'Configurações Visuais'
    
    def __str__(self):
        return 'Configurações Visuais'

