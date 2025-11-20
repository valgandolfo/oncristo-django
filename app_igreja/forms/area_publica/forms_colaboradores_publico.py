"""
==================== FORMULÁRIO PÚBLICO DE COLABORADORES ====================
Formulário simplificado para cadastro público de colaboradores
Usa telefone como chave única
"""

from django import forms
from django.core.exceptions import ValidationError
from ...models.area_admin.models_colaboradores import TBCOLABORADORES
import re


def limpar_telefone(telefone):
    """Remove caracteres não numéricos do telefone"""
    if not telefone:
        return None
    return re.sub(r'[^\d]', '', str(telefone))


class ColaboradorPublicoForm(forms.ModelForm):
    """
    Formulário público simplificado para cadastro de colaboradores
    """
    
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
        ]
        widgets = {
            'COL_telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Telefone',
                'id': 'COL_telefone',
                'readonly': True,
                'style': 'background-color: #f8f9fa;'
            }),
            'COL_nome_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo',
                'id': 'COL_nome_completo',
                'required': True
            }),
            'COL_apelido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apelido (como gosta de ser chamado)',
                'id': 'COL_apelido'
            }),
            'COL_cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000',
                'id': 'COL_cep',
                'maxlength': '9'
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
                'placeholder': 'Complemento (Apto, Casa, etc.)',
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
            'COL_estado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'UF',
                'id': 'COL_estado',
                'maxlength': '2'
            }),
            'COL_data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
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
                ('Solteiro', 'Solteiro'),
                ('Casado', 'Casado'),
                ('Divorciado', 'Divorciado'),
                ('Viúvo', 'Viúvo'),
                ('Separado', 'Separado')
            ]),
            'COL_funcao_pretendida': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Cantor, Músico, Leitor, etc.',
                'id': 'COL_funcao_pretendida'
            }),
            'COL_foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'COL_foto'
            }),
        }
    
    def clean_COL_telefone(self):
        """Valida e limpa o telefone"""
        telefone = self.cleaned_data.get('COL_telefone')
        if telefone:
            telefone_limpo = limpar_telefone(telefone)
            if len(telefone_limpo) < 10:
                raise ValidationError('Telefone deve ter pelo menos 10 dígitos')
            return telefone_limpo
        return telefone
    
    def clean_COL_cep(self):
        """Valida e formata o CEP"""
        cep = self.cleaned_data.get('COL_cep')
        if cep:
            cep_limpo = re.sub(r'[^\d]', '', str(cep))
            if len(cep_limpo) != 8:
                raise ValidationError('CEP deve ter 8 dígitos')
            return f"{cep_limpo[:5]}-{cep_limpo[5:]}"
        return cep
    
    def save(self, commit=True):
        """Override save para definir status como PENDENTE"""
        instance = super().save(commit=False)
        instance.COL_status = 'PENDENTE'  # Sempre inicia como pendente
        if commit:
            instance.save()
        return instance

