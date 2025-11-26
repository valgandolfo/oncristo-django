"""
==================== FORMULÁRIOS COMUNS ====================
Arquivo com widgets, validações e funcionalidades compartilhadas
entre todos os formulários da área administrativa
"""

from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from ...utils import ESTADOS_BRASIL, TIPOS_PIX


class DateInputWidget(forms.DateInput):
    """Widget personalizado para campos de data que formata corretamente para HTML5"""
    input_type = 'date'
    
    def __init__(self, attrs=None, format=None):
        super().__init__(attrs, format)
        if format is None:
            self.format = '%Y-%m-%d'
    
    def format_value(self, value):
        """Formata o valor da data para o formato YYYY-MM-DD esperado pelo HTML5"""
        if value is None:
            return ''
        if isinstance(value, date):
            return value.strftime('%Y-%m-%d')
        elif isinstance(value, str):
            try:
                from datetime import datetime
                parsed_date = datetime.strptime(value, '%Y-%m-%d').date()
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                return value
        return value


class BaseAdminForm(forms.ModelForm):
    """Formulário base com validações comuns para área administrativa"""
    
    class Meta:
        abstract = True
    
    def clean_telefone(self):
        """Validação comum para campos de telefone"""
        telefone_field = None
        for field_name, field_obj in self.fields.items():
            if 'telefone' in field_name.lower():
                telefone_field = self.cleaned_data.get(field_name)
                break
        
        if telefone_field:
            # Remove caracteres não numéricos
            telefone_limpo = ''.join(filter(str.isdigit, telefone_field))
            
            # Validação básica
            if len(telefone_limpo) < 10:
                raise ValidationError("Telefone deve ter pelo menos 10 dígitos")
            
            # Formatação automática
            if len(telefone_limpo) == 11:
                return f"({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}"
            elif len(telefone_limpo) == 10:
                return f"({telefone_limpo[:2]}) {telefone_limpo[2:6]}-{telefone_limpo[6:]}"
        
        return telefone_field
    
    def clean_cep(self):
        """Validação comum para campos de CEP"""
        cep_field = None
        for field_name, field_obj in self.fields.items():
            if 'cep' in field_name.lower():
                cep_field = self.cleaned_data.get(field_name)
                break
        
        if cep_field:
            # Remove caracteres não numéricos
            cep_limpo = ''.join(filter(str.isdigit, cep_field))
            if len(cep_limpo) != 8:
                raise ValidationError("CEP deve ter 8 dígitos")
            
            # Formatação padrão
            if len(cep_limpo) == 8:
                return f"{cep_limpo[:5]}-{cep_limpo[5:]}"
        
        return cep_field
    
    def clean_cpf(self):
        """Validação comum para campos de CPF"""
        cpf_field = None
        for field_name, field_obj in self.fields.items():
            if 'cpf' in field_name.lower():
                cpf_field = self.cleaned_data.get(field_name)
                break
        
        if cpf_field:
            # Remove caracteres não numéricos
            cpf_limpo = ''.join(filter(str.isdigit, str(cpf_field)))
            
            # Verifica se tem 11 dígitos
            if len(cpf_limpo) != 11:
                raise ValidationError("CPF deve ter 11 dígitos.")
            
            # Verifica se todos os dígitos são iguais
            if cpf_limpo == cpf_limpo[0] * 11:
                raise ValidationError("CPF inválido.")
            
            # Calcula primeiro dígito verificador
            soma = 0
            for i in range(9):
                soma += int(cpf_limpo[i]) * (10 - i)
            resto = soma % 11
            digito1 = 0 if resto < 2 else 11 - resto
            
            # Calcula segundo dígito verificador
            soma = 0
            for i in range(10):
                soma += int(cpf_limpo[i]) * (11 - i)
            resto = soma % 11
            digito2 = 0 if resto < 2 else 11 - resto
            
            # Verifica se os dígitos calculados são iguais aos do CPF
            if cpf_limpo[-2:] != f"{digito1}{digito2}":
                raise ValidationError("CPF inválido.")
            
            # Formata o CPF
            return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        
        return cpf_field
    
    def clean_foto(self):
        """Validação comum para campos de foto/arquivo"""
        foto_field = None
        for field_name, field_obj in self.fields.items():
            if any(word in field_name.lower() for word in ['foto', 'photo', 'image']):
                foto_field = self.cleaned_data.get(field_name)
                break
        
        if foto_field:
            # Verificar tamanho (máximo 5MB)
            if foto_field.size > 5 * 1024 * 1024:
                raise ValidationError("A imagem deve ter no máximo 5MB")
            
            # Verificar extensão
            extensoes_validas = ['.jpg', '.jpeg', '.png', '.gif']
            import os
            nome_arquivo = foto_field.name.lower()
            if not any(nome_arquivo.endswith(ext) for ext in extensoes_validas):
                raise ValidationError("Formato de arquivo não suportado. Use JPG, PNG ou GIF")
        
        return foto_field


def get_estados_brasil():
    """Retorna lista de estados do Brasil para uso em formulários"""
    return ESTADOS_BRASIL


def get_tipos_pix():
    """Retorna tipos de PIX para uso em formulários"""
    return TIPOS_PIX


def get_generic_text_input_attrs(placeholder="Digite aqui..."):
    """Retorna atributos padrão para campos de texto"""
    return {
        'class': 'form-control',
        'placeholder': placeholder
    }


def get_generic_email_input_attrs(placeholder="email@exemplo.com"):
    """Retorna atributos padrão para campos de email"""
    return {
        'class': 'form-control',
        'placeholder': placeholder
    }


def get_generic_phone_input_attrs(placeholder="(00) 00000-0000"):
    """Retorna atributos padrão para campos de telefone"""
    return {
        'class': 'form-control',
        'placeholder': placeholder
    }


def get_generic_select_attrs():
    """Retorna atributos padrão para campos de seleção"""
    return {
        'class': 'form-control'
    }


def get_generic_file_input_attrs(accept="image/*"):
    """Retorna atributos padrão para campos de arquivo"""
    return {
        'class': 'form-control',
        'accept': accept
    }
