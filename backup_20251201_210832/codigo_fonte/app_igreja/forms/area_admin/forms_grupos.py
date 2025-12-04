from django import forms
from app_igreja.models import TBGRUPOS


class GrupoForm(forms.ModelForm):
    """Formulário para Grupos Litúrgicos"""
    
    class Meta:
        model = TBGRUPOS
        fields = ['GRU_nome_grupo', 'GRU_ativo', 'GRU_eventos_json']
        widgets = {
            'GRU_nome_grupo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome do grupo litúrgico...',
                'maxlength': '100',
                'id': 'GRU_nome_grupo'
            }),
            'GRU_ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'GRU_ativo'
            }),
            'GRU_eventos_json': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Digite os eventos em formato JSON...',
                'rows': 4,
                'id': 'GRU_eventos_json'
            }),
        }
        labels = {
            'GRU_nome_grupo': 'Nome do Grupo',
            'GRU_ativo': 'Grupo Ativo',
            'GRU_eventos_json': 'Eventos (JSON)',
        }
        help_texts = {
            'GRU_nome_grupo': 'Nome identificador do grupo litúrgico',
            'GRU_ativo': 'Marque se o grupo está ativo no sistema',
            'GRU_eventos_json': 'Eventos associados ao grupo em formato JSON',
        }
    
    def clean_GRU_nome_grupo(self):
        """Validação do nome do grupo"""
        nome = self.cleaned_data.get('GRU_nome_grupo')
        if not nome:
            raise forms.ValidationError('O nome do grupo é obrigatório.')
        
        if len(nome.strip()) < 3:
            raise forms.ValidationError('O nome do grupo deve ter pelo menos 3 caracteres.')
        
        # Verificar se já existe outro grupo com o mesmo nome (exceto o atual)
        queryset = TBGRUPOS.objects.filter(GRU_nome_grupo__iexact=nome.strip())
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise forms.ValidationError('Já existe um grupo com este nome.')
        
        return nome.strip()
    
    def clean_GRU_eventos_json(self):
        """Validação do JSON de eventos"""
        eventos_json = self.cleaned_data.get('GRU_eventos_json')
        
        if eventos_json:
            import json
            try:
                # Tentar fazer parse do JSON para validar
                json.loads(eventos_json)
            except json.JSONDecodeError:
                raise forms.ValidationError('O formato JSON dos eventos é inválido.')
        
        return eventos_json
    
    def save(self, commit=True):
        """Salva o grupo com validações adicionais"""
        grupo = super().save(commit=False)
        
        if commit:
            grupo.save()
        
        return grupo
