import json
import io
import os
from django.db import models
from django.utils import timezone
from django.core.files.base import ContentFile
from PIL import Image

from .models_dioceses import TBDIOCESE
from ...utils import TIPOS_PIX

DIAS_DISPLAY = {
    'domingo': 'Domingo', 'segunda': 'Segunda-feira', 'terca': 'Terça-feira',
    'quarta': 'Quarta-feira', 'quinta': 'Quinta-feira', 'sexta': 'Sexta-feira', 'sabado': 'Sábado'
}

class TBPAROQUIA(models.Model):
    """Paróquia (registro único)."""
    PAR_nome_paroquia = models.CharField(max_length=255, verbose_name="Nome da Paróquia", null=True, blank=True)
    PAR_diocese = models.ForeignKey(TBDIOCESE, on_delete=models.CASCADE, verbose_name="Diocese", blank=True, null=True)
    PAR_cep = models.CharField(max_length=10, verbose_name="CEP", blank=True, null=True)
    PAR_endereco = models.TextField(verbose_name="Endereço", blank=True, null=True)
    PAR_numero = models.CharField(max_length=10, verbose_name="Número", blank=True, null=True)
    PAR_cidade = models.CharField(max_length=100, verbose_name="Cidade", blank=True, null=True)
    PAR_uf = models.CharField(max_length=2, verbose_name="UF", blank=True, null=True)
    PAR_bairro = models.CharField(max_length=100, verbose_name="Bairro", blank=True, null=True)
    PAR_telefone = models.CharField(max_length=20, verbose_name="Telefone", blank=True, null=True)
    PAR_email = models.EmailField(verbose_name="E-mail", blank=True, null=True)
    PAR_paroco = models.CharField(max_length=255, verbose_name="Pároco", blank=True, null=True)
    PAR_foto_paroco = models.ImageField(upload_to='parocos/', verbose_name="Foto do Pároco", blank=True, null=True)
    PAR_secretario = models.CharField(max_length=255, verbose_name="Secretário(a)", blank=True, null=True)
    PAR_cnpj = models.CharField(max_length=18, verbose_name="CNPJ", blank=True, null=True)
    PAR_banco = models.CharField(max_length=100, verbose_name="Banco", blank=True, null=True)
    PAR_agencia = models.CharField(max_length=20, verbose_name="Agência", blank=True, null=True)
    PAR_conta = models.CharField(max_length=20, verbose_name="Conta", blank=True, null=True)
    PAR_pix_chave = models.CharField(max_length=255, verbose_name="Chave PIX", blank=True, null=True, help_text="Chave PIX (CPF, CNPJ, e-mail, telefone ou chave aleatória)")
    PAR_pix_tipo = models.CharField(max_length=20, verbose_name="Tipo da Chave PIX", blank=True, null=True, choices=TIPOS_PIX)
    PAR_pix_beneficiario = models.CharField(max_length=255, verbose_name="Nome do Beneficiário PIX", blank=True, null=True)
    PAR_pix_cidade = models.CharField(max_length=100, verbose_name="Cidade do Beneficiário PIX", blank=True, null=True)
    PAR_pix_uf = models.CharField(max_length=2, verbose_name="UF do Beneficiário PIX", blank=True, null=True)
    PAR_url_youtube = models.URLField(verbose_name="URL do YouTube", blank=True, null=True, help_text="URL do canal do YouTube da paróquia")
    PAR_url_facebook = models.URLField(verbose_name="URL do Facebook", blank=True, null=True, help_text="URL da página do Facebook da paróquia")
    PAR_url_instagram = models.URLField(verbose_name="URL do Instagram", blank=True, null=True, help_text="URL do perfil do Instagram da paróquia")
    PAR_horarios_fixos_json = models.TextField(
        verbose_name="Horários Fixos de Celebração", blank=True, null=True, default='{}',
        help_text="Horários fixos por dia da semana em formato JSON"
    )
    PAR_data_criacao = models.DateTimeField(default=timezone.now, verbose_name="Data de Criação")
    PAR_data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")

    class Meta:
        verbose_name = "Paróquia"
        verbose_name_plural = "Paróquias"
        db_table = 'TBPAROQUIA'

    def __str__(self):
        return self.PAR_nome_paroquia or "Paróquia"

    # --- LÓGICA DE HORÁRIOS ---
    def get_horarios_fixos(self):
        try:
            return json.loads(self.PAR_horarios_fixos_json or '{}')
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_horarios_fixos(self, horarios_dict):
        self.PAR_horarios_fixos_json = json.dumps(horarios_dict)

    def get_horarios_display(self):
        horarios = self.get_horarios_fixos()
        return {DIAS_DISPLAY[k]: v for k, v in horarios.items() if k in DIAS_DISPLAY and v}

    def get_pix_tipo_display(self):
        if not self.PAR_pix_tipo:
            return None
        return dict(TIPOS_PIX).get(self.PAR_pix_tipo, self.PAR_pix_tipo)

    # --- O PENTE FINO: COMPRESSÃO DE IMAGEM ---
    def save(self, *args, **kwargs):
        """Reduz a foto do pároco antes de enviar ao Wasabi."""
        if self.PAR_foto_paroco:
            try:
                img = Image.open(self.PAR_foto_paroco)
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                output_size = (600, 600) # Foto de perfil não precisa ser maior que isso
                img.thumbnail(output_size)

                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=75, optimize=True)
                buffer.seek(0)

                # Gera o nome do arquivo garantindo a extensão .jpg
                nome_limpo = os.path.splitext(self.PAR_foto_paroco.name)[0] + '.jpg'
                self.PAR_foto_paroco.save(nome_limpo, ContentFile(buffer.read()), save=False)
            except Exception as e:
                print(f"Erro na compressão (Paróquia): {e}")

        super(TBPAROQUIA, self).save(*args, **kwargs)
