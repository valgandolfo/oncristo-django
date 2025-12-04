from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, date
from django.db.models import Q

from ...models.area_admin.models_dizimistas import TBDIZIMISTAS
from ...models.area_admin.models_colaboradores import TBCOLABORADORES
from ...models.area_admin.models_paroquias import TBPAROQUIA


def aniversariantes_mes(request):
    """
    Área pública para visualizar aniversariantes do mês
    Filtro por data (até o mês) e tipo (Dizimista/Colaborador)
    Só busca dados quando o usuário clicar em "Buscar"
    """
    # Buscar paróquia
    paroquia = TBPAROQUIA.objects.first()
    
    # Valores iniciais
    aniversariantes = []
    busca_realizada = False
    
    # Verificar se há parâmetros de busca (usuário clicou em "Buscar")
    data_filtro_str = request.GET.get('data', '').strip()
    tipo_filtro = request.GET.get('tipo', '').strip().upper()
    
    # Só busca se houver parâmetros de busca
    if data_filtro_str or tipo_filtro:
        busca_realizada = True
        
        mes_ano = None
        
        if data_filtro_str:
            try:
                # Se veio no formato YYYY-MM
                if len(data_filtro_str) == 7:
                    mes_ano = datetime.strptime(data_filtro_str, '%Y-%m')
                # Se veio no formato YYYY-MM-DD, pega só mês e ano
                elif len(data_filtro_str) == 10:
                    mes_ano = datetime.strptime(data_filtro_str, '%Y-%m-%d')
            except ValueError:
                pass
        
        # Se não tiver filtro de data, usa o mês atual
        if not mes_ano:
            hoje = timezone.now().date()
            mes = hoje.month
        else:
            mes = mes_ano.month
        
        # Se não tiver filtro de tipo, usa TODOS
        if not tipo_filtro:
            tipo_filtro = 'TODOS'
        
        # Buscar Dizimistas
        if tipo_filtro in ['TODOS', 'DIZIMISTA']:
            dizimistas = TBDIZIMISTAS.objects.filter(
                DIS_data_nascimento__isnull=False,
                DIS_status=True  # Apenas ativos
            )
            
            # Filtrar pelo mês de aniversário (qualquer ano, apenas o mês)
            dizimistas = dizimistas.filter(DIS_data_nascimento__month=mes)
            
            for dizimista in dizimistas:
                if dizimista.DIS_data_nascimento:  # Verifica se tem data válida
                    aniversariantes.append({
                        'nome': dizimista.DIS_nome,
                        'data_aniversario': dizimista.DIS_data_nascimento,
                        'tipo': 'Dizimista',
                        'id': dizimista.pk,  # Usa pk (id automático do Django)
                    })
        
        # Buscar Colaboradores
        if tipo_filtro in ['TODOS', 'COLABORADOR']:
            colaboradores = TBCOLABORADORES.objects.filter(
                COL_data_nascimento__isnull=False,
                COL_status='ATIVO'  # Apenas ativos
            )
            
            # Filtrar pelo mês de aniversário (qualquer ano, apenas o mês)
            colaboradores = colaboradores.filter(COL_data_nascimento__month=mes)
            
            for colaborador in colaboradores:
                if colaborador.COL_data_nascimento:  # Verifica se tem data válida
                    aniversariantes.append({
                        'nome': colaborador.COL_nome_completo,
                        'data_aniversario': colaborador.COL_data_nascimento,
                        'tipo': 'Colaborador',
                        'id': colaborador.COL_id,
                    })
        
        # Ordenar por dia do aniversário
        aniversariantes.sort(key=lambda x: x['data_aniversario'].day if x['data_aniversario'] else 0)
    
    # Preparar data para exibição no campo (formato YYYY-MM)
    if data_filtro_str and len(data_filtro_str) >= 7:
        data_input_value = data_filtro_str[:7]  # Pega YYYY-MM
    else:
        hoje = timezone.now().date()
        data_input_value = hoje.strftime('%Y-%m')
    
    # Se não tiver tipo, usar TODOS como padrão
    if not tipo_filtro:
        tipo_filtro = 'TODOS'
    
    context = {
        'paroquia': paroquia,
        'aniversariantes': aniversariantes,
        'data_filtro': data_input_value,
        'tipo_filtro': tipo_filtro,
        'total_encontrado': len(aniversariantes),
        'busca_realizada': busca_realizada,
    }
    
    return render(request, 'area_publica/tpl_aniversariantes_publico.html', context)

