import io
import os
from django.db import models
from django.core.files.base import ContentFile
from PIL import Image

class TBBANNERS(models.Model):
    """Banners de patrocinadores."""

    BAN_NOME_PATROCINADOR = models.CharField(
        max_length=200,
        verbose_name="Nome do Patrocinador",
        help_text="Nome do patrocinador ou empresa"
    )
    BAN_DESCRICAO_COMERCIAL = models.CharField(
        max_length=255,
        verbose_name="Descrição Comercial",
        help_text="Breve descrição do negócio ou serviço",
        blank=True, null=True
    )
    BAN_IMAGE = models.ImageField(
        upload_to='banners/',
        verbose_name="Imagem do Banner",
        help_text="Imagem do banner do patrocinador"
    )
    BAN_LINK = models.CharField(
        max_length=255, # Aumentado de 50 para 255 para suportar URLs longas
        verbose_name="Link",
        help_text="URL do site do patrocinador",
        blank=True, null=True
    )
    BAN_TELEFONE = models.CharField(
        max_length=20,
        verbose_name="Telefone",
        help_text="Telefone de contato",
        blank=True, null=True
    )
    BAN_ENDERECO = models.CharField(
        max_length=255,
        verbose_name="Endereço",
        help_text="Endereço completo do patrocinador",
        blank=True, null=True
    )
    BAN_ORDEM = models.IntegerField(
        verbose_name="Ordem",
        default=0,
        help_text="Ordem de exibição. Se for 0 (zero), o banner está inativo."
    )
    BAN_data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    BAN_data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Atualização"
    )

    class Meta:
        db_table = 'TBBANNERS'
        verbose_name = "Banner de Patrocinador"
        verbose_name_plural = "Banners de Patrocinadores"
        ordering = ['BAN_ORDEM', 'BAN_NOME_PATROCINADOR']

    def __str__(self):
        return f"{self.BAN_NOME_PATROCINADOR} (Ordem: {self.BAN_ORDEM})"

    def is_ativo(self):
        return self.BAN_ORDEM > 0

    def get_status_display(self):
        return "Ativo" if self.is_ativo() else "Inativo"

    def get_status_class(self):
        return "success" if self.is_ativo() else "secondary"

    def get_image_url(self):
        if self.BAN_IMAGE:
            return self.BAN_IMAGE.url
        return "/static/img/default-banner.png"

    # --- O REFORÇO ESTRATÉGICO: COMPRESSÃO DE BANNERS ---
    def save(self, *args, **kwargs):
        """Otimiza a imagem do patrocinador antes de enviar ao Wasabi."""
        if self.BAN_IMAGE:
            try:
                img = Image.open(self.BAN_IMAGE)
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Banners geralmente são largos (landscape). 
                # Vamos limitar a 1200px de largura para manter a qualidade em telas grandes
                output_size = (1200, 1200) 
                img.thumbnail(output_size)

                buffer = io.BytesIO()
                # Qualidade 80% para banners, pois eles precisam ter boa nitidez visual
                img.save(buffer, format='JPEG', quality=80, optimize=True)
                buffer.seek(0)

                nome_arquivo = os.path.splitext(self.BAN_IMAGE.name)[0] + '.jpg'
                self.BAN_IMAGE.save(nome_arquivo, ContentFile(buffer.read()), save=False)
            except Exception as e:
                print(f"Erro na compressão do Banner: {e}")

        super(TBBANNERS, self).save(*args, **kwargs)
