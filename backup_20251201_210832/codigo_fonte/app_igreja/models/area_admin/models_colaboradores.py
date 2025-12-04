


from django.db import models
from django.utils import timezone

class TBCOLABORADORES(models.Model):
    """
    Tabela de Colaboradores - Define os colaboradores da igreja
    """
    COL_id = models.AutoField(primary_key=True, verbose_name="ID do Colaborador")
    COL_telefone = models.CharField(max_length=20, unique=True, verbose_name="Telefone")
    COL_nome_completo = models.CharField(max_length=200, verbose_name="Nome Completo")
    COL_apelido = models.CharField(max_length=100, blank=True, null=True, verbose_name="Apelido")
    COL_cep = models.CharField(max_length=10, blank=True, null=True, verbose_name="CEP")
    COL_endereco = models.CharField(max_length=200, blank=True, null=True, verbose_name="Endereço")
    COL_numero = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número")
    COL_complemento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Complemento")
    COL_bairro = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    COL_cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    COL_estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="Estado")
    COL_data_nascimento = models.DateField(blank=True, null=True, verbose_name="Data de Nascimento")
    COL_sexo = models.CharField(max_length=1, blank=True, null=True, verbose_name="Sexo", choices=[('M', 'Masculino'), ('F', 'Feminino')])
    COL_estado_civil = models.CharField(max_length=20, blank=True, null=True, verbose_name="Estado Civil")
    COL_funcao_pretendida = models.CharField(max_length=100, blank=True, null=True, verbose_name="Função Pretendida")
    COL_foto = models.ImageField(upload_to='colaboradores/', blank=True, null=True, verbose_name="Foto")
    COL_status = models.CharField(max_length=20, default='PENDENTE', verbose_name="Status", choices=[
        ('PENDENTE', 'Pendente'),
        ('ATIVO', 'Ativo'),
        ('INATIVO', 'Inativo')
    ])
    COL_membro_ativo = models.BooleanField(default=False, verbose_name="Membro Ativo")
    COL_funcao_id = models.IntegerField(blank=True, null=True, verbose_name="ID da Função")
    COL_data_cadastro = models.DateTimeField(default=timezone.now, verbose_name="Data de Cadastro")
    COL_data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        db_table = 'TBCOLABORADORES'
        verbose_name = 'Colaborador'
        verbose_name_plural = 'Colaboradores'
        ordering = ['COL_nome_completo']
    
    def __str__(self):
        return f"{self.COL_nome_completo}"
    
    def save(self, *args, **kwargs):
        """Override save para atualizar COL_data_atualizacao e formatar telefone"""
        # Formatar telefone antes de salvar se não estiver formatado
        if self.COL_telefone:
            # Verificar se já está formatado (tem parênteses ou hífen)
            if '(' not in str(self.COL_telefone) and '-' not in str(self.COL_telefone):
                # Não está formatado, então formatar
                numeros = ''.join(filter(str.isdigit, str(self.COL_telefone)))
                # Remove código do país (55) se existir
                if numeros.startswith('55') and len(numeros) > 11:
                    numeros = numeros[2:]
                # Formata conforme o tamanho
                if len(numeros) == 11:
                    self.COL_telefone = f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
                elif len(numeros) == 10:
                    self.COL_telefone = f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
        
        self.COL_data_atualizacao = timezone.now()
        super().save(*args, **kwargs)
