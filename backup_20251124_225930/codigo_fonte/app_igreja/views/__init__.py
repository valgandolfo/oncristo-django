# ==================== IMPORTAÇÕES DOS VIEWS ====================
# Importações das views específicas da área administrativa
from .admin_area.views_admin_area import admin_area
from .admin_area.views_dioceses import *
from .admin_area.views_paroquias import paroquia_generic_view
from .admin_area.views_visual import visual_generic_view
from .admin_area.views_relatorios import *
from .admin_area.views_celebracoes import *

# ==================== VIEWS DISPONÍVEIS ====================
# Views de Dioceses:
# - diocese_detail()

# Views de Paróquias:
# - paroquia_generic_view()

# Views de Relatórios:
# - (a serem implementadas)

# Views de Celebrações:
# - (a serem implementadas)
