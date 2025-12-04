from django import forms

from app_igreja.models.area_admin.models_modelo import (
    TBMODELO,
    TBITEM_MODELO,
    OCORRENCIA_CHOICES,
)
from .forms_commons import DateInputWidget


class ModeloForm(forms.ModelForm):
    MOD_DATA_CRIACAO = forms.DateField(
        label='Data de Criação',
        required=False,
        widget=DateInputWidget(attrs={'class': 'form-control', 'readonly': True})
    )
    MOD_DATA_ALTERACAO = forms.DateField(
        label='Data de Alteração',
        required=False,
        widget=DateInputWidget(attrs={'class': 'form-control', 'readonly': True})
    )

    class Meta:
        model = TBMODELO
        fields = ['MOD_DESCRICAO']
        widgets = {
            'MOD_DESCRICAO': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição do modelo',
                'maxlength': '100'
            })
        }
        labels = {
            'MOD_DESCRICAO': 'Descrição do Modelo'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['MOD_DATA_CRIACAO'].initial = self.instance.MOD_DATA_CRIACAO
            self.fields['MOD_DATA_ALTERACAO'].initial = self.instance.MOD_DATA_ALTERACAO


class ItemModeloForm(forms.ModelForm):
    ITEM_MOD_OCORRENCIA = forms.MultipleChoiceField(
        label='Ocorrências',
        required=True,
        choices=OCORRENCIA_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = TBITEM_MODELO
        fields = ['ITEM_MOD_MODELO', 'ITEM_MOD_ENCARGO', 'ITEM_MOD_OCORRENCIA']
        widgets = {
            'ITEM_MOD_MODELO': forms.Select(attrs={'class': 'form-select'}),
            'ITEM_MOD_ENCARGO': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição do encargo',
                'maxlength': '100'
            })
        }
        labels = {
            'ITEM_MOD_MODELO': 'Modelo',
            'ITEM_MOD_ENCARGO': 'Encargo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ITEM_MOD_MODELO'].queryset = TBMODELO.objects.order_by('MOD_DESCRICAO')
        if self.instance and self.instance.pk:
            ocorrencias = self.instance.ITEM_MOD_OCORRENCIA or ''
            self.initial['ITEM_MOD_OCORRENCIA'] = [valor for valor in ocorrencias.split(',') if valor]

    def clean_ITEM_MOD_OCORRENCIA(self):
        values = self.cleaned_data['ITEM_MOD_OCORRENCIA']
        return ','.join(values)
