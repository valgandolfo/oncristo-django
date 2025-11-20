"""
==================== FORMULÁRIOS DE DIOCESES ====================
Arquivo com formulários específicos para Diocese

🔗 HERDA COMPONENTES DE:
├── Models: app_igreja.models.area_admin.models_dioceses.TBDIOCESE
├── Commons: app_igreja.forms.area_admin.forms_commons.BaseAdminForm
├── Utils: app_igreja.utils.ESTADOS_BRASIL (lista de estados)
└── Widgets: forms_commons.DateInputWidget, validações Comuns

📋 FORMS DISPONÍVEIS:
├── DioceseForm: Formulário completo para diocese com validações
├── Validações herdadas: telefone, CEP, foto, CPF (do BaseAdminForm)
└── Widgets: campos HTML5, estilos Bootstrap
"""

from django import forms

# Imports específicos com comentários de origem
from ...models.area_admin.models_dioceses import TBDIOCESE  # Model: estrutura de dados
from .forms_commons import BaseAdminForm, get_estados_brasil  # Commons: herança + utils


class DioceseForm(BaseAdminForm):
    """Formulário para Diocese baseado no model TBDIOCESE"""

    class Meta:
        model = TBDIOCESE
        fields = [
            'DIO_nome_diocese',
            'DIO_nome_bispo', 
            'DIO_foto_bispo',
            'DIO_cep',
            'DIO_endereco',
            'DIO_numero',
            'DIO_complemento',
            'DIO_bairro',
            'DIO_cidade',
            'DIO_uf',
            'DIO_telefone',
            'DIO_email',
            'DIO_site',
        ]
        widgets = {
            'DIO_nome_diocese': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da Diocese',
                'id': 'DIO_nome_diocese'
            }),
            'DIO_nome_bispo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do Bispo',
                'id': 'DIO_nome_bispo'
            }),
            'DIO_foto_bispo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'DIO_foto_bispo'
            }),
            'DIO_cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000',
                'id': 'DIO_cep'
            }),
            'DIO_endereco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o endereço',
                'id': 'DIO_endereco'
            }),
            'DIO_numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número',
                'id': 'DIO_numero'
            }),
            'DIO_complemento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Complemento (apto, sala, etc.)',
                'id': 'DIO_complemento'
            }),
            'DIO_bairro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bairro',
                'id': 'DIO_bairro'
            }),
            'DIO_cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade',
                'id': 'DIO_cidade'
            }),
            'DIO_uf': forms.Select(attrs={
                'class': 'form-control',
                'id': 'DIO_uf'
            }, choices=[('', 'Selecione UF')] + list(get_estados_brasil())),
            'DIO_telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 0000-0000',
                'id': 'DIO_telefone'
            }),
            'DIO_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@diocese.com.br',
                'id': 'DIO_email'
            }),
            'DIO_site': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.diocese.com.br',
                'id': 'DIO_site'
            }),
        }
