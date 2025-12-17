"""
Template Tags Customizadas - DRY Principle
Sistema On Cristo
"""

from django import template
from django.utils.safestring import mark_safe
from datetime import datetime

register = template.Library()

# ============================================================================
# CONSTANTES
# ============================================================================

MESES = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

DIAS_SEMANA = [
    'Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira',
    'Quinta-feira', 'Sexta-feira', 'Sábado'
]

ESTADOS_UF = {
    'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
    'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
    'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
    'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
    'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
    'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
    'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
}

STATUS_COLABORADOR = {
    'ATIVO': {'label': 'Ativo', 'class': 'bg-success'},
    'PENDENTE': {'label': 'Pendente', 'class': 'bg-warning'},
    'INATIVO': {'label': 'Inativo', 'class': 'bg-danger'}
}

SEXO = {
    'M': 'Masculino',
    'F': 'Feminino'
}

# ============================================================================
# FILTROS DE FORMATAÇÃO
# ============================================================================

@register.filter
def formatar_data_brasileira(data, formato='dd/mm/yyyy'):
    """
    Formata data para exibição brasileira
    """
    if not data:
        return 'Não informado'
    
    try:
        if isinstance(data, str):
            data = datetime.strptime(data, '%Y-%m-%d')
        
        dia = data.day
        mes = data.month
        ano = data.year
        hora = data.hour
        minuto = data.minute
        
        if formato == 'dd/mm/yyyy':
            return f"{dia:02d}/{mes:02d}/{ano}"
        elif formato == 'dd/mm/yyyy hh:mm':
            return f"{dia:02d}/{mes:02d}/{ano} {hora:02d}:{minuto:02d}"
        elif formato == 'dd de mês de yyyy':
            return f"{dia} de {MESES[mes-1]} de {ano}"
        elif formato == 'dia da semana, dd de mês de yyyy':
            return f"{DIAS_SEMANA[data.weekday()]}, {dia} de {MESES[mes-1]} de {ano}"
        else:
            return f"{dia:02d}/{mes:02d}/{ano}"
    except:
        return 'Data inválida'

@register.filter
def formatar_telefone(telefone):
    """
    Formata telefone brasileiro
    """
    if not telefone:
        return 'Não informado'
    
    numeros = ''.join(filter(str.isdigit, telefone))
    
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    elif len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    
    return telefone

@register.filter
def formatar_cep(cep):
    """
    Formata CEP brasileiro
    """
    if not cep:
        return 'Não informado'
    
    numeros = ''.join(filter(str.isdigit, cep))
    if len(numeros) == 8:
        return f"{numeros[:5]}-{numeros[5:]}"
    
    return cep

@register.filter
def formatar_cpf(cpf):
    """
    Formata CPF brasileiro
    """
    if not cpf:
        return 'Não informado'
    
    numeros = ''.join(filter(str.isdigit, cpf))
    if len(numeros) == 11:
        return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
    
    return cpf

@register.filter
def nome_estado(uf):
    """
    Obtém nome completo do estado pela UF
    """
    return ESTADOS_UF.get(uf, uf)

@register.filter
def nome_mes(numero_mes):
    """
    Obtém nome do mês pelo número
    """
    if 1 <= numero_mes <= 12:
        return MESES[numero_mes - 1]
    return 'Mês inválido'

@register.filter
def nome_dia_semana(numero_dia):
    """
    Obtém nome do dia da semana pelo número (0-6, onde 0 = domingo)
    """
    if 0 <= numero_dia <= 6:
        return DIAS_SEMANA[numero_dia]
    return 'Dia inválido'

# ============================================================================
# FILTROS DE BADGE
# ============================================================================

@register.filter
def badge_status(status):
    """
    Cria badge Bootstrap para status
    """
    status_info = STATUS_COLABORADOR.get(status)
    if not status_info:
        return mark_safe(f'<span class="badge bg-secondary">{status}</span>')
    
    return mark_safe(f'<span class="badge {status_info["class"]}">{status_info["label"]}</span>')

@register.filter
def badge_sexo(sexo):
    """
    Cria badge Bootstrap para sexo
    """
    sexo_info = SEXO.get(sexo)
    if not sexo_info:
        return mark_safe('<span class="badge bg-secondary">Não informado</span>')
    
    return mark_safe(f'<span class="badge bg-info">{sexo_info}</span>')

@register.filter
def badge_membro_ativo(ativo):
    """
    Cria badge Bootstrap para membro ativo
    """
    if ativo:
        return mark_safe('<span class="badge bg-success">Sim</span>')
    else:
        return mark_safe('<span class="badge bg-secondary">Não</span>')

# ============================================================================
# FILTROS DE ENDEREÇO
# ============================================================================

@register.filter
def endereco_completo(endereco_dict):
    """
    Formata endereço completo
    """
    if not endereco_dict:
        return 'Não informado'
    
    partes = []
    
    if endereco_dict.get('endereco'):
        endereco_completo = endereco_dict['endereco']
        if endereco_dict.get('numero'):
            endereco_completo += f", {endereco_dict['numero']}"
        if endereco_dict.get('complemento'):
            endereco_completo += f", {endereco_dict['complemento']}"
        partes.append(endereco_completo)
    
    if endereco_dict.get('bairro'):
        partes.append(endereco_dict['bairro'])
    if endereco_dict.get('cidade'):
        partes.append(endereco_dict['cidade'])
    if endereco_dict.get('estado'):
        partes.append(endereco_dict['estado'])
    if endereco_dict.get('cep'):
        partes.append(formatar_cep(endereco_dict['cep']))
    
    return ' - '.join(partes) if partes else 'Não informado'

