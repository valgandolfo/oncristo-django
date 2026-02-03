"""Formulário de Celebrantes (TBCELEBRANTES)."""
from django import forms

from ...models.area_admin.models_celebrantes import TBCELEBRANTES


class CelebranteForm(forms.ModelForm):
    class Meta:
        model = TBCELEBRANTES
        fields = ['CEL_nome_celebrante', 'CEL_ordenacao', 'CEL_foto', 'CEL_ativo']
        widgets = {
            'CEL_nome_celebrante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do celebrante', 'id': 'CEL_nome_celebrante'}),
            'CEL_ordenacao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ordenação (ex: Padre, Diácono)', 'id': 'CEL_ordenacao'}),
            'CEL_foto': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'id': 'CEL_foto'}),
            'CEL_ativo': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'CEL_ativo'}),
        }
