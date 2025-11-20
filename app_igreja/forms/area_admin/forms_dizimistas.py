"""
==================== FORMULÁRIOS DE DIZIMISTAS ====================
Arquivo com formulários específicos para Dizimistas
"""

from django import forms
from django.core.exceptions import ValidationError
from ...models.area_admin.models_dizimistas import TBDIZIMISTAS, TBDOACAODIZIMO
from .forms_commons import BaseAdminForm, DateInputWidget


class DizimistaForm(BaseAdminForm):
    """Formulário para cadastro de dizimistas"""
    
    class Meta:
        model = TBDIZIMISTAS
        fields = [
            'DIS_telefone', 'DIS_nome', 'DIS_email', 'DIS_data_nascimento', 'DIS_sexo',
            'DIS_cep', 'DIS_endereco', 'DIS_numero', 'DIS_complemento', 'DIS_bairro', 'DIS_cidade', 'DIS_estado', 
            'DIS_foto', 'DIS_cpf', 'DIS_valor', 'DIS_status'
        ]
        widgets = {
            'DIS_telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000',
                'id': 'DIS_telefone'
            }),
            'DIS_nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do dizimista'
            }),
            'DIS_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'DIS_data_nascimento': DateInputWidget(attrs={
                'class': 'form-control'
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
                'id': 'DIS_cep',
                'onblur': 'buscarCep()'
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
            'DIS_status': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'DIS_telefone': 'Telefone',
            'DIS_nome': 'Nome Completo',
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
            'DIS_valor': 'Valor do Dízimo',
            'DIS_status': 'Status'
        }
    
    def clean_DIS_valor(self):
        """Validação do valor"""
        valor = self.cleaned_data.get('DIS_valor')
        if valor and valor <= 0:
            raise ValidationError("O valor deve ser maior que zero.")
        return valor


class DoacaoDizimoForm(forms.ModelForm):
    """Formulário para cadastro de doações/dízimos"""
    
    class Meta:
        model = TBDOACAODIZIMO
        fields = [
            'dizimista', 'tipo', 'valor', 'data_vencimento', 
            'status', 'data_recebimento', 'forma_pagamento', 'observacoes', 'ativo'
        ]
        widgets = {
            'dizimista': forms.Select(attrs={
                'class': 'form-control',
                'id': 'dizimista'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control',
                'id': 'tipo'
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'id': 'valor'
            }),
            'data_vencimento': DateInputWidget(attrs={
                'class': 'form-control',
                'id': 'data_vencimento'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
                'id': 'status'
            }),
            'data_recebimento': DateInputWidget(attrs={
                'class': 'form-control',
                'id': 'data_recebimento'
            }),
            'forma_pagamento': forms.Select(attrs={
                'class': 'form-control',
                'id': 'forma_pagamento'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Observações sobre a doação...',
                'id': 'observacoes'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'ativo'
            }),
        }
        labels = {
            'dizimista': 'Dizimista',
            'tipo': 'Tipo de Doação',
            'valor': 'Valor',
            'data_vencimento': 'Data de Vencimento',
            'status': 'Status',
            'data_recebimento': 'Data de Recebimento',
            'forma_pagamento': 'Forma de Pagamento',
            'observacoes': 'Observações',
            'ativo': 'Ativo'
        }
    
    def clean_valor(self):
        """Validação do valor"""
        valor = self.cleaned_data.get('valor')
        if valor and valor <= 0:
            raise ValidationError("O valor deve ser maior que zero.")
        return valor
    
    def clean_data_recebimento(self):
        """Validação da data de recebimento"""
        data_recebimento = self.cleaned_data.get('data_recebimento')
        data_vencimento = self.cleaned_data.get('data_vencimento')
        
        if data_recebimento and data_vencimento:
            if data_recebimento < data_vencimento:
                raise ValidationError("A data de recebimento não pode ser anterior à data de vencimento.")
        
        return data_recebimento
