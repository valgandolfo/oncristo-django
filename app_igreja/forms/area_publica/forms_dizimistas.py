"""
==================== FORMULÁRIOS PÚBLICOS DE DIZIMISTAS ====================
Arquivo com formulários específicos para cadastro público de Dizimistas
"""

from django import forms
from django.core.exceptions import ValidationError
from ...models.area_admin.models_dizimistas import TBDIZIMISTAS


class DizimistaPublicoForm(forms.ModelForm):
    """Formulário público para cadastro de dizimistas"""
    
    class Meta:
        model = TBDIZIMISTAS
        fields = [
            'DIS_telefone', 'DIS_nome', 'DIS_email', 'DIS_data_nascimento', 'DIS_sexo',
            'DIS_cep', 'DIS_endereco', 'DIS_numero', 'DIS_complemento', 'DIS_bairro', 'DIS_cidade', 'DIS_estado', 
            'DIS_foto', 'DIS_cpf', 'DIS_valor'
        ]
        widgets = {
            'DIS_telefone': forms.TextInput(attrs={
                'class': 'form-control form-control',
                'placeholder': '(00) 00000-0000',
                'id': 'DIS_telefone',
                'required': True
            }),
            'DIS_nome': forms.TextInput(attrs={
                'class': 'form-control form-control',
                'placeholder': 'Nome completo do dizimista',
                'required': True
            }),
            'DIS_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'DIS_data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'DIS_sexo': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('', 'Selecione...'),
                ('M', 'Masculino'),
                ('F', 'Feminino'),
            ]),
            'DIS_cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000',
                'id': 'DIS_cep'
            }),
            'DIS_endereco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Endereço completo',
                'id': 'DIS_endereco'
            }),
            'DIS_numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número',
                'id': 'DIS_numero'
            }),
            'DIS_complemento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Complemento (casa, apto, sala, etc.)',
                'id': 'DIS_complemento'
            }),
            'DIS_bairro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bairro',
                'id': 'DIS_bairro'
            }),
            'DIS_cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade',
                'id': 'DIS_cidade'
            }),
            'DIS_estado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'UF',
                'maxlength': '2',
                'id': 'DIS_estado'
            }),
            'DIS_foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'onchange': 'previewFoto(this)'
            }),
            'DIS_cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00',
                'id': 'DIS_cpf',
                'maxlength': '14'
            }),
            'DIS_valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'id': 'DIS_valor'
            }),
        }
        labels = {
            'DIS_telefone': 'Telefone *',
            'DIS_nome': 'Nome Completo *',
            'DIS_email': 'E-mail',
            'DIS_data_nascimento': 'Data de Nascimento',
            'DIS_sexo': 'Sexo',
            'DIS_cep': 'CEP',
            'DIS_endereco': 'Endereço',
            'DIS_numero': 'Número',
            'DIS_complemento': 'Complemento',
            'DIS_bairro': 'Bairro',
            'DIS_cidade': 'Cidade',
            'DIS_estado': 'Estado',
            'DIS_foto': 'Foto',
            'DIS_cpf': 'CPF',
            'DIS_valor': 'Valor do Dízimo (R$)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Campos obrigatórios
        self.fields['DIS_telefone'].required = True
        self.fields['DIS_nome'].required = True
        
        # Adicionar classes CSS para campos obrigatórios
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['class'] += ' required-field'
    
    def clean_DIS_telefone(self):
        """Validação do telefone"""
        telefone = self.cleaned_data.get('DIS_telefone')
        if telefone:
            # Remove caracteres não numéricos
            telefone_limpo = ''.join(filter(str.isdigit, str(telefone)))
            if len(telefone_limpo) < 10:
                raise ValidationError("Telefone deve ter pelo menos 10 dígitos")
            
            # Verificar se já existe
            if TBDIZIMISTAS.objects.filter(DIS_telefone=telefone).exists():
                raise ValidationError("Este telefone já está cadastrado")
                
        return telefone
    
    def clean_DIS_email(self):
        """Validação do email"""
        email = self.cleaned_data.get('DIS_email')
        if email:
            # Verificar se já existe
            if TBDIZIMISTAS.objects.filter(DIS_email=email).exists():
                raise ValidationError("Este e-mail já está cadastrado")
        return email
    
    def clean_DIS_valor(self):
        """Validação do valor"""
        valor = self.cleaned_data.get('DIS_valor')
        if valor and valor <= 0:
            raise ValidationError("O valor deve ser maior que zero.")
        return valor
    
    def clean_DIS_cep(self):
        """Validação do CEP"""
        cep = self.cleaned_data.get('DIS_cep')
        if cep:
            cep_limpo = ''.join(filter(str.isdigit, str(cep)))
            if len(cep_limpo) != 8:
                raise ValidationError("CEP deve ter 8 dígitos")
        return cep
    
    def clean_DIS_cpf(self):
        """Validação do CPF"""
        cpf = self.cleaned_data.get('DIS_cpf')
        if cpf:
            if not self.validar_cpf(cpf):
                raise ValidationError("CPF inválido")
        return cpf
    
    def validar_cpf(self, cpf):
        """Valida CPF"""
        import re
        
        # Remove caracteres não numéricos
        cpf = re.sub(r'[^0-9]', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False
        
        # Verifica se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Validação do primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        if int(cpf[9]) != digito1:
            return False
        
        # Validação do segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        return int(cpf[10]) == digito2
