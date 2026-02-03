import io
import os
from django.db import models
from django.utils import timezone
from django.core.files.base import ContentFile
from PIL import Image

class TBMURAL(models.Model):
    """Modelo para Mural de Fotos com compressão automática."""

    MUR_ID = models.AutoField(primary_key=True, verbose_name="ID")
    MUR_data_mural = models.DateField(default=timezone.now, verbose_name="Data do Mural")
    MUR_titulo_mural = models.CharField(max_length=255, verbose_name="Título do Mural")
    
    # Fotos
    MUR_foto1_mural = models.ImageField(upload_to='mural/', blank=True, null=True, verbose_name="Foto 1")
    MUR_foto2_mural = models.ImageField(upload_to='mural/', blank=True, null=True, verbose_name="Foto 2")
    MUR_foto3_mural = models.ImageField(upload_to='mural/', blank=True, null=True, verbose_name="Foto 3")
    MUR_foto4_mural = models.ImageField(upload_to='mural/', blank=True, null=True, verbose_name="Foto 4")
    MUR_foto5_mural = models.ImageField(upload_to='mural/', blank=True, null=True, verbose_name="Foto 5")
    
    # Legendas
    MUR_legenda1_mural = models.CharField(max_length=255, blank=True, null=True, verbose_name="Legenda Foto 1")
    MUR_legenda2_mural = models.CharField(max_length=255, blank=True, null=True, verbose_name="Legenda Foto 2")
    MUR_legenda3_mural = models.CharField(max_length=255, blank=True, null=True, verbose_name="Legenda Foto 3")
    MUR_legenda4_mural = models.CharField(max_length=255, blank=True, null=True, verbose_name="Legenda Foto 4")
    MUR_legenda5_mural = models.CharField(max_length=255, blank=True, null=True, verbose_name="Legenda Foto 5")
    
    MUR_ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        db_table = 'TBMURAL'
        verbose_name = 'Mural'
        verbose_name_plural = 'Murais'
        ordering = ['-MUR_data_mural', 'MUR_titulo_mural']

    def __str__(self):
        return self.MUR_titulo_mural

    # --- AUXILIARES ---
    @property
    def status_display(self):
        return "Ativo" if self.MUR_ativo else "Inativo"

    def get_fotos_count(self):
        return sum(1 for f in [self.MUR_foto1_mural, self.MUR_foto2_mural, self.MUR_foto3_mural, self.MUR_foto4_mural, self.MUR_foto5_mural] if f)

    # --- O PENTE FINO: COMPRESSÃO EM MASSA ---
    def save(self, *args, **kwargs):
        """Processa as 5 fotos antes de salvar no Wasabi."""
        fotos = [
            'MUR_foto1_mural', 'MUR_foto2_mural', 'MUR_foto3_mural', 
            'MUR_foto4_mural', 'MUR_foto5_mural'
        ]

        for campo_nome in fotos:
            foto_campo = getattr(self, campo_nome)
            
            # Se a foto existe e não é apenas uma string (garante que é um arquivo novo)
            if foto_campo and not isinstance(foto_campo, str):
                try:
                    img = Image.open(foto_campo)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Para murais, 800px é o ideal para visualização em galeria
                    img.thumbnail((800, 800))
                    
                    buffer = io.BytesIO()
                    img.save(buffer, format='JPEG', quality=70, optimize=True)
                    buffer.seek(0)
                    
                    novo_nome = os.path.splitext(foto_campo.name)[0] + '.jpg'
                    # O save=False é vital para não entrar em loop infinito no save()
                    foto_campo.save(novo_nome, ContentFile(buffer.read()), save=False)
                except Exception as e:
                    print(f"Erro ao processar {campo_nome}: {e}")

        super(TBMURAL, self).save(*args, **kwargs)
