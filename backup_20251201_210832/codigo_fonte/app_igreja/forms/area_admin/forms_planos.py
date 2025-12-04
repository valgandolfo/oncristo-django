"""
==================== FORMULÁRIOS DE PLANOS ====================
Arquivo com formulários para Planos de Ação e Itens do Plano
"""

from django import forms
from app_igreja.models.area_admin.models_planos import TBPLANO, TBITEMPLANO


class PlanoForm(forms.ModelForm):
    class Meta:
        model = TBPLANO
        fields = ['PLA_titulo_plano', 'PLA_ativo']
        widgets = {
            'PLA_titulo_plano': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o título do plano de ação',
                'maxlength': '50'
            }),
            'PLA_ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'PLA_titulo_plano': 'Título do Plano',
            'PLA_ativo': 'Plano Ativo'
        }
        help_texts = {
            'PLA_titulo_plano': 'Digite um título descritivo para o plano de ação',
            'PLA_ativo': 'Marque se o plano está ativo'
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
    
    def clean_PLA_titulo_plano(self):
        titulo = self.cleaned_data.get('PLA_titulo_plano')
        
        if titulo:
            # Remover espaços extras
            titulo = titulo.strip()
            
            # Verificar se não está vazio após remoção de espaços
            if not titulo:
                raise forms.ValidationError('O título do plano não pode estar vazio.')
            
            # Verificar se já existe um plano com o mesmo título
            if self.instance.pk:
                # Edição - verificar se existe outro plano com o mesmo título
                if TBPLANO.objects.filter(
                    PLA_titulo_plano=titulo
                ).exclude(PLA_id=self.instance.PLA_id).exists():
                    raise forms.ValidationError('Já existe um plano com este título.')
            else:
                # Criação - verificar se existe um plano com o mesmo título
                if TBPLANO.objects.filter(PLA_titulo_plano=titulo).exists():
                    raise forms.ValidationError('Já existe um plano com este título.')
        
        return titulo


class ItemPlanoForm(forms.ModelForm):
    """Formulário para Itens do Plano de Ação"""
    
    class Meta:
        model = TBITEMPLANO
        fields = ['ITEM_PLANO_PLANO', 'ITEM_HORA_PLANO', 'ITEM_ACAO_PLANO']
        widgets = {
            'ITEM_PLANO_PLANO': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'ITEM_HORA_PLANO': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'required': True
            }),
            'ITEM_ACAO_PLANO': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite a ação do plano',
                'maxlength': '100',
                'required': True
            })
        }
        labels = {
            'ITEM_PLANO_PLANO': 'Plano',
            'ITEM_HORA_PLANO': 'Hora',
            'ITEM_ACAO_PLANO': 'Ação'
        }
        help_texts = {
            'ITEM_PLANO_PLANO': 'Selecione o plano de ação',
            'ITEM_HORA_PLANO': 'Horário para execução da ação',
            'ITEM_ACAO_PLANO': 'Descrição da ação a ser executada'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar apenas planos ativos
        self.fields['ITEM_PLANO_PLANO'].queryset = TBPLANO.objects.filter(PLA_ativo=True)
        
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
    
    def clean_ITEM_ACAO_PLANO(self):
        """Validação da ação do plano"""
        acao = self.cleaned_data.get('ITEM_ACAO_PLANO')
        
        if acao:
            # Remover espaços extras
            acao = acao.strip()
            
            # Verificar se não está vazio após remoção de espaços
            if not acao:
                raise forms.ValidationError('A ação do plano não pode estar vazia.')
        
        return acao
