"""
==================== FORM CADASTRO DIZIMISTA PÚBLICO ====================
Formulário para cadastro público de dizimistas (nomenclatura: cadastro_dizimista_pub)
"""

from django import forms
from django.core.exceptions import ValidationError
from ...models.area_admin.models_dizimistas import TBDIZIMISTAS
import re


class CadastroDizimistaPubForm(forms.ModelForm):
    """
    Formulário público para cadastro de dizimistas
    
    Características:
    - Validação completa de dados (telefone, CPF, email)
    - Widgets otimizados para UX
    - Integração com APIs externas (ViaCEP)
    - Suporte a upload de foto
    """
    
    class Meta:
        model = TBDIZIMISTAS
        fields = [
            'DIS_telefone', 'DIS_nome', 'DIS_email', 'DIS_data_nascimento', 'DIS_sexo',
            'DIS_cep', 'DIS_endereco', 'DIS_numero', 'DIS_complemento', 'DIS_bairro', 
            'DIS_cidade', 'DIS_estado', 'DIS_foto', 'DIS_cpf', 'DIS_dia_pagamento', 'DIS_valor'
        ]
        
        widgets = {
            'DIS_telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000',
                'id': 'DIS_telefone',
                'required': True,
                'data-mask': '(00) 00000-0000'
            }),
            'DIS_nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do dizimista',
                'required': True,
                'minlength': '3',
                'maxlength': '100'
            }),
            'DIS_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com',
                'pattern': r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
            }),
            'DIS_data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'max': '2010-12-31'  # Máximo 14 anos
            }),
            'DIS_sexo': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('', 'Selecione...'),
                ('M', 'Masculino'),
                ('F', 'Feminino'),
            ]),
            'DIS_cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000',
                'id': 'DIS_cep',
                'data-mask': '00000-000',
                'maxlength': '9'
            }),
            'DIS_endereco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Endereço completo',
                'id': 'DIS_endereco',
                'maxlength': '200'
            }),
            'DIS_numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número',
                'id': 'DIS_numero',
                'maxlength': '10'
            }),
            'DIS_complemento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Complemento (casa, apto, sala, etc.)',
                'id': 'DIS_complemento',
                'maxlength': '100'
            }),
            'DIS_bairro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bairro',
                'id': 'DIS_bairro',
                'maxlength': '100'
            }),
            'DIS_cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade',
                'id': 'DIS_cidade',
                'maxlength': '100'
            }),
            'DIS_estado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'UF',
                'maxlength': '2',
                'id': 'DIS_estado',
                'pattern': r'[A-Za-z]{2}',
                'title': 'Digite a sigla do estado (ex: SP, RJ)'
            }),
            'DIS_foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png,image/gif',
                'onchange': 'previewFoto(this)',
                'title': 'Formatos aceitos: JPG, PNG, GIF (máx. 5MB)'
            }),
            'DIS_cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00',
                'id': 'DIS_cpf',
                'data-mask': '000.000.000-00',
                'maxlength': '14'
            }),
            'DIS_dia_pagamento': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dia do mês (1-31)',
                'min': '1',
                'max': '31',
                'id': 'DIS_dia_pagamento',
                'title': 'Escolha o dia do mês para pagamento do dízimo'
            }),
            'DIS_valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0,00',
                'step': '0.01',
                'min': '1.00',
                'id': 'DIS_valor',
                'title': 'Valor mensal do dízimo em reais'
            }),
        }
        
        labels = {
            'DIS_telefone': '📱 Telefone *',
            'DIS_nome': '👤 Nome Completo *',
            'DIS_email': '📧 E-mail',
            'DIS_data_nascimento': '🎂 Data de Nascimento',
            'DIS_sexo': '⚧ Sexo',
            'DIS_cep': '📮 CEP',
            'DIS_endereco': '🏠 Endereço',
            'DIS_numero': '🔢 Número',
            'DIS_complemento': '🏢 Complemento',
            'DIS_bairro': '🏘️ Bairro',
            'DIS_cidade': '🏙️ Cidade',
            'DIS_estado': '🌎 Estado',
            'DIS_foto': '📷 Foto',
            'DIS_cpf': '🆔 CPF',
            'DIS_dia_pagamento': '📅 Dia do Pagamento',
            'DIS_valor': '💰 Valor do Dízimo (R$)',
        }
        
        help_texts = {
            'DIS_telefone': 'Número com DDD para contato',
            'DIS_nome': 'Nome completo como no documento',
            'DIS_email': 'E-mail para comunicações da paróquia',
            'DIS_data_nascimento': 'Data de nascimento para parabenizar você',
            'DIS_cep': 'CEP para preenchimento automático do endereço',
            'DIS_foto': 'Foto opcional para identificação (máx. 5MB)',
            'DIS_cpf': 'CPF para identificação fiscal (opcional)',
            'DIS_dia_pagamento': 'Dia do mês preferido para contribuição',
            'DIS_valor': 'Valor mensal que pretende contribuir',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Definir campos obrigatórios
        self.fields['DIS_telefone'].required = True
        self.fields['DIS_nome'].required = True
        
        # Adicionar classes CSS para campos obrigatórios
        for field_name, field in self.fields.items():
            if field.required:
                current_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{current_class} required-field".strip()
        
        # Melhorar acessibilidade
        for field_name, field in self.fields.items():
            if 'id' in field.widget.attrs:
                field.widget.attrs['aria-describedby'] = f"{field.widget.attrs['id']}_help"
    
    def clean_DIS_telefone(self):
        """Validação avançada do telefone"""
        telefone = self.cleaned_data.get('DIS_telefone')
        
        if not telefone:
            raise ValidationError("Telefone é obrigatório")
        
        # Remove caracteres não numéricos
        telefone_limpo = re.sub(r'[^\d]', '', str(telefone))
        
        # Validar tamanho
        if len(telefone_limpo) < 10:
            raise ValidationError("Telefone deve ter pelo menos 10 dígitos (DDD + número)")
        elif len(telefone_limpo) > 11:
            raise ValidationError("Telefone deve ter no máximo 11 dígitos")
        
        # Validar DDD
        if len(telefone_limpo) >= 2:
            ddd = int(telefone_limpo[:2])
            ddds_validos = [
                11, 12, 13, 14, 15, 16, 17, 18, 19,  # SP
                21, 22, 24,  # RJ/ES
                27, 28,  # ES
                31, 32, 33, 34, 35, 37, 38,  # MG
                41, 42, 43, 44, 45, 46,  # PR
                47, 48, 49,  # SC
                51, 53, 54, 55,  # RS
                61,  # DF/GO
                62, 64,  # GO/TO
                63,  # TO
                65, 66,  # MT/MS
                67,  # MS
                68,  # AC
                69,  # RO
                71, 73, 74, 75, 77,  # BA
                79,  # SE
                81, 87,  # PE
                82,  # AL
                83,  # PB
                84,  # RN
                85, 88,  # CE
                86, 89,  # PI
                91, 93, 94,  # PA
                92, 97,  # AM
                95,  # RR
                96,  # AP
                98, 99,  # MA
            ]
            
            if ddd not in ddds_validos:
                raise ValidationError("DDD inválido")
        
        # Verificar se já existe (excluindo o próprio registro se for edição)
        existing_query = TBDIZIMISTAS.objects.filter(DIS_telefone=telefone)
        if self.instance and self.instance.pk:
            existing_query = existing_query.exclude(pk=self.instance.pk)
        
        if existing_query.exists():
            raise ValidationError("Este telefone já está cadastrado")
                
        return telefone
    
    def clean_DIS_email(self):
        """Validação do email"""
        email = self.cleaned_data.get('DIS_email')
        
        if email:
            # Validação básica de formato
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                raise ValidationError("Formato de e-mail inválido")
            
            # Verificar se já existe (excluindo o próprio registro se for edição)
            existing_query = TBDIZIMISTAS.objects.filter(DIS_email=email)
            if self.instance and self.instance.pk:
                existing_query = existing_query.exclude(pk=self.instance.pk)
                
            if existing_query.exists():
                raise ValidationError("Este e-mail já está cadastrado")
        
        return email
    
    def clean_DIS_valor(self):
        """Validação do valor"""
        valor = self.cleaned_data.get('DIS_valor')
        
        if valor is not None:
            if valor <= 0:
                raise ValidationError("O valor deve ser maior que zero")
            elif valor > 99999.99:
                raise ValidationError("Valor muito alto. Entre em contato conosco para contribuições especiais")
        
        return valor
    
    def clean_DIS_cep(self):
        """Validação do CEP"""
        cep = self.cleaned_data.get('DIS_cep')
        
        if cep:
            cep_limpo = re.sub(r'[^\d]', '', str(cep))
            if len(cep_limpo) != 8:
                raise ValidationError("CEP deve ter 8 dígitos")
            
            # Verificar se não é um CEP claramente inválido
            if cep_limpo == '00000000' or cep_limpo[0] == '0' and len(set(cep_limpo)) == 1:
                raise ValidationError("CEP inválido")
        
        return cep
    
    def clean_DIS_cpf(self):
        """Validação do CPF com algoritmo oficial"""
        cpf = self.cleaned_data.get('DIS_cpf')
        
        if cpf:
            if not self._validar_cpf(cpf):
                raise ValidationError("CPF inválido")
        
        return cpf
    
    def clean_DIS_dia_pagamento(self):
        """Validação do dia de pagamento"""
        dia = self.cleaned_data.get('DIS_dia_pagamento')
        
        if dia is not None:
            if dia < 1 or dia > 31:
                raise ValidationError("Dia do pagamento deve ser entre 1 e 31")
        
        return dia
    
    def clean_DIS_nome(self):
        """Validação do nome"""
        nome = self.cleaned_data.get('DIS_nome')
        
        if nome:
            # Remover espaços extras
            nome = ' '.join(nome.split())
            
            # Verificar tamanho mínimo
            if len(nome) < 3:
                raise ValidationError("Nome deve ter pelo menos 3 caracteres")
            
            # Verificar se tem pelo menos nome e sobrenome
            partes = nome.split()
            if len(partes) < 2:
                raise ValidationError("Digite o nome completo (nome e sobrenome)")
            
            # Verificar caracteres válidos
            if not re.match(r'^[a-zA-ZÀ-ÿ\s\'-]+$', nome):
                raise ValidationError("Nome contém caracteres inválidos")
        
        return nome
    
    def clean_DIS_foto(self):
        """Validação da foto"""
        foto = self.cleaned_data.get('DIS_foto')
        
        if foto:
            # Verificar tamanho (5MB máximo)
            if foto.size > 5 * 1024 * 1024:
                raise ValidationError("Foto deve ter no máximo 5MB")
            
            # Verificar formato
            valid_formats = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if foto.content_type not in valid_formats:
                raise ValidationError("Formato inválido. Use JPG, PNG ou GIF")
        
        return foto
    
    def _validar_cpf(self, cpf):
        """
        Validação completa de CPF usando algoritmo oficial
        """
        # Remove caracteres não numéricos
        cpf = re.sub(r'[^0-9]', '', str(cpf))
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False
        
        # Verifica se todos os dígitos são iguais (ex: 111.111.111-11)
        if cpf == cpf[0] * 11:
            return False
        
        # Validação do primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        if int(cpf[9]) != digito1:
            return False
        
        # Validação do segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        return int(cpf[10]) == digito2


# Alias para compatibilidade (ex.: forms_dizimistas, whatsapp)
DizimistaPublicoForm = CadastroDizimistaPubForm