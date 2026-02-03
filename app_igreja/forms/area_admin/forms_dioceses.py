"""Formulário de Diocese (TBDIOCESE) - registro único."""
from django import forms

from ...models.area_admin.models_dioceses import TBDIOCESE
from .forms_commons import BaseAdminForm, get_estados_brasil

_attrs = lambda **kw: {**{'class': 'form-control'}, **kw}


class dioceseform(BaseAdminForm):
    class Meta:
        model = TBDIOCESE
        fields = [
            'DIO_nome_diocese', 'DIO_nome_bispo', 'DIO_foto_bispo',
            'DIO_cep', 'DIO_endereco', 'DIO_numero', 'DIO_complemento',
            'DIO_bairro', 'DIO_cidade', 'DIO_uf',
            'DIO_telefone', 'DIO_email', 'DIO_site',
        ]
        widgets = {
            'DIO_nome_diocese': forms.TextInput(attrs=_attrs(placeholder='Nome da Diocese', id='DIO_nome_diocese')),
            'DIO_nome_bispo': forms.TextInput(attrs=_attrs(placeholder='Nome do Bispo', id='DIO_nome_bispo')),
            'DIO_foto_bispo': forms.FileInput(attrs=_attrs(accept='image/*', id='DIO_foto_bispo')),
            'DIO_cep': forms.TextInput(attrs=_attrs(placeholder='00000-000', id='DIO_cep')),
            'DIO_endereco': forms.TextInput(attrs=_attrs(placeholder='Digite o endereço', id='DIO_endereco')),
            'DIO_numero': forms.TextInput(attrs=_attrs(placeholder='Número', id='DIO_numero')),
            'DIO_complemento': forms.TextInput(attrs=_attrs(placeholder='Complemento (apto, sala, etc.)', id='DIO_complemento')),
            'DIO_bairro': forms.TextInput(attrs=_attrs(placeholder='Bairro', id='DIO_bairro')),
            'DIO_cidade': forms.TextInput(attrs=_attrs(placeholder='Cidade', id='DIO_cidade')),
            'DIO_uf': forms.Select(attrs=_attrs(id='DIO_uf'), choices=[('', 'Selecione UF')] + list(get_estados_brasil())),
            'DIO_telefone': forms.TextInput(attrs=_attrs(placeholder='(00) 0000-0000', id='DIO_telefone')),
            'DIO_email': forms.EmailInput(attrs=_attrs(placeholder='email@diocese.com.br', id='DIO_email')),
            'DIO_site': forms.URLInput(attrs=_attrs(placeholder='https://www.diocese.com.br', id='DIO_site')),
        }
