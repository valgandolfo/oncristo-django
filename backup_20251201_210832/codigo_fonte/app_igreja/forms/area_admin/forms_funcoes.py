from django import forms
from app_igreja.models import TBFUNCAO


class FuncaoForm(forms.ModelForm):
    """Formulário para Funções"""
    
    class Meta:
        model = TBFUNCAO
        fields = ['FUN_nome_funcao']
        widgets = {
            'FUN_nome_funcao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome da função...',
                'maxlength': '255',
                'id': 'FUN_nome_funcao'
            }),
        }
        labels = {
            'FUN_nome_funcao': 'Nome da Função',
        }
        help_texts = {
            'FUN_nome_funcao': 'Nome identificador da função/cargo',
        }
    
    def clean_FUN_nome_funcao(self):
        """Validação do nome da função"""
        nome = self.cleaned_data.get('FUN_nome_funcao')
        if not nome:
            raise forms.ValidationError('O nome da função é obrigatório.')
        
        if len(nome.strip()) < 3:
            raise forms.ValidationError('O nome da função deve ter pelo menos 3 caracteres.')
        
        # Verificar se já existe outra função com o mesmo nome (exceto a atual)
        queryset = TBFUNCAO.objects.filter(FUN_nome_funcao__iexact=nome.strip())
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise forms.ValidationError('Já existe uma função com este nome.')
        
        return nome.strip()
    
    def save(self, commit=True):
        """Salva a função com validações adicionais"""
        funcao = super().save(commit=False)
        
        if commit:
            funcao.save()
        
        return funcao
