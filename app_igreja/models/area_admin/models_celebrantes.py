import io
import os
from django.db import models
from django.utils import timezone
from django.core.files.base import ContentFile
from PIL import Image

class TBCELEBRANTES(models.Model):
    """Celebrantes da igreja."""
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
        return str(self.CEL_nome_celebrante)

    # --- O REFORÇO ESTRATÉGICO: COMPRESSÃO DE FOTOS DE CELEBRANTES ---
    def save(self, *args, **kwargs):
        """Otimiza a foto do celebrante para não pesar no Wasabi/Carregamento."""
        if self.CEL_foto:
            try:
                img = Image.open(self.CEL_foto)
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Fotos de celebrantes costumam ser exibidas em círculos ou cards pequenos.
                # 600px é mais que o suficiente para manter a nitidez.
                output_size = (600, 600) 
                img.thumbnail(output_size)

                buffer = io.BytesIO()
                # Qualidade 75% para um equilíbrio perfeito entre peso e visão.
                img.save(buffer, format='JPEG', quality=75, optimize=True)
                buffer.seek(0)

                nome_arquivo = os.path.splitext(self.CEL_foto.name)[0] + '.jpg'
                self.CEL_foto.save(nome_arquivo, ContentFile(buffer.read()), save=False)
            except Exception as e:
                print(f"Erro na compressão do Celebrante: {e}")

        super(TBCELEBRANTES, self).save(*args, **kwargs)
