"""
==================== FORMULÁRIOS DE COLABORADORES ====================
Arquivo com formulários específicos para Colaboradores
"""

from django import forms
from django.core.exceptions import ValidationError
from ...models.area_admin.models_colaboradores import TBCOLABORADORES
from ...models.area_admin.models_funcoes import TBFUNCAO
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
    
    # Sobrescrever COL_funcao para ser um ChoiceField em vez de IntegerField
    COL_funcao = forms.ChoiceField(
        label='Função',
        required=False,
        choices=[('', 'Selecione uma função...')],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'COL_funcao'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Popular choices de funções
        funcoes = TBFUNCAO.objects.all().order_by('FUN_nome_funcao')
        choices_funcoes = [('', 'Selecione uma função...')]
        choices_funcoes.extend([(str(funcao.FUN_id), funcao.FUN_nome_funcao) for funcao in funcoes])
        self.fields['COL_funcao_id'].choices = choices_funcoes
        
        # Popular choices do campo COL_funcao
        if 'COL_funcao' in self.fields:
            self.fields['COL_funcao'].choices = choices_funcoes
            
        # Se estiver editando, definir o valor inicial do campo COL_funcao
        if self.instance and self.instance.pk and self.instance.COL_funcao:
            self.fields['COL_funcao'].initial = str(self.instance.COL_funcao)
    
    def clean_COL_funcao_id(self):
        """Converte string vazia para None"""
        value = self.cleaned_data.get('COL_funcao_id')
        if value == '':
            return None
        return value
    
    def clean_COL_funcao(self):
        """Converte string vazia para None"""
        value = self.cleaned_data.get('COL_funcao')
        if value == '' or value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
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
            'COL_funcao',
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
            'COL_estado_civil': forms.Select(attrs={
                'class': 'form-control',
                'id': 'COL_estado_civil'
            }, choices=[
                ('', 'Selecione...'),
                ('SOLTEIRO', 'Solteiro(a)'),
                ('CASADO', 'Casado(a)'),
                ('DIVORCIADO', 'Divorciado(a)'),
                ('VIUVO', 'Viúvo(a)'),
                ('UNIAO_ESTAVEL', 'União Estável'),
                ('SEPARADO', 'Separado(a)'),
            ]),
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
