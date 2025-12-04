"""
==================== FORMULÁRIOS DE PARÓQUIAS ====================
Arquivo com formulários específicos para Paróquias
"""

from django import forms
from django.core.exceptions import ValidationError
from ...models.area_admin.models_paroquias import TBPAROQUIA
from .forms_commons import BaseAdminForm, get_estados_brasil, get_tipos_pix


class ParoquiaForm(BaseAdminForm):
    """Formulário para Paróquia baseado no model TBPAROQUIA"""

    class Meta:
        model = TBPAROQUIA
        fields = [
            'PAR_nome_paroquia', 'PAR_diocese', 'PAR_cep', 'PAR_endereco', 'PAR_numero', 'PAR_cidade', 'PAR_uf', 'PAR_bairro',
            'PAR_telefone', 'PAR_email', 'PAR_paroco', 'PAR_foto_paroco', 'PAR_secretario',
            'PAR_cnpj', 'PAR_banco', 'PAR_agencia', 'PAR_conta',
            'PAR_pix_chave', 'PAR_pix_tipo', 'PAR_pix_beneficiario', 'PAR_pix_cidade', 'PAR_pix_uf'
        ]
        widgets = {
            'PAR_nome_paroquia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome da paróquia'
            }),
            'PAR_diocese': forms.Select(attrs={
                'class': 'form-control'
            }),
            'PAR_cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000',
                'id': 'PAR_cep'
            }),
            'PAR_endereco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o endereço',
                'id': 'PAR_endereco'
            }),
            'PAR_numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número',
                'id': 'PAR_numero'
            }),
            'PAR_cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite a cidade',
                'id': 'PAR_cidade'
            }),
            'PAR_uf': forms.Select(attrs={
                'class': 'form-control',
                'id': 'PAR_uf'
            }, choices=[('', 'Selecione UF')] + list(get_estados_brasil())),
            'PAR_bairro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o bairro',
                'id': 'PAR_bairro'
            }),
            'PAR_telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000'
            }),
            'PAR_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'PAR_paroco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do pároco'
            }),
            'PAR_foto_paroco': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'PAR_secretario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do secretário(a)'
            }),
            'PAR_cnpj': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00.000.000/0000-00'
            }),
            'PAR_banco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do banco'
            }),
            'PAR_agencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0000'
            }),
            'PAR_conta': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-0'
            }),
            'PAR_pix_chave': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Chave PIX'
            }),
            'PAR_pix_tipo': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[('', 'Selecione tipo')] + list(get_tipos_pix())),
            'PAR_pix_beneficiario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do beneficiário'
            }),
            'PAR_pix_cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade do beneficiário'
            }),
            'PAR_pix_uf': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[('', 'Selecione UF')] + list(get_estados_brasil())),
        }


class ParoquiaHorariosForm(forms.ModelForm):
    """Formulário para gerenciar horários fixos da paróquia"""
    
    # Campos para cada dia da semana
    domingo_horarios = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 07:00, 09:00, 18:00'
        }),
        required=False,
        label="Domingo",
        help_text="Horários separados por vírgula (HH:MM)"
    )
    
    segunda_horarios = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 07:00, 19:00'
        }),
        required=False,
        label="Segunda-feira",
        help_text="Horários separados por vírgula (HH:MM)"
    )
    
    terca_horarios = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 07:00, 19:00'
        }),
        required=False,
        label="Terça-feira",
        help_text="Horários separados por vírgula (HH:MM)"
    )
    
    quarta_horarios = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 07:00, 19:00'
        }),
        required=False,
        label="Quarta-feira",
        help_text="Horários separados por vírgula (HH:MM)"
    )
    
    quinta_horarios = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 07:00, 19:00'
        }),
        required=False,
        label="Quinta-feira",
        help_text="Horários separados por vírgula (HH:MM)"
    )
    
    sexta_horarios = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 07:00, 19:00'
        }),
        required=False,
        label="Sexta-feira",
        help_text="Horários separados por vírgula (HH:MM)"
    )
    
    sabado_horarios = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 07:00, 19:00'
        }),
        required=False,
        label="Sábado",
        help_text="Horários separados por vírgula (HH:MM)"
    )

    class Meta:
        model = TBPAROQUIA
        fields = []  # Não precisamos de campos do model, apenas dos campos customizados

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Carregar horários existentes se estivermos editando
        if self.instance and self.instance.pk:
            horarios_fixos = self.instance.get_horarios_fixos()
            
            self.fields['domingo_horarios'].initial = ', '.join(horarios_fixos.get('domingo', []))
            self.fields['segunda_horarios'].initial = ', '.join(horarios_fixos.get('segunda', []))
            self.fields['terca_horarios'].initial = ', '.join(horarios_fixos.get('terca', []))
            self.fields['quarta_horarios'].initial = ', '.join(horarios_fixos.get('quarta', []))
            self.fields['quinta_horarios'].initial = ', '.join(horarios_fixos.get('quinta', []))
            self.fields['sexta_horarios'].initial = ', '.join(horarios_fixos.get('sexta', []))
            self.fields['sabado_horarios'].initial = ', '.join(horarios_fixos.get('sabado', []))

    def clean(self):
        cleaned_data = super().clean()
        
        # Validar formato dos horários
        dias_semana = ['domingo', 'segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado']
        
        for dia in dias_semana:
            campo = f'{dia}_horarios'
            valor = cleaned_data.get(campo, '')
            
            if valor:
                horarios = [h.strip() for h in valor.split(',') if h.strip()]
                for horario in horarios:
                    try:
                        # Validar formato HH:MM
                        from datetime import datetime
                        datetime.strptime(horario, '%H:%M')
                    except ValueError:
                        raise forms.ValidationError(f'Horário inválido no {dia}: {horario}. Use o formato HH:MM (ex: 07:00)')
        
        return cleaned_data

    def save(self, commit=True):
        # Converter horários para formato JSON
        horarios_fixos = {
            'domingo': [h.strip() for h in self.cleaned_data.get('domingo_horarios', '').split(',') if h.strip()],
            'segunda': [h.strip() for h in self.cleaned_data.get('segunda_horarios', '').split(',') if h.strip()],
            'terca': [h.strip() for h in self.cleaned_data.get('terca_horarios', '').split(',') if h.strip()],
            'quarta': [h.strip() for h in self.cleaned_data.get('quarta_horarios', '').split(',') if h.strip()],
            'quinta': [h.strip() for h in self.cleaned_data.get('quinta_horarios', '').split(',') if h.strip()],
            'sexta': [h.strip() for h in self.cleaned_data.get('sexta_horarios', '').split(',') if h.strip()],
            'sabado': [h.strip() for h in self.cleaned_data.get('sabado_horarios', '').split(',') if h.strip()],
        }
        
        # Salvar no campo JSON
        self.instance.set_horarios_fixos(horarios_fixos)
        
        if commit:
            self.instance.save()
        
        return self.instance
