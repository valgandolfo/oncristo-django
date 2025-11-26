from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from app_igreja.models.area_admin.models_celebracoes import TBCELEBRACOES


class CelebracaoPublicoForm(forms.ModelForm):
    """
    Formulário público simplificado para agendamento de celebrações
    Não inclui campo de status (sempre será 'pendente')
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
        ]
        widgets = {
            'CEL_tipo_celebracao': forms.Select(attrs={
                'class': 'form-control'
            }),
            'CEL_data_celebracao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
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
                'placeholder': '(11) 99999-9999',
                'readonly': False
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
        }

    def __init__(self, *args, **kwargs):
        telefone_readonly = kwargs.pop('telefone_readonly', False)
        telefone_initial = kwargs.pop('telefone_initial', None)
        super().__init__(*args, **kwargs)
        
        # Personalizar labels
        self.fields['CEL_tipo_celebracao'].label = 'Tipo de Celebração'
        self.fields['CEL_data_celebracao'].label = 'Data da Celebração'
        self.fields['CEL_horario'].label = 'Horário'
        self.fields['CEL_local'].label = 'Local'
        self.fields['CEL_nome_solicitante'].label = 'Nome do Solicitante'
        self.fields['CEL_telefone'].label = 'Telefone'
        self.fields['CEL_email'].label = 'E-mail (opcional)'
        self.fields['CEL_participantes'].label = 'Número de Participantes'
        self.fields['CEL_observacoes'].label = 'Observações (opcional)'
        
        # Configurar telefone se vier da URL
        if telefone_readonly and telefone_initial:
            self.fields['CEL_telefone'].widget.attrs['readonly'] = True
            self.fields['CEL_telefone'].widget.attrs['style'] = 'background-color: #e9ecef;'
            self.fields['CEL_telefone'].initial = telefone_initial

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
            
            # Remover código do país (55) se existir
            if telefone_limpo.startswith('55'):
                telefone_limpo = telefone_limpo[2:]
            
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

    def save(self, commit=True):
        """Override save para sempre definir status como pendente"""
        instance = super().save(commit=False)
        instance.CEL_status = 'pendente'
        
        # Limpar telefone antes de salvar (remover 55 se existir)
        if instance.CEL_telefone:
            telefone_limpo = ''.join(filter(str.isdigit, instance.CEL_telefone))
            if telefone_limpo.startswith('55'):
                telefone_limpo = telefone_limpo[2:]
            instance.CEL_telefone = telefone_limpo
        
        if commit:
            instance.save()
        return instance

