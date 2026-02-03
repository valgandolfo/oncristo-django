from django.db import models
from django.utils import timezone


class TBDIZIMISTAS(models.Model):
    """Modelo para cadastro de dizimistas."""
    
    DIS_telefone = models.CharField(max_length=20, unique=True, verbose_name='Telefone')
    DIS_nome = models.CharField(max_length=200, verbose_name='Nome Completo')
    DIS_email = models.EmailField(blank=True, null=True, verbose_name='E-mail')
    DIS_data_nascimento = models.DateField(blank=True, null=True, verbose_name='Data de Nascimento')
    DIS_sexo = models.CharField(
        max_length=1, blank=True, null=True,
        choices=[('M', 'Masculino'), ('F', 'Feminino')],
        verbose_name='Sexo'
    )
    DIS_cep = models.CharField(max_length=10, blank=True, null=True, verbose_name='CEP')
    DIS_endereco = models.CharField(max_length=200, blank=True, null=True, verbose_name='Endereço')
    DIS_numero = models.CharField(max_length=10, blank=True, null=True, verbose_name='Número')
    DIS_complemento = models.CharField(
        max_length=100, blank=True, null=True,
        help_text='Casa, apartamento, sala, etc.',
        verbose_name='Complemento'
    )
    DIS_bairro = models.CharField(max_length=100, blank=True, null=True, verbose_name='Bairro')
    DIS_cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name='Cidade')
    DIS_estado = models.CharField(max_length=2, blank=True, null=True, verbose_name='Estado')
    DIS_foto = models.ImageField(upload_to='dizimistas/', blank=True, null=True, verbose_name='Foto')
    DIS_cpf = models.CharField(
        max_length=14, blank=True, null=True,
        help_text='Formato: 000.000.000-00',
        verbose_name='CPF'
    )
    DIS_dia_pagamento = models.IntegerField(
        blank=True, null=True,
        help_text='Dia do mês em que o dizimista prefere fazer o pagamento (1-31)',
        verbose_name='Dia do Pagamento'
    )
    DIS_valor = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        help_text='Valor que o dizimista deseja doar',
        verbose_name='Valor do Dízimo'
    )
    DIS_status = models.BooleanField(
        default=False,
        help_text='True = Ativo, False = Pendente',
        verbose_name='Status'
    )
    DIS_data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')
    DIS_data_atualizacao = models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')

    class Meta:
        db_table = 'TBDIZIMISTAS'
        verbose_name = 'Dizimista'
        verbose_name_plural = 'Dizimistas'
        ordering = ['DIS_nome']

    def __str__(self):
        return self.DIS_nome or self.DIS_telefone or str(self.pk)


class TBGERDIZIMO(models.Model):
    """Modelo para gerenciamento mensal de dízimos."""
    
    GER_id = models.AutoField(primary_key=True, verbose_name="ID")
    GER_mesano = models.DateField(verbose_name="Mês/Ano", help_text="Mês e ano de referência")
    GER_dizimista = models.ForeignKey(
        TBDIZIMISTAS,
        on_delete=models.CASCADE,
        verbose_name="Dizimista",
        related_name='gerenciamentos_dizimo'
    )
    GER_dtvencimento = models.DateField(verbose_name="Data de Vencimento")
    GER_vlr_dizimo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor do Dízimo")
    GER_dtpagto = models.DateField(verbose_name="Data de Pagamento", blank=True, null=True)
    GER_vlr_pago = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Pago", blank=True, null=True)
    GER_observacao = models.CharField(max_length=100, verbose_name="Observação", blank=True, null=True)
    
    GER_data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    GER_data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")

    class Meta:
        db_table = 'TBGERDIZIMO'
        verbose_name = "Gerenciamento de Dízimo"
        verbose_name_plural = "Gerenciamentos de Dízimos"
        ordering = ['-GER_mesano', 'GER_dizimista__DIS_nome']
        indexes = [
            models.Index(fields=['GER_mesano', 'GER_dizimista']),
            models.Index(fields=['GER_dtvencimento']),
        ]

    def __str__(self):
        return f"{self.GER_dizimista.DIS_nome} - {self.GER_mesano.strftime('%m/%Y')}"

    def get_status_pagamento(self):
        """Lógica de status para a View."""
        if self.GER_vlr_pago and self.GER_vlr_pago >= self.GER_vlr_dizimo:
            return "Pago"
        if self.GER_vlr_pago and self.GER_vlr_pago > 0:
            return "Parcial"
        if self.GER_dtvencimento < timezone.now().date():
            return "Atrasado"
        return "Pendente"