from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import re


def limpar_telefone_para_display(telefone):
    """Função auxiliar para formatar telefone para exibição"""
    if not telefone:
        return ""
    
    # Remove caracteres não numéricos
    numeros = ''.join(filter(str.isdigit, str(telefone)))
    
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    elif len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    else:
        return telefone


class TBDIZIMISTAS(models.Model):
    """Modelo para cadastro de dizimistas"""
    
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    ]
    
    # Campos obrigatórios
    DIS_telefone = models.CharField(max_length=20, verbose_name="Telefone", unique=True)
    DIS_nome = models.CharField(max_length=200, verbose_name="Nome Completo")
    
    # Dados pessoais
    DIS_email = models.EmailField(verbose_name="E-mail", blank=True, null=True)
    DIS_data_nascimento = models.DateField(verbose_name="Data de Nascimento", blank=True, null=True)
    DIS_sexo = models.CharField(max_length=1, verbose_name="Sexo", choices=SEXO_CHOICES, blank=True, null=True)
    
    # Endereço
    DIS_cep = models.CharField(max_length=10, verbose_name="CEP", blank=True, null=True)
    DIS_endereco = models.CharField(max_length=200, verbose_name="Endereço", blank=True, null=True)
    DIS_numero = models.CharField(max_length=10, verbose_name="Número", blank=True, null=True)
    DIS_complemento = models.CharField(max_length=100, verbose_name="Complemento", blank=True, null=True, help_text="Casa, apartamento, sala, etc.")
    DIS_bairro = models.CharField(max_length=100, verbose_name="Bairro", blank=True, null=True)
    DIS_cidade = models.CharField(max_length=100, verbose_name="Cidade", blank=True, null=True)
    DIS_estado = models.CharField(max_length=2, verbose_name="Estado", blank=True, null=True)
    
    # Foto
    DIS_foto = models.ImageField(upload_to='dizimistas/', verbose_name="Foto", blank=True, null=True)
    
    # Dados pessoais adicionais
    DIS_cpf = models.CharField(max_length=14, verbose_name="CPF", blank=True, null=True, help_text="Formato: 000.000.000-00")
    DIS_valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor do Dízimo", blank=True, null=True, help_text="Valor que o dizimista deseja doar")
    
    # Status
    DIS_status = models.BooleanField(verbose_name="Status", default=False, help_text="True = Ativo, False = Pendente")
    
    # Datas
    DIS_data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    DIS_data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    def __str__(self):
        return f"{self.DIS_nome} ({limpar_telefone_para_display(self.DIS_telefone)})"
    
    class Meta:
        verbose_name = "Dizimista"
        verbose_name_plural = "Dizimistas"
        db_table = 'TBDIZIMISTAS'
        ordering = ['DIS_nome']
    
    def get_status_display(self):
        """Retorna o status formatado"""
        return "Ativo" if self.DIS_status else "Pendente"
    
    def get_status_class(self):
        """Retorna a classe CSS para o status"""
        return "success" if self.DIS_status else "warning"
    
    def get_foto_url(self):
        """Retorna a URL da foto ou uma imagem padrão"""
        if self.DIS_foto:
            return self.DIS_foto.url
        return "/static/img/default-avatar.png"
    
    def clean(self):
        """Validação personalizada"""
        from django.core.exceptions import ValidationError
        
        # Validação do telefone
        if self.DIS_telefone:
            # Remove caracteres não numéricos
            telefone_limpo = ''.join(filter(str.isdigit, str(self.DIS_telefone)))
            if len(telefone_limpo) < 10:
                raise ValidationError("Telefone deve ter pelo menos 10 dígitos")
        
        # Validação do CEP
        if self.DIS_cep:
            cep_limpo = ''.join(filter(str.isdigit, str(self.DIS_cep)))
            if len(cep_limpo) != 8:
                raise ValidationError("CEP deve ter 8 dígitos")
        
        # Validação do CPF
        if self.DIS_cpf:
            if not self.validar_cpf(self.DIS_cpf):
                raise ValidationError("CPF inválido")
    
    def validar_cpf(self, cpf):
        """Valida CPF"""
        # Remove caracteres não numéricos
        cpf_limpo = ''.join(filter(str.isdigit, str(cpf)))
        
        # Verifica se tem 11 dígitos
        if len(cpf_limpo) != 11:
            return False
        
        # Verifica se todos os dígitos são iguais
        if cpf_limpo == cpf_limpo[0] * 11:
            return False
        
        # Calcula primeiro dígito verificador
        soma = 0
        for i in range(9):
            soma += int(cpf_limpo[i]) * (10 - i)
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        # Calcula segundo dígito verificador
        soma = 0
        for i in range(10):
            soma += int(cpf_limpo[i]) * (11 - i)
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        # Verifica se os dígitos calculados são iguais aos do CPF
        return cpf_limpo[-2:] == f"{digito1}{digito2}"


