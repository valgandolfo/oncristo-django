from django.db import models
from django.utils import timezone


class TBMURAL(models.Model):
    """
    Modelo para Mural de Fotos
    """
    
    MUR_ID = models.AutoField(primary_key=True, verbose_name="ID")
    MUR_data_mural = models.DateField(
        default=timezone.now,
        verbose_name="Data do Mural",
        help_text="Data de publicação do mural"
    )
    MUR_titulo_mural = models.CharField(
        max_length=255,
        verbose_name="Título do Mural",
        help_text="Digite o título do mural"
    )
    
    # Fotos do Mural
    MUR_foto1_mural = models.ImageField(
        upload_to='mural/',
        blank=True,
        null=True,
        verbose_name="Foto 1",
        help_text="Primeira foto do mural"
    )
    MUR_foto2_mural = models.ImageField(
        upload_to='mural/',
        blank=True,
        null=True,
        verbose_name="Foto 2",
        help_text="Segunda foto do mural"
    )
    MUR_foto3_mural = models.ImageField(
        upload_to='mural/',
        blank=True,
        null=True,
        verbose_name="Foto 3",
        help_text="Terceira foto do mural"
    )
    MUR_foto4_mural = models.ImageField(
        upload_to='mural/',
        blank=True,
        null=True,
        verbose_name="Foto 4",
        help_text="Quarta foto do mural"
    )
    MUR_foto5_mural = models.ImageField(
        upload_to='mural/',
        blank=True,
        null=True,
        verbose_name="Foto 5",
        help_text="Quinta foto do mural"
    )
    
    # Legendas das Fotos
    MUR_legenda1_mural = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Legenda Foto 1",
        help_text="Legenda para a primeira foto"
    )
    MUR_legenda2_mural = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Legenda Foto 2",
        help_text="Legenda para a segunda foto"
    )
    MUR_legenda3_mural = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Legenda Foto 3",
        help_text="Legenda para a terceira foto"
    )
    MUR_legenda4_mural = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Legenda Foto 4",
        help_text="Legenda para a quarta foto"
    )
    MUR_legenda5_mural = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Legenda Foto 5",
        help_text="Legenda para a quinta foto"
    )
    
    MUR_ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Indica se o mural está ativo"
    )
    
    class Meta:
        db_table = 'TBMURAL'
        verbose_name = 'Mural'
        verbose_name_plural = 'Murais'
        ordering = ['-MUR_data_mural', 'MUR_titulo_mural']
    
    def __str__(self):
        return self.MUR_titulo_mural
    
    @property
    def status_display(self):
        """Retorna o status formatado para exibição"""
        return "Ativo" if self.MUR_ativo else "Inativo"
    
    @property
    def status_badge_class(self):
        """Retorna a classe CSS para o badge de status"""
        return "bg-success" if self.MUR_ativo else "bg-danger"
    
    def get_fotos_count(self):
        """Retorna o número de fotos cadastradas"""
        count = 0
        if self.MUR_foto1_mural:
            count += 1
        if self.MUR_foto2_mural:
            count += 1
        if self.MUR_foto3_mural:
            count += 1
        if self.MUR_foto4_mural:
            count += 1
        if self.MUR_foto5_mural:
            count += 1
        return count
    
    def get_legendas_count(self):
        """Retorna o número de legendas cadastradas"""
        count = 0
        if self.MUR_legenda1_mural:
            count += 1
        if self.MUR_legenda2_mural:
            count += 1
        if self.MUR_legenda3_mural:
            count += 1
        if self.MUR_legenda4_mural:
            count += 1
        if self.MUR_legenda5_mural:
            count += 1
        return count

