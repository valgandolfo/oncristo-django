"""
==================== FORMULÁRIO AGENDA DO MÊS ====================
Formulário para criar/editar agenda do mês
"""

from django import forms
from datetime import date
from app_igreja.models.area_admin.models_modelo import TBMODELO
from app_igreja.models.area_admin.models_modelo import OCORRENCIA_CHOICES


class AgendaMesForm(forms.Form):
    """
    Formulário para selecionar mês e ano
    """
    MES_CHOICES = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
    ]
    
    mes = forms.ChoiceField(
        label="Mês",
        choices=MES_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    ano = forms.IntegerField(
        label="Ano",
        min_value=2020,
        max_value=2100,
        initial=date.today().year,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '2020', 'max': '2100'})
    )


class AgendaDiaForm(forms.Form):
    """
    Formulário para criar/editar agenda de um dia específico
    """
    modelo = forms.ModelChoiceField(
        queryset=TBMODELO.objects.all().order_by('MOD_DESCRICAO'),
        label="Modelo",
        required=False,
        empty_label="Selecione um modelo...",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    encargos = forms.CharField(
        label="Encargos",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Digite os encargos do dia...'
        })
    )

