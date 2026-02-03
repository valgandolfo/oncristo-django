from django import forms
from ...models.area_admin.models_mural import TBMURAL
from .forms_commons import DateInputWidget

_attrs = lambda **kw: {**{'class': 'form-control'}, **kw}
_FILE_IMG = _attrs(accept='image/*')
_LEGENDA = lambda n: _attrs(placeholder=f'Legenda para a foto {n}', maxlength='255')


class MuralForm(forms.ModelForm):
    """Formulário para Mural de Fotos."""

    class Meta:
        model = TBMURAL
        fields = [
            'MUR_data_mural', 'MUR_titulo_mural',
            'MUR_foto1_mural', 'MUR_foto2_mural', 'MUR_foto3_mural',
            'MUR_foto4_mural', 'MUR_foto5_mural',
            'MUR_legenda1_mural', 'MUR_legenda2_mural', 'MUR_legenda3_mural',
            'MUR_legenda4_mural', 'MUR_legenda5_mural',
            'MUR_ativo'
        ]
        widgets = {
            'MUR_data_mural': DateInputWidget(attrs=_attrs()),
            'MUR_titulo_mural': forms.TextInput(attrs=_attrs(placeholder='Digite o título do mural', maxlength='255')),
            'MUR_foto1_mural': forms.FileInput(attrs=_FILE_IMG),
            'MUR_foto2_mural': forms.FileInput(attrs=_FILE_IMG),
            'MUR_foto3_mural': forms.FileInput(attrs=_FILE_IMG),
            'MUR_foto4_mural': forms.FileInput(attrs=_FILE_IMG),
            'MUR_foto5_mural': forms.FileInput(attrs=_FILE_IMG),
            'MUR_legenda1_mural': forms.TextInput(attrs=_LEGENDA(1)),
            'MUR_legenda2_mural': forms.TextInput(attrs=_LEGENDA(2)),
            'MUR_legenda3_mural': forms.TextInput(attrs=_LEGENDA(3)),
            'MUR_legenda4_mural': forms.TextInput(attrs=_LEGENDA(4)),
            'MUR_legenda5_mural': forms.TextInput(attrs=_LEGENDA(5)),
            'MUR_ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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
            'MUR_ativo': 'Mural Ativo',
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
            'MUR_ativo': 'Se marcado, o mural aparecerá na visualização pública',
        }

    def clean_MUR_titulo_mural(self):
        titulo = self.cleaned_data.get('MUR_titulo_mural')
        if titulo and not titulo.strip():
            raise forms.ValidationError('O título do mural não pode estar vazio.')
        return titulo.strip() if titulo else titulo

    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.pk:
            fotos = [
                cleaned_data.get('MUR_foto1_mural'),
                cleaned_data.get('MUR_foto2_mural'),
                cleaned_data.get('MUR_foto3_mural'),
                cleaned_data.get('MUR_foto4_mural'),
                cleaned_data.get('MUR_foto5_mural'),
            ]
            if not any(fotos):
                raise forms.ValidationError('É necessário enviar pelo menos uma foto.')
        return cleaned_data
