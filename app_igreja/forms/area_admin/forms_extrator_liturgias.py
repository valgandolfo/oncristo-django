from django import forms
from ...models.area_admin.models_extrator_liturgias import TBLITURGIA

class LiturgiaForm(forms.ModelForm):
    class Meta:
        model = TBLITURGIA
        fields = ['LIT_DATALIT', 'LIT_TIPOLIT', 'LIT_TEXTO', 'LIT_STATUSLIT']
        widgets = {
            'LIT_DATALIT': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'LIT_DATALIT'
            }),
            'LIT_TIPOLIT': forms.Select(attrs={
                'class': 'form-select',
                'id': 'LIT_TIPOLIT'
            }),
            'LIT_TEXTO': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o texto da liturgia...',
                'rows': '10',
                'id': 'LIT_TEXTO'
            }),
            'LIT_STATUSLIT': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'LIT_STATUSLIT'
            }),
        }
        labels = {
            'LIT_DATALIT': 'Data da Liturgia',
            'LIT_TIPOLIT': 'Tipo de Liturgia',
            'LIT_TEXTO': 'Texto da Liturgia',
            'LIT_STATUSLIT': 'Status Ativo',
        }
        help_texts = {
            'LIT_DATALIT': 'Data para a qual a liturgia se aplica',
            'LIT_TIPOLIT': 'Tipo da leitura litúrgica (ex: Primeira Leitura, Evangelho)',
            'LIT_TEXTO': 'Conteúdo completo da liturgia',
            'LIT_STATUSLIT': 'Marque para ativar a liturgia',
        }
    
    def clean_LIT_TIPOLIT(self):
        tipo = self.cleaned_data.get('LIT_TIPOLIT')
        if not tipo:
            raise forms.ValidationError('O tipo de liturgia é obrigatório.')
        if len(tipo.strip()) < 3:
            raise forms.ValidationError('O tipo de liturgia deve ter pelo menos 3 caracteres.')
        return tipo.strip()
    
    def clean_LIT_TEXTO(self):
        texto = self.cleaned_data.get('LIT_TEXTO')
        if not texto:
            raise forms.ValidationError('O texto da liturgia é obrigatório.')
        if len(texto.strip()) < 10:
            raise forms.ValidationError('O texto deve ter pelo menos 10 caracteres.')
        return texto.strip()

