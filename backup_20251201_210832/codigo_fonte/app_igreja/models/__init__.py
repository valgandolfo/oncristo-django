# ==================== IMPORTAÇÕES DOS MODELS ====================
# Importações dos models específicos organizados por área

# Models da área administrativa
from .area_admin.models_dioceses import TBDIOCESE
from .area_admin.models_paroquias import TBPAROQUIA
from .area_admin.models_funcoes import TBFUNCAO
from .area_admin.models_grupos import TBGRUPOS
from .area_admin.models_celebrantes import TBCELEBRANTES
from .area_admin.models_colaboradores import TBCOLABORADORES
from .area_admin.models_dizimistas import TBDIZIMISTAS, TBDOACAODIZIMO
from .area_admin.models_celebracoes import TBCELEBRACOES
from .area_admin.models_modelo import TBMODELO, TBITEM_MODELO

# Models da área pública (removido TBEVENTO - agora está em area_admin)

# Models gerais
from .area_admin.models_relatorios import TBRELATORIO

# Você pode adicionar aqui qualquer lógica de inicialização ou
# definir __all__ para controlar o que é exportado.

__all__ = [
    'TBDIOCESE',
    'TBPAROQUIA',
    'TBRELATORIO',
    'TBFUNCAO',
    'TBGRUPOS',
    'TBCELEBRANTES',
    'TBCOLABORADORES',
    'TBDIZIMISTAS',
    'TBDOACAODIZIMO',
    'TBCELEBRACOES',
    'TBMODELO',
    'TBITEM_MODELO',
]
