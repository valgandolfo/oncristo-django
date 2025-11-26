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
    DIS_dia_pagamento = models.IntegerField(verbose_name="Dia do Pagamento", blank=True, null=True, help_text="Dia do mês em que o dizimista prefere fazer o pagamento (1-31)")
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
        
        # Validação do dia de pagamento
        if self.DIS_dia_pagamento is not None:
            if self.DIS_dia_pagamento < 1 or self.DIS_dia_pagamento > 31:
                raise ValidationError("Dia do pagamento deve ser entre 1 e 31")
    
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


class TBGERDIZIMO(models.Model):
    """Modelo para gerenciamento de dízimos"""
    
    # Campos principais
    GER_id = models.AutoField(primary_key=True, verbose_name="ID")
    GER_mesano = models.DateField(verbose_name="Mês/Ano", help_text="Mês e ano de referência do dízimo")
    GER_dizimista = models.ForeignKey(TBDIZIMISTAS, on_delete=models.CASCADE, verbose_name="Dizimista", related_name='gerenciamentos_dizimo')
    GER_dtvencimento = models.DateField(verbose_name="Data de Vencimento")
    GER_vlr_dizimo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor do Dízimo", help_text="Valor esperado do dízimo")
    GER_dtpagto = models.DateField(verbose_name="Data de Pagamento", blank=True, null=True, help_text="Data em que o pagamento foi realizado")
    GER_vlr_pago = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Pago", blank=True, null=True, help_text="Valor efetivamente pago")
    GER_observacao = models.CharField(max_length=100, verbose_name="Observação", blank=True, null=True, help_text="Observações sobre o pagamento")
    
    # Datas de controle
    GER_data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    GER_data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    def __str__(self):
        return f"{self.GER_dizimista.DIS_nome} - {self.GER_mesano.strftime('%m/%Y')} - R$ {self.GER_vlr_dizimo}"
    
    class Meta:
        verbose_name = "Gerenciamento de Dízimo"
        verbose_name_plural = "Gerenciamentos de Dízimos"
        db_table = 'TBGERDIZIMO'
        ordering = ['-GER_mesano', 'GER_dizimista__DIS_nome']
        indexes = [
            models.Index(fields=['GER_mesano', 'GER_dizimista']),
            models.Index(fields=['GER_dtvencimento']),
        ]
    
    def get_status_pagamento(self):
        """Retorna o status do pagamento baseado em cálculos:
        - ATRASADO: Data atual > Data de vencimento e não está pago
        - PARCIAL: Valor pago < Valor do dízimo (mas > 0)
        - PAGO: Valor pago >= Valor do dízimo
        - PENDENTE: Não tem pagamento e não está atrasado
        """
        data_atual = timezone.now().date()
        
        # Verificar se está pago (valor pago >= valor do dízimo)
        if self.GER_vlr_pago is not None and self.GER_vlr_pago > 0:
            if self.GER_vlr_pago >= self.GER_vlr_dizimo:
                return "Pago"
            elif self.GER_vlr_pago < self.GER_vlr_dizimo:
                return "Parcial"
        
        # Se não está pago, verificar se está atrasado
        if self.GER_dtvencimento < data_atual:
            return "Atrasado"
        
        # Caso contrário, está pendente
        return "Pendente"
    
    def get_status_class(self):
        """Retorna a classe CSS para o status"""
        status = self.get_status_pagamento()
        status_classes = {
            'Pago': 'success',
            'Parcial': 'warning',
            'Atrasado': 'danger',
            'Pendente': 'info',
        }
        return status_classes.get(status, 'secondary')
    
    def is_pago(self):
        """Verifica se o dízimo está pago (valor pago >= valor do dízimo)"""
        return self.GER_vlr_pago is not None and self.GER_vlr_pago >= self.GER_vlr_dizimo
    
    def calcular_dias_atraso(self):
        """Calcula quantos dias está atrasado"""
        if not self.is_pago() and self.GER_dtvencimento < timezone.now().date():
            return (timezone.now().date() - self.GER_dtvencimento).days
        return 0
    
    def calcular_diferenca_valor(self):
        """Calcula a diferença entre o valor esperado e o valor pago"""
        if self.GER_vlr_pago is not None:
            return self.GER_vlr_dizimo - self.GER_vlr_pago
        return self.GER_vlr_dizimo
    
    def clean(self):
        """Validação personalizada"""
        from django.core.exceptions import ValidationError
        
        # Validação do valor do dízimo
        if self.GER_vlr_dizimo and self.GER_vlr_dizimo <= 0:
            raise ValidationError("O valor do dízimo deve ser maior que zero")
        
        # Validação do valor pago
        if self.GER_vlr_pago is not None and self.GER_vlr_pago < 0:
            raise ValidationError("O valor pago não pode ser negativo")
        
        # Validação da data de pagamento
        if self.GER_dtpagto and self.GER_dtvencimento:
            if self.GER_dtpagto < self.GER_dtvencimento:
                raise ValidationError("A data de pagamento não pode ser anterior à data de vencimento")
        
        # Validação: se tem data de pagamento, deve ter valor pago
        if self.GER_dtpagto and self.GER_vlr_pago is None:
            raise ValidationError("Se informou a data de pagamento, deve informar o valor pago")
        
        # Validação: se tem valor pago, deve ter data de pagamento
        if self.GER_vlr_pago is not None and not self.GER_dtpagto:
            raise ValidationError("Se informou o valor pago, deve informar a data de pagamento")