# ============================================================================
# FILTROS DE VALIDAÇÃO
# ============================================================================

@register.filter
def validar_cpf(cpf):
    """
    Valida CPF brasileiro
    """
    if not cpf:
        return False
    
    numeros = ''.join(filter(str.isdigit, cpf))
    if len(numeros) != 11:
        return False
    
    # Verificar se todos os dígitos são iguais
    if len(set(numeros)) == 1:
        return False
    
    # Validar dígitos verificadores
    soma = sum(int(numeros[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(numeros[9]) != digito1:
        return False
    
    soma = sum(int(numeros[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    return int(numeros[10]) == digito2

@register.filter
def validar_cep(cep):
    """
    Valida CEP brasileiro
    """
    if not cep:
        return False
    
    numeros = ''.join(filter(str.isdigit, cep))
    return len(numeros) == 8 and numeros.isdigit()

@register.filter
def validar_email(email):
    """
    Valida email
    """
    if not email:
        return False
    
    import re
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return bool(re.match(pattern, email))

# ============================================================================
# FILTROS DE FORMATAÇÃO DE NÚMEROS
# ============================================================================

@register.filter
def formatar_moeda(valor):
    """
    Formata valor como moeda brasileira
    """
    if not valor:
        return 'R$ 0,00'
    
    try:
        valor_float = float(valor)
        return f"R$ {valor_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return 'Valor inválido'

@register.filter
def formatar_numero(numero):
    """
    Formata número com separadores de milhares
    """
    if not numero:
        return '0'
    
    try:
        numero_float = float(numero)
        return f"{numero_float:,.0f}".replace(',', '.')
    except:
        return 'Número inválido'

# ============================================================================
# FILTROS DE FORMATAÇÃO DE TEXTO
# ============================================================================

@register.filter
def capitalizar(texto):
    """
    Capitaliza primeira letra de cada palavra
    """
    if not texto:
        return ''
    
    return ' '.join(word.capitalize() for word in texto.split())

@register.filter
def truncar_texto(texto, tamanho=50):
    """
    Trunca texto no tamanho especificado
    """
    if not texto:
        return ''
    
    if len(texto) <= tamanho:
        return texto
    
    return texto[:tamanho] + '...'

@register.filter
def remover_acentos(texto):
    """
    Remove acentos do texto
    """
    if not texto:
        return ''
    
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

# ============================================================================
# FILTROS DE FORMATAÇÃO DE LISTA
# ============================================================================

@register.filter
def join_lista(lista, separador=', '):
    """
    Junta lista com separador
    """
    if not lista:
        return ''
    
    return separador.join(str(item) for item in lista)

@register.filter
def contar_itens(lista):
    """
    Conta itens em uma lista
    """
    if not lista:
        return 0
    
    return len(lista)

# ============================================================================
# FILTROS DE FORMATAÇÃO DE DATA RELATIVA
# ============================================================================

@register.filter
def tempo_relativo(data):
    """
    Formata data como tempo relativo (ex: "há 2 dias")
    """
    if not data:
        return 'Não informado'
    
    try:
        from django.utils import timezone
        from django.utils.timesince import timesince
        
        agora = timezone.now()
        if isinstance(data, str):
            data = datetime.strptime(data, '%Y-%m-%d')
        
        if data > agora:
            return 'Futuro'
        
        return f"há {timesince(data, agora)}"
    except:
        return 'Data inválida'

# ============================================================================
# TEMPLATE TAGS - GERADORES DE HTML
# ============================================================================

@register.simple_tag
def opcoes_mes(mes_selecionado=None, incluir_todos=False):
    """
    Gera opções HTML para um select de meses.
    
    Args:
        mes_selecionado: Número do mês selecionado (1-12) ou string
        incluir_todos: Se True, adiciona opção "Todos" com value=""
    
    Returns:
        String HTML com as opções do select
    """
    opcoes = []
    
    # Converter mes_selecionado para int se for string
    if mes_selecionado:
        try:
            mes_selecionado = int(mes_selecionado)
        except (ValueError, TypeError):
            mes_selecionado = None
    
    # Adicionar opção "Todos" se solicitado
    if incluir_todos:
        opcoes.append('<option value="">Selecione...</option>')
    
    # Gerar opções para cada mês
    for num_mes in range(1, 13):
        nome_mes = MESES[num_mes - 1]
        selected = 'selected' if mes_selecionado == num_mes else ''
        opcoes.append(f'<option value="{num_mes}" {selected}>{nome_mes}</option>')
    
    return mark_safe('\n'.join(opcoes))

@register.filter
def get_item(dictionary, key):
    """
    Obtém item de um dicionário pela chave
    """
    if dictionary and isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.simple_tag(takes_context=True)
def url_com_parametros(context, page_number=None):
    """
    Constrói URL preservando todos os parâmetros GET existentes e substituindo/adicional o parâmetro 'page'.
    
    Args:
        context: Contexto do template (automático)
        page_number: Número da página (opcional)
    
    Returns:
        String com a URL completa incluindo todos os parâmetros GET
    """
    from urllib.parse import urlencode
    
    request = context.get('request')
    if not request:
        return f"?page={page_number}" if page_number else "?"
    
    # Obter todos os parâmetros GET
    params = dict(request.GET.items())
    
    # Atualizar ou adicionar o parâmetro page
    if page_number:
        params['page'] = page_number
    elif 'page' in params:
        # Se não especificar page_number mas houver page nos params, manter
        pass
    
    # Construir query string
    if params:
        return f"?{urlencode(params)}"
    return "?"
