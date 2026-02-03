"""Formulários da agenda do mês (seleção mês/ano e item do dia)."""
from datetime import date

from django import forms

from ...models.area_admin.models_modelo import TBMODELO

_attrs = lambda **kw: dict({'class': 'form-control'}, **kw)

MES_CHOICES = [
    (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
    (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
    (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro'),
]


class AgendaMesForm(forms.Form):
    """Seleção de mês e ano."""

    mes = forms.ChoiceField(label="Mês", choices=MES_CHOICES, widget=forms.Select(attrs=_attrs()))
    ano = forms.IntegerField(
        label="Ano",
        min_value=2020,
        max_value=2100,
        initial=date.today().year,
        widget=forms.NumberInput(attrs=_attrs(min='2020', max='2100'))
    )


class AgendaDiaForm(forms.Form):
    """Item do dia: modelo, horário e encargos."""

    modelo = forms.ModelChoiceField(
        queryset=TBMODELO.objects.all().order_by('MOD_DESCRICAO'),
        label="Modelo",
        required=False,
        empty_label="Selecione um modelo...",
        widget=forms.Select(attrs=_attrs())
    )
    horario = forms.TimeField(
        label="Horário",
        required=False,
        widget=forms.TimeInput(attrs=_attrs(type='time', placeholder='HH:MM'))
    )
    encargos = forms.CharField(
        label="Encargos",
        required=False,
        widget=forms.Textarea(attrs=_attrs(rows=5, placeholder='Digite os encargos do dia...'))
    )
