import io
import os
from django.db import models
from django.core.files.base import ContentFile
from PIL import Image

class TBVISUAL(models.Model):
    """Configurações visuais do site (capa, brasão, padroeiro, principal)."""

    VIS_ID = models.AutoField(primary_key=True, verbose_name="ID")
    VIS_FOTO_CAPA = models.ImageField(
        upload_to='visual/capa/',
        verbose_name="Foto de Capa", blank=True, null=True,
        help_text="Imagem de capa do site"
    )
    VIS_FOTO_BRASAO = models.ImageField(
        upload_to='visual/brasao/',
        verbose_name="Foto do Brasão", blank=True, null=True,
        help_text="Brasão da paróquia/diocese"
    )
    VIS_FOTO_PADROEIRO = models.ImageField(
        upload_to='visual/padroeiro/',
        verbose_name="Foto do Padroeiro", blank=True, null=True,
        help_text="Imagem do padroeiro"
    )
    VIS_FOTO_PRINCIPAL = models.ImageField(
        upload_to='visual/principal/',
        verbose_name="Foto Principal", blank=True, null=True,
        help_text="Imagem principal do site"
    )

    class Meta:
        db_table = 'TBVISUAL'
        verbose_name = 'Configuração Visual'
        verbose_name_plural = 'Configurações Visuais'

    def __str__(self):
        return 'Configurações Visuais'

    # --- O TOQUE FINAL: OTIMIZAÇÃO DE IDENTIDADE VISUAL ---
    def save(self, *args, **kwargs):
        """Processa as imagens de identidade visual com alta fidelidade."""
        campos_imagem = [
            'VIS_FOTO_CAPA', 'VIS_FOTO_BRASAO', 
            'VIS_FOTO_PADROEIRO', 'VIS_FOTO_PRINCIPAL'
        ]

        for campo_nome in campos_imagem:
            imagem = getattr(self, campo_nome)
            
            # Só processa se for um arquivo novo sendo enviado
            if imagem and not isinstance(imagem, str):
                try:
                    img = Image.open(imagem)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Capas e fotos principais precisam de resolução (1600px largura)
                    # Brasões e Padroeiros podem ser menores (800px)
                    if campo_nome in ['VIS_FOTO_CAPA', 'VIS_FOTO_PRINCIPAL']:
                        img.thumbnail((1600, 1600))
                    else:
                        img.thumbnail((800, 800))
                    
                    buffer = io.BytesIO()
                    # Qualidade maior (85%) para não deformar o Brasão ou a Capa
                    img.save(buffer, format='JPEG', quality=85, optimize=True)
                    buffer.seek(0)
                    
                    nome_limpo = os.path.splitext(imagem.name)[0] + '.jpg'
                    imagem.save(nome_limpo, ContentFile(buffer.read()), save=False)
                except Exception as e:
                    print(f"Erro ao otimizar visual {campo_nome}: {e}")

        super(TBVISUAL, self).save(*args, **kwargs)
