from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from ...models.area_admin.models_oracoes import TBORACOES
from .forms_commons import BaseAdminForm, DateInputWidget

_attrs = lambda **kw: dict({'class': 'form-control'}, **kw)


class OracaoForm(BaseAdminForm):
    """Formulário admin para pedidos de orações."""

    class Meta:
        model = TBORACOES
        fields = [
            'ORA_nome_solicitante', 'ORA_telefone_pedinte', 'ORA_tipo_oracao',
            'ORA_descricao', 'ORA_status', 'ORA_data_pedido'
        ]
        widgets = {
            'ORA_nome_solicitante': forms.TextInput(attrs=_attrs(placeholder='Nome completo do solicitante', id='ORA_nome_solicitante')),
            'ORA_telefone_pedinte': forms.TextInput(attrs=_attrs(placeholder='(00) 00000-0000', id='ORA_telefone_pedinte', maxlength='15')),
            'ORA_tipo_oracao': forms.Select(attrs=_attrs(id='ORA_tipo_oracao')),
            'ORA_descricao': forms.Textarea(attrs=_attrs(rows='4', placeholder='Descreva o pedido de oração...', id='ORA_descricao')),
            'ORA_status': forms.Select(attrs=_attrs(id='ORA_status')),
            'ORA_data_pedido': DateInputWidget(attrs=_attrs(id='ORA_data_pedido')),
        }
        labels = {
            'ORA_nome_solicitante': 'Nome do Solicitante',
            'ORA_telefone_pedinte': 'Telefone do Solicitante',
            'ORA_tipo_oracao': 'Tipo de Oração',
            'ORA_descricao': 'Descrição da Oração',
            'ORA_status': 'Status',
            'ORA_data_pedido': 'Data do Pedido',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ORA_tipo_oracao'].choices = [('', 'Selecione o tipo...')] + list(self.fields['ORA_tipo_oracao'].choices)
        self.fields['ORA_status'].choices = [('', 'Selecione o status...')] + list(self.fields['ORA_status'].choices)
        if not self.instance.pk:
            self.fields['ORA_data_pedido'].initial = timezone.now().date()

    def clean_ORA_descricao(self):
        descricao = self.cleaned_data.get('ORA_descricao')
        if descricao and len(descricao.strip()) < 10:
            raise ValidationError("A descrição deve ter pelo menos 10 caracteres.")
        return descricao

    def clean_ORA_data_pedido(self):
        data_pedido = self.cleaned_data.get('ORA_data_pedido')
        if data_pedido and data_pedido < timezone.now().date():
            raise ValidationError("A data do pedido não pode ser no passado.")
        return data_pedido

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.ORA_ativo = True
        if commit:
            instance.save()
        return instance


class OracaoFiltroForm(forms.Form):
    """Filtros da listagem de orações (admin)."""

    STATUS_CHOICES = [
        ('', 'Todos os Status'),
        ('PENDENTE', 'Pendente'),
        ('EM_ORACAO', 'Em Oração'),
        ('ATENDIDO', 'Atendido'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    TIPO_CHOICES = [
        ('', 'Todos os Tipos'),
        ('SAUDE', 'Saúde'),
        ('FAMILIA', 'Família'),
        ('TRABALHO', 'Trabalho'),
        ('ESTUDOS', 'Estudos'),
        ('RELACIONAMENTO', 'Relacionamento'),
        ('FINANCAS', 'Finanças'),
        ('CONVERSAO', 'Conversão'),
        ('GRATIDAO', 'Gratidão'),
        ('OUTRO', 'Outro'),
    ]
    
    ATIVO_CHOICES = [
        ('', 'Todos'),
        ('true', 'Ativos'),
        ('false', 'Inativos'),
    ]
    
    q = forms.CharField(required=False, widget=forms.TextInput(attrs=_attrs(placeholder='Buscar por nome, telefone ou descrição...', id='search-input')), label='Buscar')
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, widget=forms.Select(attrs=_attrs(id='status-filter')), label='Status')
    tipo_oracao = forms.ChoiceField(choices=TIPO_CHOICES, required=False, widget=forms.Select(attrs=_attrs(id='tipo-filter')), label='Tipo de Oração')
    ativo = forms.ChoiceField(choices=ATIVO_CHOICES, required=False, widget=forms.Select(attrs=_attrs(id='ativo-filter')), label='Ativo')
    
    data_inicio = forms.DateField(required=False, widget=DateInputWidget(attrs=_attrs(id='data-inicio')), label='Data Início')
    data_fim = forms.DateField(required=False, widget=DateInputWidget(attrs=_attrs(id='data-fim')), label='Data Fim')


class OracaoPublicoForm(forms.ModelForm):
    """Formulário público para pedidos de orações (sem campos administrativos)."""

    class Meta:
        model = TBORACOES
        fields = ['ORA_nome_solicitante', 'ORA_telefone_pedinte', 'ORA_tipo_oracao', 'ORA_descricao', 'ORA_data_pedido']
        widgets = {
            'ORA_nome_solicitante': forms.TextInput(attrs=_attrs(placeholder='Nome completo do solicitante', id='ORA_nome_solicitante')),
            'ORA_telefone_pedinte': forms.TextInput(attrs=_attrs(placeholder='(00) 00000-0000', id='ORA_telefone_pedinte', maxlength='15')),
            'ORA_tipo_oracao': forms.Select(attrs=_attrs(id='ORA_tipo_oracao')),
            'ORA_descricao': forms.Textarea(attrs=_attrs(rows='4', placeholder='Descreva o pedido de oração...', id='ORA_descricao')),
            'ORA_data_pedido': DateInputWidget(attrs=_attrs(id='ORA_data_pedido')),
        }
        labels = {
            'ORA_nome_solicitante': 'Nome do Solicitante',
            'ORA_telefone_pedinte': 'Telefone do Solicitante',
            'ORA_tipo_oracao': 'Tipo de Oração',
            'ORA_descricao': 'Descrição da Oração',
            'ORA_data_pedido': 'Data do Pedido',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ORA_tipo_oracao'].choices = [('', 'Selecione o tipo...')] + list(self.fields['ORA_tipo_oracao'].choices)
        if not self.instance.pk:
            self.fields['ORA_data_pedido'].initial = timezone.now().date()

    def clean_ORA_descricao(self):
        descricao = self.cleaned_data.get('ORA_descricao')
        if descricao and len(descricao.strip()) < 10:
            raise ValidationError("A descrição deve ter pelo menos 10 caracteres.")
        return descricao

    def clean_ORA_data_pedido(self):
        data_pedido = self.cleaned_data.get('ORA_data_pedido')
        if data_pedido and data_pedido < timezone.now().date():
            raise ValidationError("A data do pedido não pode ser no passado.")
        return data_pedido
