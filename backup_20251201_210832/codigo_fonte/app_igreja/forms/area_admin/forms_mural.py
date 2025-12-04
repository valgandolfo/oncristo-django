from django import forms
from app_igreja.models.area_admin.models_mural import TBMURAL
from .forms_commons import DateInputWidget


class MuralForm(forms.ModelForm):
    class Meta:
        model = TBMURAL
        fields = [
            'MUR_data_mural',
            'MUR_titulo_mural',
            'MUR_foto1_mural',
            'MUR_foto2_mural',
            'MUR_foto3_mural',
            'MUR_foto4_mural',
            'MUR_foto5_mural',
            'MUR_legenda1_mural',
            'MUR_legenda2_mural',
            'MUR_legenda3_mural',
            'MUR_legenda4_mural',
            'MUR_legenda5_mural',
            'MUR_ativo'
        ]
        widgets = {
            'MUR_data_mural': DateInputWidget(attrs={
                'class': 'form-control'
            }),
            'MUR_titulo_mural': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o título do mural',
                'maxlength': '255'
            }),
            'MUR_foto1_mural': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'MUR_foto2_mural': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'MUR_foto3_mural': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'MUR_foto4_mural': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'MUR_foto5_mural': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'MUR_legenda1_mural': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Legenda para a foto 1',
                'maxlength': '255'
            }),
            'MUR_legenda2_mural': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Legenda para a foto 2',
                'maxlength': '255'
            }),
            'MUR_legenda3_mural': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Legenda para a foto 3',
                'maxlength': '255'
            }),
            'MUR_legenda4_mural': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Legenda para a foto 4',
                'maxlength': '255'
            }),
            'MUR_legenda5_mural': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Legenda para a foto 5',
                'maxlength': '255'
            }),
            'MUR_ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'MUR_data_mural': 'Data do Mural',
            'MUR_titulo_mural': 'Título do Mural',
            'MUR_foto1_mural': 'Foto 1',
            'MUR_foto2_mural': 'Foto 2',
            'MUR_foto3_mural': 'Foto 3',
            'MUR_foto4_mural': 'Foto 4',
            'MUR_foto5_mural': 'Foto 5',
            'MUR_legenda1_mural': 'Legenda Foto 1',
            'MUR_legenda2_mural': 'Legenda Foto 2',
            'MUR_legenda3_mural': 'Legenda Foto 3',
            'MUR_legenda4_mural': 'Legenda Foto 4',
            'MUR_legenda5_mural': 'Legenda Foto 5',
            'MUR_ativo': 'Mural Ativo'
        }
        help_texts = {
            'MUR_data_mural': 'Data de publicação do mural',
            'MUR_titulo_mural': 'Digite o título do mural',
            'MUR_foto1_mural': 'Primeira foto do mural (obrigatória)',
            'MUR_foto2_mural': 'Segunda foto do mural (opcional)',
            'MUR_foto3_mural': 'Terceira foto do mural (opcional)',
            'MUR_foto4_mural': 'Quarta foto do mural (opcional)',
            'MUR_foto5_mural': 'Quinta foto do mural (opcional)',
            'MUR_legenda1_mural': 'Legenda para a primeira foto',
            'MUR_legenda2_mural': 'Legenda para a segunda foto',
            'MUR_legenda3_mural': 'Legenda para a terceira foto',
            'MUR_legenda4_mural': 'Legenda para a quarta foto',
            'MUR_legenda5_mural': 'Legenda para a quinta foto',
            'MUR_ativo': 'Se marcado, o mural aparecerá na visualização pública'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adicionar classes CSS aos campos
        for field_name, field in self.fields.items():
            if field.widget.attrs.get('class'):
                continue
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-control'
    
    def clean_MUR_titulo_mural(self):
        titulo = self.cleaned_data.get('MUR_titulo_mural')
        
        if titulo:
            # Remover espaços extras
            titulo = titulo.strip()
            
            # Verificar se não está vazio após remoção de espaços
            if not titulo:
                raise forms.ValidationError('O título do mural não pode estar vazio.')
        
        return titulo
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Verificar se pelo menos uma foto foi enviada (apenas na criação)
        if not self.instance.pk:  # Criação
            foto1 = cleaned_data.get('MUR_foto1_mural')
            foto2 = cleaned_data.get('MUR_foto2_mural')
            foto3 = cleaned_data.get('MUR_foto3_mural')
            foto4 = cleaned_data.get('MUR_foto4_mural')
            foto5 = cleaned_data.get('MUR_foto5_mural')
            
            if not any([foto1, foto2, foto3, foto4, foto5]):
                raise forms.ValidationError('É necessário enviar pelo menos uma foto.')
        
        return cleaned_data

