# ==================== IMPORTS DOS MODELOS ADMIN ====================
# Importa todos os modelos da área administrativa

from .models_dioceses import TBDIOCESE
from .models_paroquias import TBPAROQUIA
from .models_grupos import TBGRUPOS
from .models_funcoes import TBFUNCAO
from .models_celebrantes import TBCELEBRANTES
from .models_colaboradores import TBCOLABORADORES
from .models_dizimistas import TBDIZIMISTAS, TBGERDIZIMO
from .models_celebracoes import TBCELEBRACOES
from .models_avisos import TBAVISO
from .models_oracoes import TBORACOES
from .models_planos import TBPLANO, TBITEMPLANO
from .models_eventos import TBEVENTO, TBITEM_EVENTO
from .models_mural import TBMURAL
from .models_modelo import TBMODELO, TBITEM_MODELO
from .models_escala import TBESCALA, TBITEM_ESCALA
from .models_whatsapp import TBWHATSAPP
from .models_visual import TBVISUAL
from .models_banners import TBBANNERS
from .models_agenda_mes import TBAGENDAMES, TBITEAGENDAMES
from .models_extrator_liturgias import TBLITURGIA

__all__ = [
    'TBDIOCESE',
    'TBPAROQUIA', 
    'TBGRUPOS',
    'TBFUNCAO',
    'TBCELEBRANTES',
    'TBCOLABORADORES',
    'TBDIZIMISTAS',
    'TBCELEBRACOES',
    'TBAVISO',
    'TBORACOES',
    'TBPLANO',
    'TBITEMPLANO',
    'TBEVENTO',
    'TBITEM_EVENTO',
    'TBESCALA',
    'TBITEM_ESCALA',
    'TBWHATSAPP',
    'TBMURAL',
    'TBVISUAL',
    'TBBANNERS',
    'TBAGENDAMES',
    'TBITEAGENDAMES',
    'TBLITURGIA',
]
