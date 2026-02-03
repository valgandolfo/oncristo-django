"""
==================== FORM CADASTRO DE COLABORADOR ====================
Formulário para cadastro público de colaboradores (rota: cadastro-colaborador/)
Nova nomenclatura baseada na funcionalidade/rota para melhor organização
"""

from django import forms
from django.core.exceptions import ValidationError
from ...models.area_admin.models_colaboradores import TBCOLABORADORES
import re


class CadastroColaboradorForm(forms.ModelForm):
    """
    Formulário público para cadastro de colaboradores
    
    Características:
    - Validação completa de dados (telefone, CPF se informado)
    - Widgets otimizados para UX
    - Integração com APIs externas (ViaCEP)
    - Suporte a upload de foto
    - Sistema de funções/ministérios
    """
    
    # Campo adicional para confirmar disponibilidade
    disponibilidade = forms.MultipleChoiceField(
        choices=[
            ('segunda', 'Segunda-feira'),
            ('terca', 'Terça-feira'),  
            ('quarta', 'Quarta-feira'),
            ('quinta', 'Quinta-feira'),
            ('sexta', 'Sexta-feira'),
            ('sabado', 'Sábado'),
            ('domingo', 'Domingo'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='📅 Disponibilidade de Horários',
        help_text='Marque os dias da semana em que você tem disponibilidade para colaborar'
    )
    
    class Meta:
        model = TBCOLABORADORES
        fields = [
            'COL_telefone', 'COL_nome_completo', 'COL_apelido', 'COL_data_nascimento', 'COL_sexo',
            'COL_estado_civil', 'COL_cep', 'COL_endereco', 'COL_numero', 'COL_complemento', 
            'COL_bairro', 'COL_cidade', 'COL_estado', 'COL_foto', 'COL_funcao_pretendida'
        ]
        
        widgets = {
            'COL_telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000',
                'id': 'COL_telefone',
                'required': True,
                'data-mask': '(00) 00000-0000'
            }),
            'COL_nome_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do colaborador',
                'required': True,
                'minlength': '3',
                'maxlength': '100'
            }),
            'COL_apelido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Como gosta de ser chamado (opcional)',
                'maxlength': '50'
            }),
            'COL_data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'max': '2010-12-31'  # Máximo 14 anos
            }),
            'COL_sexo': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('', 'Selecione...'),
                ('M', 'Masculino'),
                ('F', 'Feminino'),
            ]),
            'COL_estado_civil': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('', 'Selecione...'),
                ('SOLTEIRO', 'Solteiro(a)'),
                ('CASADO', 'Casado(a)'),
                ('DIVORCIADO', 'Divorciado(a)'),
                ('VIUVO', 'Viúvo(a)'),
                ('UNIAO_ESTAVEL', 'União Estável'),
            ]),
            'COL_cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000',
                'id': 'COL_cep',
                'data-mask': '00000-000',
                'maxlength': '9'
            }),
            'COL_endereco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Endereço completo',
                'id': 'COL_endereco',
                'maxlength': '200'
            }),
            'COL_numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número',
                'id': 'COL_numero',
                'maxlength': '10'
            }),
            'COL_complemento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Complemento (casa, apto, sala, etc.)',
                'id': 'COL_complemento',
                'maxlength': '100'
            }),
            'COL_bairro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bairro',
                'id': 'COL_bairro',
                'maxlength': '100'
            }),
            'COL_cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade',
                'id': 'COL_cidade',
                'maxlength': '100'
            }),
            'COL_estado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'UF',
                'maxlength': '2',
                'id': 'COL_estado',
                'pattern': r'[A-Za-z]{2}',
                'title': 'Digite a sigla do estado (ex: SP, RJ)'
            }),
            'COL_foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png,image/gif',
                'onchange': 'previewFoto(this)',
                'title': 'Formatos aceitos: JPG, PNG, GIF (máx. 5MB)'
            }),
            'COL_funcao_pretendida': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Catequista, Músico, Leitor, Ministro, etc.',
                'maxlength': '100',
                'list': 'funcoes-sugestoes'
            }),
        }
        
        labels = {
            'COL_telefone': '📱 Telefone *',
            'COL_nome_completo': '👤 Nome Completo *',
            'COL_apelido': '😊 Apelido/Como gosta de ser chamado',
            'COL_data_nascimento': '🎂 Data de Nascimento',
            'COL_sexo': '⚧ Sexo',
            'COL_estado_civil': '💒 Estado Civil',
            'COL_cep': '📮 CEP',
            'COL_endereco': '🏠 Endereço',
            'COL_numero': '🔢 Número',
            'COL_complemento': '🏢 Complemento',
            'COL_bairro': '🏘️ Bairro',
            'COL_cidade': '🏙️ Cidade',
            'COL_estado': '🌎 Estado',
            'COL_foto': '📷 Foto',
            'COL_funcao_pretendida': '⛪ Função/Ministério Pretendido',
        }
        
        help_texts = {
            'COL_telefone': 'Número com DDD para contato',
            'COL_nome_completo': 'Nome completo como no documento',
            'COL_apelido': 'Nome pelo qual gosta de ser chamado (opcional)',
            'COL_data_nascimento': 'Data de nascimento para parabenizar você',
            'COL_cep': 'CEP para preenchimento automático do endereço',
            'COL_foto': 'Foto opcional para identificação (máx. 5MB)',
            'COL_funcao_pretendida': 'Área em que gostaria de colaborar (ex: Catequese, Música, Liturgia)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Definir campos obrigatórios
        self.fields['COL_telefone'].required = True
        self.fields['COL_nome_completo'].required = True
        
        # Adicionar classes CSS para campos obrigatórios
        for field_name, field in self.fields.items():
            if field.required:
                current_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{current_class} required-field".strip()
        
        # Melhorar acessibilidade
        for field_name, field in self.fields.items():
            if 'id' in field.widget.attrs:
                field.widget.attrs['aria-describedby'] = f"{field.widget.attrs['id']}_help"
    
    def clean_COL_telefone(self):
        """Validação avançada do telefone"""
        telefone = self.cleaned_data.get('COL_telefone')
        
        if not telefone:
            raise ValidationError("Telefone é obrigatório")
        
        # Remove caracteres não numéricos
        telefone_limpo = re.sub(r'[^\d]', '', str(telefone))
        
        # Validar tamanho
        if len(telefone_limpo) < 10:
            raise ValidationError("Telefone deve ter pelo menos 10 dígitos (DDD + número)")
        elif len(telefone_limpo) > 11:
            raise ValidationError("Telefone deve ter no máximo 11 dígitos")
        
        # Validar DDD (mesmo código do dizimista)
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
        existing_query = TBCOLABORADORES.objects.filter(COL_telefone=telefone)
        if self.instance and self.instance.pk:
            existing_query = existing_query.exclude(pk=self.instance.pk)
        
        if existing_query.exists():
            colaborador_existente = existing_query.first()
            raise ValidationError(
                f"Este telefone já está cadastrado para: {colaborador_existente.COL_nome_completo} "
                f"(Status: {colaborador_existente.COL_status})"
            )
                
        return telefone
    
    def clean_COL_nome_completo(self):
        """Validação do nome"""
        nome = self.cleaned_data.get('COL_nome_completo')
        
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
    
    def clean_COL_cep(self):
        """Validação do CEP"""
        cep = self.cleaned_data.get('COL_cep')
        
        if cep:
            cep_limpo = re.sub(r'[^\d]', '', str(cep))
            if len(cep_limpo) != 8:
                raise ValidationError("CEP deve ter 8 dígitos")
            
            # Verificar se não é um CEP claramente inválido
            if cep_limpo == '00000000' or (cep_limpo[0] == '0' and len(set(cep_limpo)) == 1):
                raise ValidationError("CEP inválido")
        
        return cep
    
    def clean_COL_foto(self):
        """Validação da foto"""
        foto = self.cleaned_data.get('COL_foto')
        
        if foto:
            # Verificar tamanho (5MB máximo)
            if foto.size > 5 * 1024 * 1024:
                raise ValidationError("Foto deve ter no máximo 5MB")
            
            # Verificar formato
            valid_formats = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if foto.content_type not in valid_formats:
                raise ValidationError("Formato inválido. Use JPG, PNG ou GIF")
        
        return foto
    
    def clean_COL_funcao_pretendida(self):
        """Validação da função pretendida"""
        funcao = self.cleaned_data.get('COL_funcao_pretendida')
        
        if funcao:
            # Capitalizar primeira letra de cada palavra
            funcao = funcao.title().strip()
            
            # Lista de funções comuns para padronizar
            funcoes_padrao = {
                'catequista': 'Catequista',
                'musico': 'Músico',
                'leitor': 'Leitor',
                'ministro': 'Ministro Extraordinário',
                'coordenador': 'Coordenador',
                'secretario': 'Secretário',
                'tesoureiro': 'Tesoureiro',
                'zelador': 'Zelador',
                'liturgia': 'Liturgia',
                'pastoral': 'Pastoral',
                'evangelizacao': 'Evangelização',
                'social': 'Ação Social',
            }
            
            # Tentar padronizar com base nas palavras-chave
            funcao_lower = funcao.lower()
            for key, padrao in funcoes_padrao.items():
                if key in funcao_lower:
                    funcao = padrao
                    break
        
        return funcao
    
    def clean_COL_estado(self):
        """Validação do estado"""
        estado = self.cleaned_data.get('COL_estado')
        
        if estado:
            estado = estado.upper().strip()
            
            # Lista de estados válidos
            estados_validos = [
                'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
                'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
                'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
            ]
            
            if estado not in estados_validos:
                raise ValidationError("Estado inválido. Use a sigla (ex: SP, RJ)")
        
        return estado
    
    def clean_disponibilidade(self):
        """Validação da disponibilidade"""
        disponibilidade = self.cleaned_data.get('disponibilidade')
        
        # Converter lista para string separada por vírgulas para armazenar
        if disponibilidade:
            return ','.join(disponibilidade)
        
        return ''


# Alias para compatibilidade com código existente
# TODO: Remover após migração completa
ColaboradorPublicoForm = CadastroColaboradorForm