from django.db import models
from django.utils import timezone


class TBDIOCESE(models.Model):
    """
    Modelo para a tabela TBDIOCESE
    Representa as dioceses da igreja
    """
    DIO_id = models.AutoField(primary_key=True)
    DIO_nome_diocese = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome da Diocese")
    DIO_nome_bispo = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome do Bispo")
    DIO_foto_bispo = models.ImageField(upload_to='bispos/', blank=True, null=True, verbose_name="Foto do Bispo")
    DIO_cep = models.CharField(max_length=10, blank=True, null=True, verbose_name="CEP")
    DIO_endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    DIO_numero = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número")
    DIO_complemento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Complemento")
    DIO_bairro = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    DIO_cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    DIO_uf = models.CharField(max_length=2, blank=True, null=True, verbose_name="UF")
    DIO_telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    DIO_email = models.EmailField(max_length=254, blank=True, null=True, verbose_name="E-mail")
    DIO_site = models.URLField(max_length=200, blank=True, null=True, verbose_name="Site")
    DIO_data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    DIO_data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")

    class Meta:
        db_table = 'TBDIOCESE'
        verbose_name = 'Diocese'
        verbose_name_plural = 'Dioceses'
        ordering = ['DIO_nome_diocese']

    def __str__(self):
        return self.DIO_nome_diocese or f'Diocese ID: {self.DIO_id}'
