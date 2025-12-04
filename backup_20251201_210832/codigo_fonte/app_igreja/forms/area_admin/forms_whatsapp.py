"""
==================== FORMULÁRIOS DE WHATSAPP ====================
Arquivo com formulários específicos para envio de mensagens WhatsApp
"""

from django import forms
from django.core.exceptions import ValidationError
from ...models.area_admin.models_whatsapp import TBWHATSAPP
from ...models.area_admin.models_dizimistas import TBDIZIMISTAS
from ...models.area_admin.models_colaboradores import TBCOLABORADORES
from ...models.area_admin.models_grupos import TBGRUPOS
from .forms_commons import DateInputWidget


class MensagemWhatsAppForm(forms.Form):
    """Formulário para envio de mensagens WhatsApp"""
    
    TIPO_DESTINATARIO_CHOICES = [
        ('DIZIMISTAS', 'Dizimistas'),
        ('COLABORADORES', 'Colaboradores'),
        ('TODOS', 'Todos'),
    ]
    
    TIPO_MIDIA_CHOICES = [
        ('TEXTO', 'Texto'),
        ('IMAGEM', 'Imagem'),
        ('AUDIO', 'Áudio'),
        ('VIDEO', 'Vídeo'),
    ]
    
    FILTRAR_DIZIMISTA_CHOICES = [
        ('', 'Todos'),
        ('ATIVO', 'Ativos'),
        ('INATIVO', 'Inativos'),
    ]
    
    FILTRAR_COLABORADOR_CHOICES = [
        ('', 'Todos'),
        ('ATIVO', 'Ativos'),
        ('INATIVO', 'Inativos'),
        ('PENDENTE', 'Pendentes'),
    ]
    
    # Campos principais
    tipo_destinatario = forms.ChoiceField(
        choices=TIPO_DESTINATARIO_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Tipo de Destinatário',
        required=True
    )
    
    tipo_midia = forms.ChoiceField(
        choices=TIPO_MIDIA_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo_midia'}),
        label='Tipo de Mídia',
        required=True,
        initial='TEXTO'
    )
    
    texto = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '5',
            'id': 'id_texto',
            'placeholder': 'Digite sua mensagem aqui...'
        }),
        label='Mensagem',
        required=False,
        help_text='Campo obrigatório para mensagens de texto'
    )
    
    # Campos para dizimistas
    dizimista_especifico = forms.ModelChoiceField(
        queryset=TBDIZIMISTAS.objects.all().order_by('DIS_nome'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_dizimista_especifico'}),
        label='Dizimista Específico',
        help_text='Selecione um dizimista específico ou deixe em branco para usar filtros'
    )
    
    filtrar_dizimista = forms.ChoiceField(
        choices=FILTRAR_DIZIMISTA_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_filtrar_dizimista'}),
        label='Filtrar Dizimistas por Status'
    )
    
    data_nascimento_dizimista_inicio = forms.DateField(
        required=False,
        widget=DateInputWidget(attrs={'class': 'form-control', 'id': 'id_data_nascimento_dizimista_inicio'}),
        label='Data de Nascimento (Início)',
        help_text='Filtrar dizimistas com aniversário a partir desta data'
    )
    
    data_nascimento_dizimista_fim = forms.DateField(
        required=False,
        widget=DateInputWidget(attrs={'class': 'form-control', 'id': 'id_data_nascimento_dizimista_fim'}),
        label='Data de Nascimento (Fim)',
        help_text='Filtrar dizimistas com aniversário até esta data'
    )
    
    # Campos para colaboradores
    colaborador_especifico = forms.ModelChoiceField(
        queryset=TBCOLABORADORES.objects.all().order_by('COL_nome_completo'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_colaborador_especifico'}),
        label='Colaborador Específico',
        help_text='Selecione um colaborador específico ou deixe em branco para usar filtros'
    )
    
    filtrar_colaborador = forms.ChoiceField(
        choices=FILTRAR_COLABORADOR_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_filtrar_colaborador'}),
        label='Filtrar Colaboradores por Status'
    )
    
    grupo_colaborador = forms.ModelChoiceField(
        queryset=TBGRUPOS.objects.filter(GRU_ativo=True).order_by('GRU_nome_grupo'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_grupo_colaborador'}),
        label='Grupo',
        help_text='Filtrar colaboradores por grupo'
    )
    
    data_nascimento_colaborador_inicio = forms.DateField(
        required=False,
        widget=DateInputWidget(attrs={'class': 'form-control', 'id': 'id_data_nascimento_colaborador_inicio'}),
        label='Data de Nascimento (Início)',
        help_text='Filtrar colaboradores com aniversário a partir desta data'
    )
    
    data_nascimento_colaborador_fim = forms.DateField(
        required=False,
        widget=DateInputWidget(attrs={'class': 'form-control', 'id': 'id_data_nascimento_colaborador_fim'}),
        label='Data de Nascimento (Fim)',
        help_text='Filtrar colaboradores com aniversário até esta data'
    )
    
    # Campos de mídia - Imagem
    url_imagem = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'id': 'id_url_imagem',
            'placeholder': 'https://exemplo.com/imagem.jpg'
        }),
        label='URL da Imagem',
        help_text='URL pública da imagem (ImgBB, Imgur, etc.)'
    )
    
    arquivo_imagem = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'id': 'id_arquivo_imagem',
            'accept': 'image/*',
            'onchange': 'previewImagem(this)'
        }),
        label='Arquivo de Imagem',
        help_text='Ou faça upload de uma imagem'
    )
    
    legenda_imagem = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '3',
            'id': 'id_legenda_imagem',
            'placeholder': 'Legenda da imagem (opcional)'
        }),
        label='Legenda da Imagem',
        max_length=1000
    )
    
    # Campos de mídia - Áudio
    url_audio = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'id': 'id_url_audio',
            'placeholder': 'https://exemplo.com/audio.mp3'
        }),
        label='URL do Áudio',
        help_text='URL pública do áudio'
    )
    
    arquivo_audio = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'id': 'id_arquivo_audio',
            'accept': 'audio/*',
            'onchange': 'previewAudio(this)'
        }),
        label='Arquivo de Áudio',
        help_text='Ou faça upload de um arquivo de áudio'
    )
    
    # Campos de mídia - Vídeo
    url_video = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'id': 'id_url_video',
            'placeholder': 'https://exemplo.com/video.mp4'
        }),
        label='URL do Vídeo',
        help_text='URL pública do vídeo'
    )
    
    arquivo_video = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'id': 'id_arquivo_video',
            'accept': 'video/*',
            'onchange': 'previewVideo(this)'
        }),
        label='Arquivo de Vídeo',
        help_text='Ou faça upload de um arquivo de vídeo'
    )
    
    legenda_video = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '3',
            'id': 'id_legenda_video',
            'placeholder': 'Legenda do vídeo (opcional)'
        }),
        label='Legenda do Vídeo',
        max_length=1000
    )
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_midia = cleaned_data.get('tipo_midia')
        texto = cleaned_data.get('texto')
        
        # Validar que texto é obrigatório para mensagens de texto
        if tipo_midia == 'TEXTO' and not texto:
            raise ValidationError({
                'texto': 'O campo de mensagem é obrigatório para mensagens de texto.'
            })
        
        # Validar que há pelo menos uma mídia para tipos de mídia
        if tipo_midia == 'IMAGEM':
            url_imagem = cleaned_data.get('url_imagem')
            arquivo_imagem = cleaned_data.get('arquivo_imagem')
            if not url_imagem and not arquivo_imagem:
                raise ValidationError({
                    'url_imagem': 'Informe uma URL ou faça upload de uma imagem.',
                    'arquivo_imagem': 'Informe uma URL ou faça upload de uma imagem.'
                })
        
        if tipo_midia == 'AUDIO':
            url_audio = cleaned_data.get('url_audio')
            arquivo_audio = cleaned_data.get('arquivo_audio')
            if not url_audio and not arquivo_audio:
                raise ValidationError({
                    'url_audio': 'Informe uma URL ou faça upload de um áudio.',
                    'arquivo_audio': 'Informe uma URL ou faça upload de um áudio.'
                })
        
        if tipo_midia == 'VIDEO':
            url_video = cleaned_data.get('url_video')
            arquivo_video = cleaned_data.get('arquivo_video')
            if not url_video and not arquivo_video:
                raise ValidationError({
                    'url_video': 'Informe uma URL ou faça upload de um vídeo.',
                    'arquivo_video': 'Informe uma URL ou faça upload de um vídeo.'
                })
        
        return cleaned_data

