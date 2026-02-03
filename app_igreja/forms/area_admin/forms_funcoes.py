"""Formulário de Funções (TBFUNCAO)."""
from django import forms

from ...models.area_admin.models_funcoes import TBFUNCAO


class FuncaoForm(forms.ModelForm):
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
        labels = {'FUN_nome_funcao': 'Nome da Função'}
        help_texts = {'FUN_nome_funcao': 'Nome identificador da função/cargo'}

    def clean_FUN_nome_funcao(self):
        nome = self.cleaned_data.get('FUN_nome_funcao')
        if not nome:
            raise forms.ValidationError('O nome da função é obrigatório.')
        if len(nome.strip()) < 3:
            raise forms.ValidationError('O nome da função deve ter pelo menos 3 caracteres.')
        queryset = TBFUNCAO.objects.filter(FUN_nome_funcao__iexact=nome.strip())
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError('Já existe uma função com este nome.')
        return nome.strip()
