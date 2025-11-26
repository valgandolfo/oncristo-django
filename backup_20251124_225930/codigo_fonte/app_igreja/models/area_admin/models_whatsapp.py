from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class TBWHATSAPP(models.Model):
    """
    Modelo para armazenar mensagens enviadas via WhatsApp
    """
    
    TIPO_DESTINATARIO_CHOICES = [
        ('DIZIMISTAS', 'Dizimistas'),
        ('COLABORADORES', 'Colaboradores'),
        ('TODOS', 'Todos'),
    ]
    
    TIPO_MIDIA_CHOICES = [
        ('TEXTO', 'Texto'),
        ('IMAGEM', 'Imagem'),
        ('AUDIO', 'Áudio'),
        ('VIDEO', 'Vídeo'),
    ]
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('ENVIADA', 'Enviada'),
        ('ENTREGUE', 'Entregue'),
        ('LIDA', 'Lida'),
        ('ERRO', 'Erro'),
    ]
    
    # Campos principais
    WHA_id = models.AutoField(primary_key=True, verbose_name="ID")
    WHA_texto = models.TextField(verbose_name="Texto da Mensagem", blank=True, null=True)
    WHA_destinatario_tipo = models.CharField(
        max_length=20, 
        verbose_name="Tipo de Destinatário",
        choices=TIPO_DESTINATARIO_CHOICES,
        default='DIZIMISTAS'
    )
    WHA_tipo_midia = models.CharField(
        max_length=20,
        verbose_name="Tipo de Mídia",
        choices=TIPO_MIDIA_CHOICES,
        default='TEXTO'
    )
    
    # Campos de mídia
    WHA_url_imagem = models.URLField(verbose_name="URL da Imagem", blank=True, null=True)
    WHA_legenda_imagem = models.TextField(verbose_name="Legenda da Imagem", blank=True, null=True)
    WHA_url_audio = models.URLField(verbose_name="URL do Áudio", blank=True, null=True)
    WHA_url_video = models.URLField(verbose_name="URL do Vídeo", blank=True, null=True)
    WHA_legenda_video = models.TextField(verbose_name="Legenda do Vídeo", blank=True, null=True)
    
    # Estatísticas
    WHA_total_enviadas = models.IntegerField(default=0, verbose_name="Total Enviadas")
    WHA_sucessos = models.IntegerField(default=0, verbose_name="Sucessos")
    WHA_erros = models.IntegerField(default=0, verbose_name="Erros")
    
    # Status e controle
    WHA_status = models.CharField(
        max_length=20,
        verbose_name="Status",
        choices=STATUS_CHOICES,
        default='PENDENTE'
    )
    WHA_usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuário"
    )
    WHA_erro = models.TextField(verbose_name="Erro", blank=True, null=True)
    WHA_api_response = models.TextField(verbose_name="Resposta da API", blank=True, null=True)
    
    # Datas
    WHA_data_criacao = models.DateTimeField(default=timezone.now, verbose_name="Data de Criação")
    WHA_data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        db_table = 'TBWHATSAPP'
        verbose_name = 'Mensagem WhatsApp'
        verbose_name_plural = 'Mensagens WhatsApp'
        ordering = ['-WHA_data_criacao']
    
    def __str__(self):
        return f"Mensagem {self.WHA_id} - {self.get_WHA_destinatario_tipo_display()} - {self.WHA_data_criacao.strftime('%d/%m/%Y %H:%M')}"
    
    def get_status_class(self):
        """Retorna classe CSS para o status"""
        status_classes = {
            'PENDENTE': 'warning',
            'ENVIADA': 'info',
            'ENTREGUE': 'primary',
            'LIDA': 'success',
            'ERRO': 'danger',
        }
        return status_classes.get(self.WHA_status, 'secondary')
    
    def get_WHA_destinatario_tipo_display(self):
        """Retorna o display do tipo de destinatário"""
        tipos_dict = dict(self.TIPO_DESTINATARIO_CHOICES)
        return tipos_dict.get(self.WHA_destinatario_tipo, self.WHA_destinatario_tipo)
    
    def get_WHA_tipo_midia_display(self):
        """Retorna o display do tipo de mídia"""
        tipos_dict = dict(self.TIPO_MIDIA_CHOICES)
        return tipos_dict.get(self.WHA_tipo_midia, self.WHA_tipo_midia)
    
    def get_WHA_status_display(self):
        """Retorna o display do status"""
        status_dict = dict(self.STATUS_CHOICES)
        return status_dict.get(self.WHA_status, self.WHA_status)

