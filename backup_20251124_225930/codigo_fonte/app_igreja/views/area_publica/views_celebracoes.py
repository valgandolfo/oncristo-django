from django.shortcuts import render
from django.db.models import Q
from django.contrib import messages

from ...models.area_admin.models_celebracoes import TBCELEBRACOES
from ...models.area_admin.models_paroquias import TBPAROQUIA


def minhas_celebracaoes_publico(request):
    """
    Área pública para consultar celebrações agendadas pelo telefone
    """
    # Buscar paróquia
    paroquia = TBPAROQUIA.objects.first()
    
    # Busca por telefone
    telefone = request.GET.get('telefone', '').strip()
    celebracaoes = None
    resultados_encontrados = False
    
    if telefone:
        # Remove caracteres não numéricos para busca
        telefone_limpo = ''.join(filter(str.isdigit, telefone))
        
        if len(telefone_limpo) >= 10:
            # Buscar por telefone (com e sem formatação)
            celebracaoes = TBCELEBRACOES.objects.filter(
                Q(CEL_telefone__icontains=telefone_limpo) | 
                Q(CEL_telefone__icontains=telefone) |
                Q(CEL_telefone__icontains=f"({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}")
            ).order_by('-CEL_data_celebracao', 'CEL_horario')
            
            resultados_encontrados = celebracaoes.exists()
            
            if not resultados_encontrados:
                messages.info(request, f'Nenhuma celebração encontrada para o telefone {telefone}')
        else:
            messages.warning(request, 'Digite um telefone válido com pelo menos 10 dígitos')
    context = {
        'paroquia': paroquia,
        'telefone': telefone,
        'celebracaoes': celebracaoes,
        'resultados_encontrados': resultados_encontrados,
        'total_encontrado': celebracaoes.count() if celebracaoes else 0,
    }
    
    return render(request, 'area_publica/bot_celebracoes_publico.html', context)

