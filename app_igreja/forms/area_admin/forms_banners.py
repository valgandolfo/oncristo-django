from django import forms
from ...models.area_admin.models_banners import TBBANNERS
from .forms_commons import BaseAdminForm

_attrs = lambda **kw: {**{'class': 'form-control'}, **kw}
MAX_IMAGE_MB = 5


class BannerForm(BaseAdminForm):
    """Formulário para Banners de Patrocinadores."""

    class Meta:
        model = TBBANNERS
        fields = [
            'BAN_NOME_PATROCINADOR',
            'BAN_DESCRICAO_COMERCIAL',
            'BAN_IMAGE',
            'BAN_LINK',
            'BAN_TELEFONE',
            'BAN_ENDERECO',
            'BAN_ORDEM'
        ]
        widgets = {
            'BAN_NOME_PATROCINADOR': forms.TextInput(attrs=_attrs(placeholder='Nome do patrocinador ou empresa')),
            'BAN_DESCRICAO_COMERCIAL': forms.Textarea(attrs=_attrs(placeholder='Breve descrição do negócio ou serviço', rows=3, maxlength=255)),
            'BAN_IMAGE': forms.FileInput(attrs=_attrs(accept='image/*', onchange='previewBannerImage(this)')),
            'BAN_LINK': forms.URLInput(attrs=_attrs(placeholder='https://www.exemplo.com.br', maxlength=50)),
            'BAN_TELEFONE': forms.TextInput(attrs=_attrs(placeholder='(00) 00000-0000')),
            'BAN_ENDERECO': forms.TextInput(attrs=_attrs(placeholder='Endereço completo do patrocinador')),
            'BAN_ORDEM': forms.NumberInput(attrs=_attrs(placeholder='0', min=0, step=1)),
        }
        labels = {
            'BAN_NOME_PATROCINADOR': 'Nome do Patrocinador',
            'BAN_DESCRICAO_COMERCIAL': 'Descrição Comercial',
            'BAN_IMAGE': 'Imagem do Banner',
            'BAN_LINK': 'Link (URL)',
            'BAN_TELEFONE': 'Telefone',
            'BAN_ENDERECO': 'Endereço',
            'BAN_ORDEM': 'Ordem de Exibição',
        }
        help_texts = {
            'BAN_NOME_PATROCINADOR': 'Nome do patrocinador ou empresa',
            'BAN_DESCRICAO_COMERCIAL': 'Breve descrição do negócio ou serviço (máximo 255 caracteres)',
            'BAN_IMAGE': 'Imagem do banner do patrocinador',
            'BAN_LINK': 'URL do site do patrocinador (máximo 50 caracteres, opcional)',
            'BAN_TELEFONE': 'Telefone de contato (opcional)',
            'BAN_ENDERECO': 'Endereço completo do patrocinador (opcional)',
            'BAN_ORDEM': 'Ordem de exibição. Se for 0 (zero), o banner está inativo.',
        }

    def clean_BAN_ORDEM(self):
        ordem = self.cleaned_data.get('BAN_ORDEM')
        if ordem is not None and ordem < 0:
            raise forms.ValidationError("A ordem deve ser um número positivo ou zero.")
        return ordem

    def clean_BAN_LINK(self):
        link = self.cleaned_data.get('BAN_LINK')
        if link and not link.startswith(('http://', 'https://')):
            return 'https://' + link
        return link

    def clean_BAN_IMAGE(self):
        imagem = self.cleaned_data.get('BAN_IMAGE')
        if not imagem and self.instance and self.instance.pk:
            return self.instance.BAN_IMAGE
        if imagem and hasattr(imagem, 'content_type'):
            if imagem.size > MAX_IMAGE_MB * 1024 * 1024:
                raise forms.ValidationError('A imagem deve ter no máximo 5MB.')
            if not imagem.content_type.startswith('image/'):
                raise forms.ValidationError('O arquivo deve ser uma imagem.')
        return imagem