class TBDOACAODIZIMO(models.Model):
    """Modelo para cadastro de doações/dízimos"""
    
    TIPO_CHOICES = [
        ('DIZIMO', 'Dízimo'),
        ('OFERTA', 'Oferta'),
        ('DOACAO', 'Doação'),
        ('OUTRO', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('RECEBIDO', 'Recebido'),
        ('ATRASADO', 'Atrasado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    FORMA_PAGAMENTO_CHOICES = [
        ('DINHEIRO', 'Dinheiro'),
        ('PIX', 'PIX'),
        ('CARTAO', 'Cartão'),
        ('TRANSFERENCIA', 'Transferência'),
        ('CHEQUE', 'Cheque'),
        ('OUTRO', 'Outro'),
    ]
    
    # Relacionamento
    dizimista = models.ForeignKey(TBDIZIMISTAS, on_delete=models.CASCADE, verbose_name="Dizimista")
    
    # Informações da doação
    tipo = models.CharField(max_length=20, verbose_name="Tipo", choices=TIPO_CHOICES, default='DIZIMO')
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    
    # Recebimento
    status = models.CharField(max_length=20, verbose_name="Status", choices=STATUS_CHOICES, default='PENDENTE')
    data_recebimento = models.DateField(verbose_name="Data de Recebimento", blank=True, null=True)
    forma_pagamento = models.CharField(max_length=20, verbose_name="Forma de Pagamento", choices=FORMA_PAGAMENTO_CHOICES, blank=True, null=True)
    
    # Observações
    observacoes = models.TextField(verbose_name="Observações", blank=True, null=True)
    
    # Status
    ativo = models.BooleanField(verbose_name="Ativo", default=True)
    
    # Datas
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    def __str__(self):
        return f"{self.dizimista.DIS_nome} - {self.tipo} - R$ {self.valor} - {self.get_status_display()}"
    
    class Meta:
        verbose_name = "Doação/Dízimo"
        verbose_name_plural = "Doações/Dízimos"
        db_table = 'TBDOACAODIZIMO'
        ordering = ['-data_vencimento', 'dizimista__DIS_nome']
    
    def get_status_display(self):
        """Retorna o status formatado"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
    
    def get_status_class(self):
        """Retorna a classe CSS para o status"""
        status_classes = {
            'PENDENTE': 'warning',
            'RECEBIDO': 'success',
            'ATRASADO': 'danger',
            'CANCELADO': 'secondary',
        }
        return status_classes.get(self.status, 'info')
    
    def is_atrasado(self):
        """Verifica se a doação está atrasada"""
        if self.status == 'PENDENTE' and self.data_vencimento < timezone.now().date():
            return True
        return False
    
    def calcular_dias_atraso(self):
        """Calcula quantos dias a doação está atrasada"""
        if self.is_atrasado():
            return (timezone.now().date() - self.data_vencimento).days
        return 0
