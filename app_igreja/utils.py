# Constantes do sistema
# Valores fixos utilizados em todo o projeto

# Estados do Brasil
ESTADOS_BRASIL = [
    ('', 'Selecione...'),
    ('AC', 'Acre'),
    ('AL', 'Alagoas'),
    ('AP', 'Amapá'),
    ('AM', 'Amazonas'),
    ('BA', 'Bahia'),
    ('CE', 'Ceará'),
    ('DF', 'Distrito Federal'),
    ('ES', 'Espírito Santo'),
    ('GO', 'Goiás'),
    ('MA', 'Maranhão'),
    ('MT', 'Mato Grosso'),
    ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'),
    ('PA', 'Pará'),
    ('PB', 'Paraíba'),
    ('PR', 'Paraná'),
    ('PE', 'Pernambuco'),
    ('PI', 'Piauí'),
    ('RJ', 'Rio de Janeiro'),
    ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'),
    ('RO', 'Rondônia'),
    ('RR', 'Roraima'),
    ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'),
    ('SE', 'Sergipe'),
    ('TO', 'Tocantins'),
]

# Tipos de PIX
TIPOS_PIX = [
    ('cpf', 'CPF'),
    ('cnpj', 'CNPJ'),
    ('email', 'E-mail'),
    ('telefone', 'Telefone'),
    ('aleatoria', 'Chave Aleatória'),
]

# Configurações de Upload
MAX_SIZE_FOTO = 5 * 1024 * 1024  # 5MB
EXTENSOES_FOTO = ['.jpg', '.jpeg', '.png', '.gif']

# Configurações de Redimensionamento de Imagens
MAX_WIDTH_IMAGE = 1920  # Largura máxima em pixels
MAX_HEIGHT_IMAGE = 1080  # Altura máxima em pixels
IMAGE_QUALITY = 85  # Qualidade JPEG (0-100)


def reconstruir_url_com_filtros(request, nome_view, filtros_list):
    """
    Reconstrói URL com filtros preservados do POST (campos hidden).
    nome_view: ex. 'app_igreja:listar_colaboradores'
    filtros_list: ex. ['busca_telefone', 'busca_nome', 'page']
    """
    from django.urls import reverse
    params = [f"{filtro}={request.POST.get(filtro, '')}" for filtro in filtros_list if request.POST.get(filtro)]
    query_string = '&'.join(params)
    return f"{reverse(nome_view)}?{query_string}" if query_string else reverse(nome_view)
