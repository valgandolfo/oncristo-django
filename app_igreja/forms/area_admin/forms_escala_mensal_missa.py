from django import forms
from datetime import date
from app_igreja.models.area_admin.models_modelo import TBMODELO


class EscalaMensalMissaForm(forms.Form):
    """
    Formulário para gerar escala mensal com modelo e tema
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
        label="Mês/Ano",
        choices=MES_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    modelo = forms.ModelChoiceField(
        queryset=TBMODELO.objects.all().order_by('MOD_DESCRICAO'),
        label="Modelo",
        required=True,
        empty_label="Selecione um modelo...",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    tema_mes = forms.CharField(
        label="Tema do Mês",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Advento, Quaresma, etc.'})
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


class EditarDescricaoEscalaMissaForm(forms.Form):
    """
    Formulário para editar descrição de um item da escala
    """
    
    descricao = forms.CharField(
        label="Descrição",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
