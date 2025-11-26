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
