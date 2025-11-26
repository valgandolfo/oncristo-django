"""
==================== FORMULÁRIOS DE GERENCIAMENTO DE DÍZIMOS ====================
Arquivo com formulários para gerenciar coletas de dízimos
"""

from django import forms
from datetime import date
from ...models.area_admin.models_dizimistas import TBDIZIMISTAS


class GerarMensalidadeDizimoForm(forms.Form):
    """
    Formulário para gerar mensalidades de dizimistas
    """
    
    MES_CHOICES = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
    ]
    
    ano = forms.IntegerField(
        label="Ano",
        min_value=2020,
        max_value=2100,
        initial=date.today().year,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '2020', 'max': '2100'})
    )
    
    mes = forms.ChoiceField(
        label="Mês",
        choices=MES_CHOICES,
        initial=date.today().month,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    dizimista = forms.ModelChoiceField(
        queryset=TBDIZIMISTAS.objects.filter(DIS_status=True).order_by('DIS_nome'),
        label="Dizimista",
        required=False,
        empty_label="Todos os Dizimistas Ativos",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def clean_mes(self):
        mes = self.cleaned_data.get('mes')
        if mes:
            try:
                return int(mes)
            except (ValueError, TypeError):
                raise forms.ValidationError("Mês inválido.")
        return mes
    
    def clean_ano(self):
        ano = self.cleaned_data.get('ano')
        if ano and (ano < 2020 or ano > 2100):
            raise forms.ValidationError("Ano deve estar entre 2020 e 2100.")
        return ano


class BuscarColetaDizimoForm(forms.Form):
    """
    Formulário para buscar/filtrar coletas de dízimos
    """
    
    MES_CHOICES = [
        (0, 'Todos'),
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
    ]
    
    STATUS_CHOICES = [
        ('TODOS', 'Todos'),
        ('PAGOS', 'Pagos'),
        ('EM_ABERTO', 'Em Aberto'),
        ('PARCIAL', 'Parcialmente'),
    ]
    
    mes = forms.ChoiceField(
        label="Mês",
        choices=MES_CHOICES,
        initial=date.today().month,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    ano = forms.IntegerField(
        label="Ano",
        min_value=2020,
        max_value=2100,
        initial=date.today().year,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '2020', 'max': '2100'})
    )
    
    dizimista = forms.ModelChoiceField(
        queryset=TBDIZIMISTAS.objects.filter(DIS_status=True).order_by('DIS_nome'),
        label="Dizimista",
        required=False,
        empty_label="Todos",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        label="Status",
        choices=STATUS_CHOICES,
        initial='TODOS',
        required=False,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )


class BaixarDizimoForm(forms.Form):
    """
    Formulário para baixar (registrar pagamento) de dízimo
    """
    
    data_pagamento = forms.DateField(
        label="Data Pagamento",
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'data_pagamento_baixa'
        })
    )
    
    valor_pago = forms.DecimalField(
        label="Valor Pago",
        max_digits=10,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'id': 'valor_pago_baixa',
            'placeholder': '0.00'
        })
    )
    
    observacao = forms.CharField(
        label="Observação",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'observacao_baixa',
            'placeholder': 'Observações sobre o pagamento'
        })
    )
