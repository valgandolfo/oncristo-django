from django import forms
from app_igreja.models.area_admin.models_eventos import TBEVENTO
from .forms_commons import DateInputWidget


class EventoForm(forms.ModelForm):
    class Meta:
        model = TBEVENTO
        fields = [
            'EVE_TITULO', 'EVE_TIPO', 'EVE_DESCRICAO',
            'EVE_DT_INICIAL', 'EVE_DT_FINAL',
            'EVE_HORA_INICIAL', 'EVE_HORA_FINAL',
            'EVE_LOCAL', 'EVE_ENDERECO', 'EVE_RESPONSAVEL',
            'EVE_CELEBRANTE', 'EVE_PARTICIPANTES', 'EVE_CONFIRMADOS',
            'EVE_RECURSOS', 'EVE_STATUS'
        ]
        widgets = {
            'EVE_TITULO': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o título do evento',
                'maxlength': '100'
            }),
            'EVE_TIPO': forms.Select(attrs={
                'class': 'form-select'
            }),
            'EVE_DESCRICAO': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'maxlength': '255',
                'placeholder': 'Descrição do evento'
            }),
            'EVE_DT_INICIAL': DateInputWidget(attrs={
                'class': 'form-control',
                'required': True
            }),
            'EVE_DT_FINAL': DateInputWidget(attrs={
                'class': 'form-control'
            }),
            'EVE_HORA_INICIAL': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'EVE_HORA_FINAL': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'EVE_LOCAL': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '100',
                'placeholder': 'Local do evento'
            }),
            'EVE_ENDERECO': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '100',
                'placeholder': 'Endereço do evento'
            }),
            'EVE_RESPONSAVEL': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '100',
                'placeholder': 'Responsável pelo evento'
            }),
            'EVE_CELEBRANTE': forms.Select(attrs={
                'class': 'form-select'
            }),
            'EVE_PARTICIPANTES': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1'
            }),
            'EVE_CONFIRMADOS': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1'
            }),
            'EVE_RECURSOS': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '255',
                'placeholder': 'Recursos necessários'
            }),
            'EVE_STATUS': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'EVE_TITULO': 'Título do Evento',
            'EVE_TIPO': 'Tipo do Evento',
            'EVE_DESCRICAO': 'Descrição',
            'EVE_DT_INICIAL': 'Data Inicial',
            'EVE_DT_FINAL': 'Data Final',
            'EVE_HORA_INICIAL': 'Hora Inicial',
            'EVE_HORA_FINAL': 'Hora Final',
            'EVE_LOCAL': 'Local',
            'EVE_ENDERECO': 'Endereço',
            'EVE_RESPONSAVEL': 'Responsável',
            'EVE_CELEBRANTE': 'Celebrante',
            'EVE_PARTICIPANTES': 'Participantes',
            'EVE_CONFIRMADOS': 'Confirmados',
            'EVE_RECURSOS': 'Recursos',
            'EVE_STATUS': 'Status'
        }
        help_texts = {
            'EVE_TITULO': 'Digite um título descritivo para o evento',
            'EVE_TIPO': 'Selecione o tipo do evento',
            'EVE_DESCRICAO': 'Descrição detalhada do evento',
            'EVE_DT_INICIAL': 'Data inicial do evento',
            'EVE_DT_FINAL': 'Data final do evento (opcional)',
            'EVE_HORA_INICIAL': 'Horário inicial do evento',
            'EVE_HORA_FINAL': 'Horário final do evento',
            'EVE_LOCAL': 'Local onde será realizado o evento',
            'EVE_ENDERECO': 'Endereço completo do evento',
            'EVE_RESPONSAVEL': 'Pessoa responsável pelo evento',
            'EVE_CELEBRANTE': 'Celebrante que irá conduzir o evento',
            'EVE_PARTICIPANTES': 'Número de participantes esperados',
            'EVE_CONFIRMADOS': 'Número de participantes confirmados',
            'EVE_RECURSOS': 'Recursos necessários para o evento',
            'EVE_STATUS': 'Status atual do evento'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app_igreja.models.area_admin.models_celebrantes import TBCELEBRANTES
        
        # Filtrar apenas celebrantes ativos
        self.fields['EVE_CELEBRANTE'].queryset = TBCELEBRANTES.objects.filter(CEL_ativo=True)
        self.fields['EVE_CELEBRANTE'].empty_label = 'Selecione um celebrante...'
        
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
    
    def clean(self):
        cleaned_data = super().clean()
        dt_inicial = cleaned_data.get('EVE_DT_INICIAL')
        dt_final = cleaned_data.get('EVE_DT_FINAL')
        hora_inicial = cleaned_data.get('EVE_HORA_INICIAL')
        hora_final = cleaned_data.get('EVE_HORA_FINAL')
        participantes = cleaned_data.get('EVE_PARTICIPANTES', 0)
        confirmados = cleaned_data.get('EVE_CONFIRMADOS', 0)
        
        # Validar que data final não seja anterior à data inicial
        if dt_final and dt_inicial:
            if dt_final < dt_inicial:
                raise forms.ValidationError({
                    'EVE_DT_FINAL': 'A data final não pode ser anterior à data inicial.'
                })
        
        # Validar que hora final não seja anterior à hora inicial (se mesma data)
        if hora_final and hora_inicial and dt_final == dt_inicial:
            if hora_final < hora_inicial:
                raise forms.ValidationError({
                    'EVE_HORA_FINAL': 'A hora final não pode ser anterior à hora inicial quando a data é a mesma.'
                })
        
        # Validar que confirmados não seja maior que participantes
        if confirmados > participantes:
            raise forms.ValidationError({
                'EVE_CONFIRMADOS': 'O número de confirmados não pode ser maior que o número de participantes.'
            })
        
        return cleaned_data
    
    def clean_EVE_TITULO(self):
        titulo = self.cleaned_data.get('EVE_TITULO')
        
        if titulo:
            # Remover espaços extras
            titulo = titulo.strip()
            
            # Verificar se não está vazio após remoção de espaços
            if not titulo:
                raise forms.ValidationError('O título do evento não pode estar vazio.')
            
            # Verificar se já existe um evento com o mesmo título
            if self.instance.pk:
                # Edição - verificar se existe outro evento com o mesmo título
                if TBEVENTO.objects.filter(
                    EVE_TITULO=titulo
                ).exclude(EVE_ID=self.instance.EVE_ID).exists():
                    raise forms.ValidationError('Já existe um evento com este título.')
            else:
                # Criação - verificar se existe um evento com o mesmo título
                if TBEVENTO.objects.filter(EVE_TITULO=titulo).exists():
                    raise forms.ValidationError('Já existe um evento com este título.')
        
        return titulo


class ItemEventoForm(forms.ModelForm):
    class Meta:
        from app_igreja.models.area_admin.models_eventos import TBITEM_EVENTO, TBEVENTO
        model = TBITEM_EVENTO
        fields = [
            'ITEM_EVE_EVENTO', 
            'ITEM_EVE_DATA_INICIAL', 
            'ITEM_EVE_ACAO',
            'ITEM_EVE_DATA_FINAL',
            'ITEM_EVE_HORA_INICIAL', 
            'ITEM_EVE_HORA_FINAL'
        ]
        widgets = {
            'ITEM_EVE_EVENTO': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'ITEM_EVE_DATA_INICIAL': DateInputWidget(attrs={
                'class': 'form-control',
                'required': True
            }),
            'ITEM_EVE_ACAO': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '100',
                'placeholder': 'Descrição da ação',
                'required': True
            }),
            'ITEM_EVE_DATA_FINAL': DateInputWidget(attrs={
                'class': 'form-control'
            }),
            'ITEM_EVE_HORA_INICIAL': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'required': True
            }),
            'ITEM_EVE_HORA_FINAL': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            })
        }
        labels = {
            'ITEM_EVE_EVENTO': 'Evento',
            'ITEM_EVE_DATA_INICIAL': 'Data Inicial',
            'ITEM_EVE_ACAO': 'Ação',
            'ITEM_EVE_DATA_FINAL': 'Data Final',
            'ITEM_EVE_HORA_INICIAL': 'Hora Inicial',
            'ITEM_EVE_HORA_FINAL': 'Hora Final'
        }
        help_texts = {
            'ITEM_EVE_EVENTO': 'Selecione o evento',
            'ITEM_EVE_DATA_INICIAL': 'Data inicial do item do evento',
            'ITEM_EVE_ACAO': 'Descrição da ação do item',
            'ITEM_EVE_DATA_FINAL': 'Data final do item do evento (opcional)',
            'ITEM_EVE_HORA_INICIAL': 'Horário inicial do item do evento',
            'ITEM_EVE_HORA_FINAL': 'Horário final do item do evento (opcional)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app_igreja.models.area_admin.models_eventos import TBEVENTO
        
        # Filtrar apenas eventos com status Ativo
        self.fields['ITEM_EVE_EVENTO'].queryset = TBEVENTO.objects.filter(EVE_STATUS='Ativo')
        
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
    
    def clean(self):
        cleaned_data = super().clean()
        data_inicial = cleaned_data.get('ITEM_EVE_DATA_INICIAL')
        data_final = cleaned_data.get('ITEM_EVE_DATA_FINAL')
        hora_inicial = cleaned_data.get('ITEM_EVE_HORA_INICIAL')
        hora_final = cleaned_data.get('ITEM_EVE_HORA_FINAL')
        
        # Validar que data final não seja anterior à data inicial
        if data_final and data_inicial:
            if data_final < data_inicial:
                raise forms.ValidationError({
                    'ITEM_EVE_DATA_FINAL': 'A data final não pode ser anterior à data inicial.'
                })
        
        # Validar que hora final não seja anterior à hora inicial (se mesma data)
        if hora_final and hora_inicial and data_final == data_inicial:
            if hora_final < hora_inicial:
                raise forms.ValidationError({
                    'ITEM_EVE_HORA_FINAL': 'A hora final não pode ser anterior à hora inicial quando a data é a mesma.'
                })
        
        return cleaned_data
