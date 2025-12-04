"""
==================== FORMULÁRIOS DE GERENCIAR ESCALA ====================
Arquivo com formulários específicos para Gerenciar Escala de Missas
"""

from django import forms
from datetime import date
from ...models.area_admin.models_escala import TBITEM_ESCALA
from ...models.area_admin.models_colaboradores import TBCOLABORADORES
from ...models.area_admin.models_grupos import TBGRUPOS


class ItemEscalaForm(forms.ModelForm):
    """Formulário para cadastro/edição de itens da escala"""
    
    # Sobrescrever campos para usar ModelChoiceField
    ITE_ESC_COLABORADOR = forms.ModelChoiceField(
        queryset=TBCOLABORADORES.objects.all().order_by('COL_nome_completo'),
        required=False,
        empty_label="Selecione um colaborador...",
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Colaborador',
    )
    
    ITE_ESC_GRUPO = forms.ModelChoiceField(
        queryset=TBGRUPOS.objects.all().order_by('GRU_nome_grupo'),
        required=False,
        empty_label="Selecione um grupo...",
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Grupo',
    )
    
    class Meta:
        model = TBITEM_ESCALA
        fields = [
            'ITE_ESC_DATA',
            'ITE_ESC_HORARIO',
            'ITE_ESC_ENCARGO',
            'ITE_ESC_STATUS',
            'ITE_ESC_SITUACAO',
        ]
        # ITE_ESC_COLABORADOR e ITE_ESC_GRUPO são definidos como ModelChoiceField acima
        # e não devem estar em fields para evitar conflito
        widgets = {
            'ITE_ESC_DATA': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'ITE_ESC_HORARIO': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'ITE_ESC_ENCARGO': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Primeira Leitura, Salmos, etc.',
            }),
            'ITE_ESC_STATUS': forms.Select(attrs={
                'class': 'form-control',
            }, choices=[
                ('EM_ABERTO', 'Em aberto'),
                ('DEFINIDO', 'Definido'),
            ]),
            'ITE_ESC_SITUACAO': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'ITE_ESC_DATA': 'Dia',
            'ITE_ESC_HORARIO': 'Hora',
            'ITE_ESC_ENCARGO': 'Encargo',
            'ITE_ESC_STATUS': 'Status',
            'ITE_ESC_SITUACAO': 'Desbloquear este item',
        }
    
    def __init__(self, *args, **kwargs):
        escala = kwargs.pop('escala', None)
        acao = kwargs.pop('acao', None)  # Receber ação para controlar readonly
        super().__init__(*args, **kwargs)
        
        if escala and not self.instance.pk:
            # Se for criação e tiver escala, definir a escala
            self.instance.ITE_ESC_ESCALA = escala
        
        # Se for incluir, tornar data readonly
        if acao == 'incluir':
            self.fields['ITE_ESC_DATA'].widget.attrs['readonly'] = True
        
        # Sempre tornar data readonly (não pode ser alterada)
        self.fields['ITE_ESC_DATA'].widget.attrs['readonly'] = True
        
        # Converter valores IntegerField para ModelChoiceField
        if self.instance.pk:
            # Se estiver editando, converter IDs para objetos
            if self.instance.ITE_ESC_COLABORADOR:
                try:
                    colaborador = TBCOLABORADORES.objects.get(COL_id=self.instance.ITE_ESC_COLABORADOR)
                    self.initial['ITE_ESC_COLABORADOR'] = colaborador
                except TBCOLABORADORES.DoesNotExist:
                    pass
            
            if self.instance.ITE_ESC_GRUPO:
                try:
                    grupo = TBGRUPOS.objects.get(GRU_id=self.instance.ITE_ESC_GRUPO)
                    self.initial['ITE_ESC_GRUPO'] = grupo
                except TBGRUPOS.DoesNotExist:
                    pass
        else:
            # Se for novo registro, garantir que os campos estão vazios
            if 'ITE_ESC_COLABORADOR' not in self.initial:
                self.initial['ITE_ESC_COLABORADOR'] = None
            if 'ITE_ESC_GRUPO' not in self.initial:
                self.initial['ITE_ESC_GRUPO'] = None
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Converter ModelChoiceField para IntegerField
        if self.cleaned_data.get('ITE_ESC_COLABORADOR'):
            colaborador = self.cleaned_data['ITE_ESC_COLABORADOR']
            instance.ITE_ESC_COLABORADOR = colaborador.COL_id
            # Gravar a função do colaborador no momento da atribuição (preserva histórico)
            instance.ITE_ESC_FUNCAO = colaborador.COL_funcao
        else:
            instance.ITE_ESC_COLABORADOR = None
            instance.ITE_ESC_FUNCAO = None
        
        if self.cleaned_data.get('ITE_ESC_GRUPO'):
            instance.ITE_ESC_GRUPO = self.cleaned_data['ITE_ESC_GRUPO'].GRU_id
        else:
            instance.ITE_ESC_GRUPO = None
        
        if commit:
            instance.save()
        return instance

