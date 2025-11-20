"""
==================== FORMULÁRIOS DE BANNERS ====================
Arquivo com formulários específicos para Banners de Patrocinadores
"""

from django import forms
from django.core.exceptions import ValidationError
from ...models.area_admin.models_banners import TBBANNERS
from .forms_commons import BaseAdminForm


class BannerForm(BaseAdminForm):
    """Formulário para cadastro de banners de patrocinadores"""
    
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
            'BAN_NOME_PATROCINADOR': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do patrocinador ou empresa',
                'required': True
            }),
            'BAN_DESCRICAO_COMERCIAL': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Breve descrição do negócio ou serviço',
                'rows': 3,
                'maxlength': 255
            }),
            'BAN_IMAGE': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'onchange': 'previewBannerImage(this)'
            }),
            'BAN_LINK': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.exemplo.com.br',
                'maxlength': 50
            }),
            'BAN_TELEFONE': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000'
            }),
            'BAN_ENDERECO': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Endereço completo do patrocinador'
            }),
            'BAN_ORDEM': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': 0,
                'step': 1,
                'help_text': 'Ordem de exibição. Use 0 para inativar o banner.'
            }),
        }
        labels = {
            'BAN_NOME_PATROCINADOR': 'Nome do Patrocinador',
            'BAN_DESCRICAO_COMERCIAL': 'Descrição Comercial',
            'BAN_IMAGE': 'Imagem do Banner',
            'BAN_LINK': 'Link (URL)',
            'BAN_TELEFONE': 'Telefone',
            'BAN_ENDERECO': 'Endereço',
            'BAN_ORDEM': 'Ordem de Exibição'
        }
        help_texts = {
            'BAN_NOME_PATROCINADOR': 'Nome do patrocinador ou empresa',
            'BAN_DESCRICAO_COMERCIAL': 'Breve descrição do negócio ou serviço (máximo 255 caracteres)',
            'BAN_IMAGE': 'Imagem do banner do patrocinador',
            'BAN_LINK': 'URL do site do patrocinador (máximo 50 caracteres, opcional)',
            'BAN_TELEFONE': 'Telefone de contato (opcional)',
            'BAN_ENDERECO': 'Endereço completo do patrocinador (opcional)',
            'BAN_ORDEM': 'Ordem de exibição. Se for 0 (zero), o banner está inativo.'
        }
    
    def clean_BAN_ORDEM(self):
        """Validação da ordem"""
        ordem = self.cleaned_data.get('BAN_ORDEM')
        if ordem is not None and ordem < 0:
            raise ValidationError("A ordem deve ser um número positivo ou zero.")
        return ordem
    
    def clean_BAN_LINK(self):
        """Validação do link"""
        link = self.cleaned_data.get('BAN_LINK')
        if link:
            # Adicionar http:// se não tiver protocolo
            if not link.startswith(('http://', 'https://')):
                link = 'https://' + link
        return link
    
    def clean_BAN_IMAGE(self):
        """Validação da imagem"""
        imagem = self.cleaned_data.get('BAN_IMAGE')
        
        # Se estiver editando e não houver nova imagem, manter a existente
        if not imagem and self.instance and self.instance.pk:
            return self.instance.BAN_IMAGE
        
        # Se imagem for um arquivo novo (não é ImageFieldFile)
        if imagem and hasattr(imagem, 'content_type'):
            # Validar tamanho (máximo 5MB)
            if imagem.size > 5 * 1024 * 1024:
                raise ValidationError('A imagem deve ter no máximo 5MB.')
            
            # Validar formato
            if not imagem.content_type.startswith('image/'):
                raise ValidationError('O arquivo deve ser uma imagem.')
        
        return imagem
