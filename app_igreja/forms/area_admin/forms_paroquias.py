"""Formulários de Paróquias (TBPAROQUIA) e horários fixos."""
from datetime import datetime

from django import forms

from ...models.area_admin.models_paroquias import TBPAROQUIA
from .forms_commons import BaseAdminForm, get_estados_brasil, get_tipos_pix

DIAS_SEMANA = ['domingo', 'segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado']


class ParoquiaForm(BaseAdminForm):
    class Meta:
        model = TBPAROQUIA
        fields = [
            'PAR_nome_paroquia', 'PAR_diocese', 'PAR_cep', 'PAR_endereco', 'PAR_numero',
            'PAR_cidade', 'PAR_uf', 'PAR_bairro', 'PAR_telefone', 'PAR_email',
            'PAR_paroco', 'PAR_foto_paroco', 'PAR_secretario',
            'PAR_cnpj', 'PAR_banco', 'PAR_agencia', 'PAR_conta',
            'PAR_pix_chave', 'PAR_pix_tipo', 'PAR_pix_beneficiario', 'PAR_pix_cidade', 'PAR_pix_uf',
            'PAR_url_youtube', 'PAR_url_facebook', 'PAR_url_instagram'
        ]
        widgets = {
            'PAR_nome_paroquia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o nome da paróquia'}),
            'PAR_diocese': forms.Select(attrs={'class': 'form-control'}),
            'PAR_cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000', 'id': 'PAR_cep'}),
            'PAR_endereco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o endereço', 'id': 'PAR_endereco'}),
            'PAR_numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número', 'id': 'PAR_numero'}),
            'PAR_cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite a cidade', 'id': 'PAR_cidade'}),
            'PAR_uf': forms.Select(attrs={'class': 'form-control', 'id': 'PAR_uf'}, choices=[('', 'Selecione UF')] + list(get_estados_brasil())),
            'PAR_bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o bairro', 'id': 'PAR_bairro'}),
            'PAR_telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'PAR_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemplo.com'}),
            'PAR_paroco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do pároco'}),
            'PAR_foto_paroco': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'PAR_secretario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do secretário(a)'}),
            'PAR_cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0000-00'}),
            'PAR_banco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do banco'}),
            'PAR_agencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0000'}),
            'PAR_conta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-0'}),
            'PAR_pix_chave': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Chave PIX'}),
            'PAR_pix_tipo': forms.Select(attrs={'class': 'form-control'}, choices=[('', 'Selecione tipo')] + list(get_tipos_pix())),
            'PAR_pix_beneficiario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do beneficiário'}),
            'PAR_pix_cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade do beneficiário'}),
            'PAR_pix_uf': forms.Select(attrs={'class': 'form-control'}, choices=[('', 'Selecione UF')] + list(get_estados_brasil())),
            'PAR_url_youtube': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.youtube.com/@canalparoquia'}),
            'PAR_url_facebook': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.facebook.com/paroquia'}),
            'PAR_url_instagram': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.instagram.com/paroquia'}),
        }


def _horario_field(label, placeholder='Ex: 07:00, 19:00'):
    return forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': placeholder}),
        required=False, label=label, help_text='Horários separados por vírgula (HH:MM)'
    )


class ParoquiaHorariosForm(forms.ModelForm):
    domingo_horarios = _horario_field('Domingo', 'Ex: 07:00, 09:00, 18:00')
    segunda_horarios = _horario_field('Segunda-feira')
    terca_horarios = _horario_field('Terça-feira')
    quarta_horarios = _horario_field('Quarta-feira')
    quinta_horarios = _horario_field('Quinta-feira')
    sexta_horarios = _horario_field('Sexta-feira')
    sabado_horarios = _horario_field('Sábado')

    class Meta:
        model = TBPAROQUIA
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            horarios_fixos = self.instance.get_horarios_fixos()
            for dia in DIAS_SEMANA:
                self.fields[f'{dia}_horarios'].initial = ', '.join(horarios_fixos.get(dia, []))

    def clean(self):
        cleaned_data = super().clean()
        for dia in DIAS_SEMANA:
            valor = cleaned_data.get(f'{dia}_horarios', '')
            if valor:
                for horario in [h.strip() for h in valor.split(',') if h.strip()]:
                    try:
                        datetime.strptime(horario, '%H:%M')
                    except ValueError:
                        raise forms.ValidationError(f'Horário inválido no {dia}: {horario}. Use HH:MM (ex: 07:00)')
        return cleaned_data

    def save(self, commit=True):
        horarios_fixos = {}
        for dia in DIAS_SEMANA:
            raw = (self.cleaned_data.get(f'{dia}_horarios') or '').strip()
            horarios_fixos[dia] = [h.strip() for h in raw.split(',') if h.strip()]
        self.instance.set_horarios_fixos(horarios_fixos)
        if commit:
            self.instance.save()
        return self.instance
