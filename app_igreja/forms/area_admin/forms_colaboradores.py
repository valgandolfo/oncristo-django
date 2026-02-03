"""
==================== FORMULÁRIOS DE COLABORADORES ====================
Arquivo com formulários específicos para Colaboradores
"""

from django import forms
from django.core.exceptions import ValidationError
from ...models.area_admin.models_colaboradores import TBCOLABORADORES
from ...models.area_admin.models_funcoes import TBFUNCAO
from ...models.area_admin.models_grupos import TBGRUPOS
from .forms_commons import BaseAdminForm, DateInputWidget, get_estados_brasil


class ColaboradorForm(BaseAdminForm):
    """
    Formulário para CRUD de Colaboradores
    """
    COL_funcao = forms.ChoiceField(
        label='Função',
        required=False,
        choices=[('', 'Selecione uma função...')],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'COL_funcao'
        })
    )

    COL_grupo_liturgico = forms.ChoiceField(
        label='Grupo Litúrgico',
        required=False,
        choices=[('', 'Selecione um grupo...')],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'COL_grupo_liturgico'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        funcoes = TBFUNCAO.objects.all().order_by('FUN_nome_funcao')
        choices_funcoes = [('', 'Selecione uma função...')]
        choices_funcoes.extend([(str(f.FUN_id), f.FUN_nome_funcao) for f in funcoes])
        self.fields['COL_funcao'].choices = choices_funcoes
        if self.instance and self.instance.pk and self.instance.COL_funcao:
            self.fields['COL_funcao'].initial = str(self.instance.COL_funcao)

        # Grupos litúrgicos
        grupos = TBGRUPOS.objects.filter(GRU_ativo=True).order_by('GRU_nome_grupo')
        choices_grupos = [('', 'Selecione um grupo...')]
        choices_grupos.extend([(str(grupo.GRU_id), grupo.GRU_nome_grupo) for grupo in grupos])
        self.fields['COL_grupo_liturgico'].choices = choices_grupos

        if self.instance and self.instance.pk and self.instance.COL_grupo_liturgico:
            self.fields['COL_grupo_liturgico'].initial = str(self.instance.COL_grupo_liturgico)

    def clean_COL_funcao(self):
        """Converte string vazia para None"""
        value = self.cleaned_data.get('COL_funcao')
        if value == '' or value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def clean_COL_grupo_liturgico(self):
        """Converte string vazia para None"""
        value = self.cleaned_data.get('COL_grupo_liturgico')
        if value in ('', None):
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    class Meta:
        model = TBCOLABORADORES
        fields = [
            'COL_telefone', 'COL_nome_completo', 'COL_apelido',
            'COL_cep', 'COL_endereco', 'COL_numero', 'COL_complemento',
            'COL_bairro', 'COL_cidade', 'COL_estado',
            'COL_data_nascimento', 'COL_sexo', 'COL_estado_civil',
            'COL_foto', 'COL_status', 'COL_funcao', 'COL_grupo_liturgico',
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
            'COL_grupo_liturgico': forms.Select(attrs={
                'class': 'form-control',
                'id': 'COL_grupo_liturgico'
            }),
        }
