"""
==================== FORMULÁRIOS DE CONFIGURAÇÕES VISUAIS ====================
Arquivo com formulários específicos para Configurações Visuais
"""

from django import forms
from ...models.area_admin.models_visual import TBVISUAL
from .forms_commons import BaseAdminForm


class VisualForm(BaseAdminForm):
    """Formulário para Configurações Visuais baseado no model TBVISUAL"""

    class Meta:
        model = TBVISUAL
        fields = [
            'VIS_FOTO_CAPA',
            'VIS_FOTO_BRASAO',
            'VIS_FOTO_PADROEIRO',
            'VIS_FOTO_PRINCIPAL'
        ]
        widgets = {
            'VIS_FOTO_CAPA': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'onchange': 'previewImage(this, "preview-capa")'
            }),
            'VIS_FOTO_BRASAO': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'onchange': 'previewImage(this, "preview-brasao")'
            }),
            'VIS_FOTO_PADROEIRO': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'onchange': 'previewImage(this, "preview-padroeiro")'
            }),
            'VIS_FOTO_PRINCIPAL': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'onchange': 'previewImage(this, "preview-principal")'
            }),
        }
        labels = {
            'VIS_FOTO_CAPA': 'Foto da Paróquia',
            'VIS_FOTO_BRASAO': 'Foto do Brasão (Logo)',
            'VIS_FOTO_PADROEIRO': 'Foto do(a) Santo(a) Padroeiro(a)',
            'VIS_FOTO_PRINCIPAL': 'Imagem Principal (Homepage)',
        }
        help_texts = {
            'VIS_FOTO_CAPA': 'Foto da paróquia',
            'VIS_FOTO_BRASAO': 'Logo ou brasão da paróquia',
            'VIS_FOTO_PADROEIRO': 'Imagem do santo padroeiro da paróquia',
            'VIS_FOTO_PRINCIPAL': 'Imagem principal que aparece no topo da página inicial (dimensões recomendadas: 286x253px)',
        }
    
    def clean_VIS_FOTO_CAPA(self):
        """Validação do tamanho da foto de capa"""
        foto = self.cleaned_data.get('VIS_FOTO_CAPA')
        if foto:
            if foto.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError('A foto de capa deve ter no máximo 5MB.')
        return foto
    
    def clean_VIS_FOTO_BRASAO(self):
        """Validação do tamanho do brasão"""
        foto = self.cleaned_data.get('VIS_FOTO_BRASAO')
        if foto:
            if foto.size > 2 * 1024 * 1024:  # 2MB
                raise forms.ValidationError('O brasão deve ter no máximo 2MB.')
        return foto
    
    def clean_VIS_FOTO_PADROEIRO(self):
        """Validação do tamanho da foto do padroeiro"""
        foto = self.cleaned_data.get('VIS_FOTO_PADROEIRO')
        if foto:
            if foto.size > 3 * 1024 * 1024:  # 3MB
                raise forms.ValidationError('A foto do padroeiro deve ter no máximo 3MB.')
        return foto
    
    def clean_VIS_FOTO_PRINCIPAL(self):
        """Validação do tamanho da imagem principal"""
        foto = self.cleaned_data.get('VIS_FOTO_PRINCIPAL')
        if foto:
            if foto.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError('A imagem principal deve ter no máximo 5MB.')
        return foto

