"""
==================== FORMULÁRIOS DE COLABORADORES ====================
Arquivo com formulários específicos para Colaboradores
"""

from django import forms
from django.core.exceptions import ValidationError
from ...models.area_admin.models_colaboradores import TBCOLABORADORES
from .forms_commons import BaseAdminForm, DateInputWidget, get_estados_brasil


class ColaboradorForm(BaseAdminForm):
    """
    Formulário para CRUD de Colaboradores
    """
    COL_funcao_id = forms.ChoiceField(
        label='Função',
        required=False,
        choices=[('', 'Selecione uma função...')],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'COL_funcao_id'
        })
    )
    
    def clean_COL_funcao_id(self):
        """Converte string vazia para None"""
        value = self.cleaned_data.get('COL_funcao_id')
        if value == '':
            return None
        return value
    
    class Meta:
        model = TBCOLABORADORES
        fields = [
            'COL_telefone',
            'COL_nome_completo',
            'COL_apelido',
            'COL_cep',
            'COL_endereco',
            'COL_numero',
            'COL_complemento',
            'COL_bairro',
            'COL_cidade',
            'COL_estado',
            'COL_data_nascimento',
            'COL_sexo',
            'COL_estado_civil',
            'COL_funcao_pretendida',
            'COL_foto',
            'COL_status',
            'COL_membro_ativo',
            'COL_funcao_id',
        ]
        widgets = {
            'COL_telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Telefone',
                'id': 'COL_telefone'
            }),
            'COL_nome_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo',
                'id': 'COL_nome_completo'
            }),
            'COL_apelido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apelido',
                'id': 'COL_apelido'
            }),
            'COL_cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'CEP',
                'id': 'COL_cep'
            }),
            'COL_endereco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Endereço',
                'id': 'COL_endereco'
            }),
            'COL_numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número',
                'id': 'COL_numero'
            }),
            'COL_complemento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Complemento',
                'id': 'COL_complemento'
            }),
            'COL_bairro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bairro',
                'id': 'COL_bairro'
            }),
            'COL_cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade',
                'id': 'COL_cidade'
            }),
            'COL_estado': forms.Select(attrs={
                'class': 'form-control',
                'id': 'COL_estado'
            }, choices=[('', 'Selecione...')] + list(get_estados_brasil())),
            'COL_data_nascimento': DateInputWidget(attrs={
                'class': 'form-control',
                'id': 'COL_data_nascimento'
            }),
            'COL_sexo': forms.Select(attrs={
                'class': 'form-control',
                'id': 'COL_sexo'
            }, choices=[('', 'Selecione...'), ('M', 'Masculino'), ('F', 'Feminino')]),
            'COL_estado_civil': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estado civil',
                'id': 'COL_estado_civil'
            }),
            'COL_funcao_pretendida': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Função pretendida',
                'id': 'COL_funcao_pretendida'
            }),
            'COL_foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'COL_foto'
            }),
            'COL_status': forms.Select(attrs={
                'class': 'form-control',
                'id': 'COL_status'
            }, choices=[
                ('PENDENTE', 'Pendente'),
                ('ATIVO', 'Ativo'),
                ('INATIVO', 'Inativo')
            ]),
            'COL_membro_ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'COL_membro_ativo'
            }),
        }
