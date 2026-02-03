from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from ...models.area_admin.models_celebracoes import TBCELEBRACOES
from .forms_commons import DateInputWidget

_attrs = lambda **kw: dict({'class': 'form-control'}, **kw)


class CelebracaoForm(forms.ModelForm):
    """Formulário para Celebrações Agendadas (admin)."""

    class Meta:
        model = TBCELEBRACOES
        fields = [
            'CEL_tipo_celebracao', 'CEL_data_celebracao', 'CEL_horario', 'CEL_local',
            'CEL_nome_solicitante', 'CEL_telefone', 'CEL_email', 'CEL_participantes',
            'CEL_observacoes', 'CEL_status',
        ]
        widgets = {
            'CEL_tipo_celebracao': forms.Select(attrs=_attrs()),
            'CEL_data_celebracao': DateInputWidget(attrs=_attrs(min=str(date.today()))),
            'CEL_horario': forms.TimeInput(attrs=_attrs(type='time')),
            'CEL_local': forms.TextInput(attrs=_attrs(placeholder='Ex: Igreja Matriz, Capela São José...')),
            'CEL_nome_solicitante': forms.TextInput(attrs=_attrs(placeholder='Nome completo do solicitante')),
            'CEL_telefone': forms.TextInput(attrs=_attrs(placeholder='(11) 99999-9999')),
            'CEL_email': forms.EmailInput(attrs=_attrs(placeholder='email@exemplo.com')),
            'CEL_participantes': forms.NumberInput(attrs=_attrs(min='1', max='1000')),
            'CEL_observacoes': forms.Textarea(attrs=_attrs(rows=3, placeholder='Observações adicionais...')),
            'CEL_status': forms.Select(attrs=_attrs()),
        }
        labels = {
            'CEL_tipo_celebracao': 'Tipo de Celebração',
            'CEL_data_celebracao': 'Data da Celebração',
            'CEL_horario': 'Horário',
            'CEL_local': 'Local',
            'CEL_nome_solicitante': 'Nome do Solicitante',
            'CEL_telefone': 'Telefone',
            'CEL_email': 'E-mail',
            'CEL_participantes': 'Número de Participantes',
            'CEL_observacoes': 'Observações',
            'CEL_status': 'Status',
        }

    def clean_CEL_data_celebracao(self):
        data_celebracao = self.cleaned_data.get('CEL_data_celebracao')
        if data_celebracao and data_celebracao < date.today():
            raise ValidationError('A data da celebração não pode ser anterior à data atual.')
        return data_celebracao

    def clean_CEL_telefone(self):
        telefone = self.cleaned_data.get('CEL_telefone')
        if telefone:
            n = ''.join(filter(str.isdigit, telefone))
            if len(n) < 10 or len(n) > 11:
                raise ValidationError('Telefone deve ter entre 10 e 11 dígitos.')
        return telefone

    def clean_CEL_participantes(self):
        participantes = self.cleaned_data.get('CEL_participantes')
        if participantes is not None:
            if participantes < 1:
                raise ValidationError('O número de participantes deve ser pelo menos 1.')
            if participantes > 1000:
                raise ValidationError('O número de participantes não pode exceder 1000.')
        return participantes

    def clean_CEL_email(self):
        email = self.cleaned_data.get('CEL_email')
        return email.lower().strip() if email else email
