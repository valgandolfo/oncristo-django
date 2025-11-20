"""
==================== FORMULÁRIOS DE ORAÇÕES ====================
Arquivo com formulários específicos para Pedidos de Orações
"""

from django import forms
from django.core.exceptions import ValidationError
from ...models.area_admin.models_oracoes import TBORACOES
from .forms_commons import BaseAdminForm, DateInputWidget


class OracaoForm(BaseAdminForm):
    """Formulário para cadastro de pedidos de orações"""
    
    class Meta:
        model = TBORACOES
        fields = [
            'ORA_nome_solicitante', 'ORA_telefone_pedinte', 'ORA_tipo_oracao', 
            'ORA_descricao', 'ORA_status', 'ORA_ativo', 'ORA_data_pedido'
        ]
        widgets = {
            'ORA_nome_solicitante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do solicitante',
                'id': 'ORA_nome_solicitante'
            }),
            'ORA_telefone_pedinte': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000',
                'id': 'ORA_telefone_pedinte'
            }),
            'ORA_tipo_oracao': forms.Select(attrs={
                'class': 'form-control',
                'id': 'ORA_tipo_oracao'
            }),
            'ORA_descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '4',
                'placeholder': 'Descreva detalhadamente o pedido de oração...',
                'id': 'ORA_descricao'
            }),
            'ORA_status': forms.Select(attrs={
                'class': 'form-control',
                'id': 'ORA_status'
            }),
            'ORA_ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'ORA_ativo'
            }),
            'ORA_data_pedido': DateInputWidget(attrs={
                'class': 'form-control',
                'id': 'ORA_data_pedido'
            }),
        }
        labels = {
            'ORA_nome_solicitante': 'Nome do Solicitante',
            'ORA_telefone_pedinte': 'Telefone do Solicitante',
            'ORA_tipo_oracao': 'Tipo de Oração',
            'ORA_descricao': 'Descrição da Oração',
            'ORA_status': 'Status',
            'ORA_ativo': 'Ativo',
            'ORA_data_pedido': 'Data do Pedido',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adicionar opção vazia para tipo de oração
        self.fields['ORA_tipo_oracao'].choices = [('', 'Selecione o tipo...')] + list(self.fields['ORA_tipo_oracao'].choices)
        
        # Adicionar opção vazia para status
        self.fields['ORA_status'].choices = [('', 'Selecione o status...')] + list(self.fields['ORA_status'].choices)
        
        # Definir data padrão como hoje se for novo pedido
        from django.utils import timezone
        if not self.instance.pk:  # Se for um novo pedido
            self.fields['ORA_data_pedido'].initial = timezone.now().date()
    
    def clean_ORA_descricao(self):
        """Validação da descrição"""
        descricao = self.cleaned_data.get('ORA_descricao')
        if descricao and len(descricao.strip()) < 10:
            raise ValidationError("A descrição deve ter pelo menos 10 caracteres.")
        return descricao
    
    def clean_ORA_data_pedido(self):
        """Validação da data do pedido"""
        from django.utils import timezone
        
        data_pedido = self.cleaned_data.get('ORA_data_pedido')
        if data_pedido and data_pedido < timezone.now().date():
            raise ValidationError("A data do pedido não pode ser no passado.")
        return data_pedido


class OracaoFiltroForm(forms.Form):
    """Formulário para filtros na listagem de orações"""
    
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
    
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nome, telefone ou descrição...',
            'id': 'search-input'
        }),
        label='Buscar'
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'status-filter'
        }),
        label='Status'
    )
    
    tipo_oracao = forms.ChoiceField(
        choices=TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'tipo-filter'
        }),
        label='Tipo de Oração'
    )
    
    ativo = forms.ChoiceField(
        choices=ATIVO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'ativo-filter'
        }),
        label='Ativo'
    )
    
    data_inicio = forms.DateField(
        required=False,
        widget=DateInputWidget(attrs={
            'class': 'form-control',
            'id': 'data-inicio'
        }),
        label='Data Início'
    )
    
    data_fim = forms.DateField(
        required=False,
        widget=DateInputWidget(attrs={
            'class': 'form-control',
            'id': 'data-fim'
        }),
        label='Data Fim'
    )


class OracaoPublicoForm(forms.ModelForm):
    """Formulário para cadastro público de pedidos de orações (sem campos administrativos)"""
    
    class Meta:
        model = TBORACOES
        fields = [
            'ORA_nome_solicitante', 'ORA_telefone_pedinte', 'ORA_tipo_oracao', 
            'ORA_descricao', 'ORA_data_pedido'
        ]
        widgets = {
            'ORA_nome_solicitante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do solicitante',
                'id': 'ORA_nome_solicitante'
            }),
            'ORA_telefone_pedinte': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000',
                'id': 'ORA_telefone_pedinte'
            }),
            'ORA_tipo_oracao': forms.Select(attrs={
                'class': 'form-control',
                'id': 'ORA_tipo_oracao'
            }),
            'ORA_descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '4',
                'placeholder': 'Descreva detalhadamente o pedido de oração...',
                'id': 'ORA_descricao'
            }),
            'ORA_data_pedido': DateInputWidget(attrs={
                'class': 'form-control',
                'id': 'ORA_data_pedido'
            }),
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
        
        # Adicionar opção vazia para tipo de oração
        self.fields['ORA_tipo_oracao'].choices = [('', 'Selecione o tipo...')] + list(self.fields['ORA_tipo_oracao'].choices)
        
        # Definir data padrão como hoje se for novo pedido
        from django.utils import timezone
        if not self.instance.pk:  # Se for um novo pedido
            self.fields['ORA_data_pedido'].initial = timezone.now().date()
    
    def clean_ORA_descricao(self):
        """Validação da descrição"""
        descricao = self.cleaned_data.get('ORA_descricao')
        if descricao and len(descricao.strip()) < 10:
            raise ValidationError("A descrição deve ter pelo menos 10 caracteres.")
        return descricao
    
    def clean_ORA_data_pedido(self):
        """Validação da data do pedido"""
        from django.utils import timezone
        
        data_pedido = self.cleaned_data.get('ORA_data_pedido')
        if data_pedido and data_pedido < timezone.now().date():
            raise ValidationError("A data do pedido não pode ser no passado.")
        return data_pedido
