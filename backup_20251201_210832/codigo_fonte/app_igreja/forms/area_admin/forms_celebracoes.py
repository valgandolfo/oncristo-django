from django import forms
from django.core.exceptions import ValidationError
from datetime import date, time
from app_igreja.models.area_admin.models_celebracoes import TBCELEBRACOES


class DateInputWidget(forms.DateInput):
    """Widget customizado para garantir formato correto no input date"""
    input_type = 'date'
    
    def format_value(self, value):
        """Formata o valor para YYYY-MM-DD"""
        if value is None:
            return ''
        if isinstance(value, str):
            return value
        # Se for um objeto date, converter para string no formato YYYY-MM-DD
        return value.strftime('%Y-%m-%d') if hasattr(value, 'strftime') else str(value)

class CelebracaoForm(forms.ModelForm):
    """
    Formulário para Celebrações Agendadas via WhatsApp
    """
    
    class Meta:
        model = TBCELEBRACOES
        fields = [
            'CEL_tipo_celebracao',
            'CEL_data_celebracao',
            'CEL_horario',
            'CEL_local',
            'CEL_nome_solicitante',
            'CEL_telefone',
            'CEL_email',
            'CEL_participantes',
            'CEL_observacoes',
            'CEL_status',
        ]
        widgets = {
            'CEL_tipo_celebracao': forms.Select(attrs={
                'class': 'form-control'
            }),
            'CEL_data_celebracao': DateInputWidget(attrs={
                'class': 'form-control',
                'min': str(date.today())
            }),
            'CEL_horario': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'CEL_local': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Igreja Matriz, Capela São José...'
            }),
            'CEL_nome_solicitante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do solicitante'
            }),
            'CEL_telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 99999-9999'
            }),
            'CEL_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'CEL_participantes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '1000'
            }),
            'CEL_observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais sobre a celebração...'
            }),
            'CEL_status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar labels
        self.fields['CEL_tipo_celebracao'].label = 'Tipo de Celebração'
        self.fields['CEL_data_celebracao'].label = 'Data da Celebração'
        self.fields['CEL_horario'].label = 'Horário'
        self.fields['CEL_local'].label = 'Local'
        self.fields['CEL_nome_solicitante'].label = 'Nome do Solicitante'
        self.fields['CEL_telefone'].label = 'Telefone'
        self.fields['CEL_email'].label = 'E-mail'
        self.fields['CEL_participantes'].label = 'Número de Participantes'
        self.fields['CEL_observacoes'].label = 'Observações'
        self.fields['CEL_status'].label = 'Status'
        
        # Garantir que a data esteja no formato correto para o input date (YYYY-MM-DD)
        if self.instance and self.instance.pk and self.instance.CEL_data_celebracao:
            # Se estiver editando, garantir que o valor inicial esteja no formato correto
            # O widget DateInputWidget já faz isso automaticamente, mas garantimos aqui também
            data_value = self.instance.CEL_data_celebracao
            if hasattr(data_value, 'strftime'):
                self.fields['CEL_data_celebracao'].initial = data_value.strftime('%Y-%m-%d')
            else:
                self.fields['CEL_data_celebracao'].initial = data_value

    def clean_CEL_data_celebracao(self):
        """Validação da data da celebração"""
        data_celebracao = self.cleaned_data.get('CEL_data_celebracao')
        
        if data_celebracao and data_celebracao < date.today():
            raise ValidationError('A data da celebração não pode ser anterior à data atual.')
        
        return data_celebracao

    def clean_CEL_telefone(self):
        """Validação do telefone"""
        telefone = self.cleaned_data.get('CEL_telefone')
        
        if telefone:
            # Remove caracteres não numéricos
            telefone_limpo = ''.join(filter(str.isdigit, telefone))
            
            # Validação básica de telefone brasileiro
            if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
                raise ValidationError('Telefone deve ter entre 10 e 11 dígitos.')
        
        return telefone

    def clean_CEL_participantes(self):
        """Validação do número de participantes"""
        participantes = self.cleaned_data.get('CEL_participantes')
        
        if participantes and participantes < 1:
            raise ValidationError('O número de participantes deve ser pelo menos 1.')
        
        if participantes and participantes > 1000:
            raise ValidationError('O número de participantes não pode exceder 1000.')
        
        return participantes

    def clean_CEL_email(self):
        """Validação e normalização do email (case insensitive)"""
        email = self.cleaned_data.get('CEL_email')
        
        if email:
            # Converter para lowercase para garantir case insensitive
            email = email.lower().strip()
        
        return email
