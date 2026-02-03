from django import forms

from ...models.area_admin.models_avisos import TBAVISO
from .forms_commons import DateInputWidget


class AvisoForm(forms.ModelForm):
    class Meta:
        model = TBAVISO
        fields = ['AVI_titulo', 'AVI_texto', 'AVI_data']
        widgets = {
            'AVI_titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o título do aviso...',
                'maxlength': '255',
                'id': 'AVI_titulo'
            }),
            'AVI_texto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o texto do aviso...',
                'maxlength': '255',
                'id': 'AVI_texto'
            }),
            'AVI_data': DateInputWidget(attrs={
                'class': 'form-control',
                'id': 'AVI_data'
            }),
        }
        labels = {
            'AVI_titulo': 'Título do Aviso',
            'AVI_texto': 'Texto do Aviso',
            'AVI_data': 'Data do Aviso',
        }
        help_texts = {
            'AVI_titulo': 'Título que será exibido',
            'AVI_texto': 'Conteúdo do aviso',
            'AVI_data': 'Data de cadastro do aviso',
        }
    
    def clean_AVI_titulo(self):
        titulo = self.cleaned_data.get('AVI_titulo')
        if not titulo:
            raise forms.ValidationError('O título é obrigatório.')
        if len(titulo.strip()) < 3:
            raise forms.ValidationError('O título deve ter pelo menos 3 caracteres.')
        return titulo.strip()
    
    def clean_AVI_texto(self):
        texto = self.cleaned_data.get('AVI_texto')
        if not texto:
            raise forms.ValidationError('O texto é obrigatório.')
        if len(texto.strip()) < 3:
            raise forms.ValidationError('O texto deve ter pelo menos 3 caracteres.')
        return texto.strip()
