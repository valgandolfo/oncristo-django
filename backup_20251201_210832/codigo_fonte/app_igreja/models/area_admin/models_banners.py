"""
==================== MODELOS DE BANNERS ====================
Arquivo com modelos para Banners de Patrocinadores
"""

from django.db import models
from django.utils import timezone


class TBBANNERS(models.Model):
    """Modelo para cadastro de Banners de Patrocinadores"""
    
    # Campos obrigatórios
    BAN_NOME_PATROCINADOR = models.CharField(
        max_length=200,
        verbose_name="Nome do Patrocinador",
        help_text="Nome do patrocinador ou empresa"
    )
    BAN_DESCRICAO_COMERCIAL = models.CharField(
        max_length=255,
        verbose_name="Descrição Comercial",
        help_text="Breve descrição do negócio ou serviço",
        blank=True,
        null=True
    )
    BAN_IMAGE = models.ImageField(
        upload_to='banners/',
        verbose_name="Imagem do Banner",
        help_text="Imagem do banner do patrocinador"
    )
    BAN_LINK = models.CharField(
        max_length=50,
        verbose_name="Link",
        help_text="URL do site do patrocinador (máximo 50 caracteres)",
        blank=True,
        null=True
    )
    BAN_TELEFONE = models.CharField(
        max_length=20,
        verbose_name="Telefone",
        help_text="Telefone de contato",
        blank=True,
        null=True
    )
    BAN_ENDERECO = models.CharField(
        max_length=255,
        verbose_name="Endereço",
        help_text="Endereço completo do patrocinador",
        blank=True,
        null=True
    )
    BAN_ORDEM = models.IntegerField(
        verbose_name="Ordem",
        default=0,
        help_text="Ordem de exibição. Se for 0 (zero), o banner está inativo."
    )
    
    # Datas
    BAN_data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    BAN_data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Atualização"
    )
    
    def __str__(self):
        return f"{self.BAN_NOME_PATROCINADOR} (Ordem: {self.BAN_ORDEM})"
    
    class Meta:
        verbose_name = "Banner de Patrocinador"
        verbose_name_plural = "Banners de Patrocinadores"
        db_table = 'TBBANNERS'
        ordering = ['BAN_ORDEM', 'BAN_NOME_PATROCINADOR']
    
    def is_ativo(self):
        """Verifica se o banner está ativo (ordem > 0)"""
        return self.BAN_ORDEM > 0
    
    def get_status_display(self):
        """Retorna o status formatado"""
        return "Ativo" if self.is_ativo() else "Inativo"
    
    def get_status_class(self):
        """Retorna a classe CSS para o status"""
        return "success" if self.is_ativo() else "secondary"
    
    def get_image_url(self):
        """Retorna a URL da imagem ou uma imagem padrão"""
        if self.BAN_IMAGE:
            return self.BAN_IMAGE.url
        return "/static/img/default-banner.png"
