from django.db import models
from django.utils import timezone
from .models_dioceses import TBDIOCESE
from ...utils import TIPOS_PIX


class TBPAROQUIA(models.Model):
    """Modelo para Paróquias com prefixos PAR_"""
    
    # Campos principais
    PAR_nome_paroquia = models.CharField(max_length=255, verbose_name="Nome da Paróquia", null=True, blank=True)
    PAR_diocese = models.ForeignKey(TBDIOCESE, on_delete=models.CASCADE, verbose_name="Diocese", blank=True, null=True)
    
    # Endereço
    PAR_cep = models.CharField(max_length=10, verbose_name="CEP", blank=True, null=True)
    PAR_endereco = models.TextField(verbose_name="Endereço", blank=True, null=True)
    PAR_numero = models.CharField(max_length=10, verbose_name="Número", blank=True, null=True)
    PAR_cidade = models.CharField(max_length=100, verbose_name="Cidade", blank=True, null=True)
    PAR_uf = models.CharField(max_length=2, verbose_name="UF", blank=True, null=True)
    PAR_bairro = models.CharField(max_length=100, verbose_name="Bairro", blank=True, null=True)
    
    # Contato
    PAR_telefone = models.CharField(max_length=20, verbose_name="Telefone", blank=True, null=True)
    PAR_email = models.EmailField(verbose_name="E-mail", blank=True, null=True)
    
    # Pessoas
    PAR_paroco = models.CharField(max_length=255, verbose_name="Pároco", blank=True, null=True)
    PAR_foto_paroco = models.ImageField(upload_to='parocos/', verbose_name="Foto do Pároco", blank=True, null=True)
    PAR_secretario = models.CharField(max_length=255, verbose_name="Secretário(a)", blank=True, null=True)
    
    # Dados bancários
    PAR_cnpj = models.CharField(max_length=18, verbose_name="CNPJ", blank=True, null=True)
    PAR_banco = models.CharField(max_length=100, verbose_name="Banco", blank=True, null=True)
    PAR_agencia = models.CharField(max_length=20, verbose_name="Agência", blank=True, null=True)
    PAR_conta = models.CharField(max_length=20, verbose_name="Conta", blank=True, null=True)
    
    # Dados PIX
    PAR_pix_chave = models.CharField(max_length=255, verbose_name="Chave PIX", blank=True, null=True, help_text="Chave PIX (CPF, CNPJ, e-mail, telefone ou chave aleatória)")
    PAR_pix_tipo = models.CharField(max_length=20, verbose_name="Tipo da Chave PIX", blank=True, null=True, choices=TIPOS_PIX)
    PAR_pix_beneficiario = models.CharField(max_length=255, verbose_name="Nome do Beneficiário PIX", blank=True, null=True)
    PAR_pix_cidade = models.CharField(max_length=100, verbose_name="Cidade do Beneficiário PIX", blank=True, null=True)
    PAR_pix_uf = models.CharField(max_length=2, verbose_name="UF do Beneficiário PIX", blank=True, null=True)
    
    # Horários Fixos de Celebração (JSON)
    PAR_horarios_fixos_json = models.TextField(
        verbose_name="Horários Fixos de Celebração", 
        blank=True, 
        null=True,
        default='{}',
        help_text="Horários fixos de celebração por dia da semana em formato JSON"
    )
    
    # Controle
    PAR_data_criacao = models.DateTimeField(default=timezone.now, verbose_name="Data de Criação")
    PAR_data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    def __str__(self):
        return self.PAR_nome_paroquia or "Paróquia"
    
    class Meta:
        verbose_name = "Paróquia"
        verbose_name_plural = "Paróquias"
        db_table = 'TBPAROQUIA'
    
    def get_horarios_fixos(self):
        """Retorna horários fixos em formato de dicionário"""
        import json
        try:
            return json.loads(self.PAR_horarios_fixos_json or '{}')
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def set_horarios_fixos(self, horarios_dict):
        """Define horários fixos a partir de um dicionário"""
        import json
        self.PAR_horarios_fixos_json = json.dumps(horarios_dict)
    
    def get_horarios_display(self):
        """Retorna horários formatados para exibição"""
        horarios = self.get_horarios_fixos()
        dias_semana = {
            'domingo': 'Domingo',
            'segunda': 'Segunda-feira', 
            'terca': 'Terça-feira',
            'quarta': 'Quarta-feira',
            'quinta': 'Quinta-feira',
            'sexta': 'Sexta-feira',
            'sabado': 'Sábado'
        }
        
        resultado = {}
        for dia, nome_dia in dias_semana.items():
            if dia in horarios and horarios[dia]:
                resultado[nome_dia] = horarios[dia]
        
        return resultado
    
    def get_pix_tipo_display(self):
        """Retorna o display do tipo PIX"""
        if not self.PAR_pix_tipo:
            return None
        tipos_dict = dict(TIPOS_PIX)
        return tipos_dict.get(self.PAR_pix_tipo, self.PAR_pix_tipo)