"""
Views para Relatórios da Área Administrativa
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse
from datetime import datetime, date
from django.db.models import Q
import logging

from ...models.area_admin.models_dizimistas import TBDIZIMISTAS
from ...models.area_admin.models_colaboradores import TBCOLABORADORES
from ...models.area_admin.models_paroquias import TBPAROQUIA
from ...models.area_admin.models_escala import TBESCALA, TBITEM_ESCALA
from ...models.area_admin.models_grupos import TBGRUPOS
from ...models.area_admin.models_funcoes import TBFUNCAO

logger = logging.getLogger(__name__)


def admin_required(view_func):
    """Decorator para verificar se o usuário é admin"""
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            from django.contrib import messages
            from django.shortcuts import redirect
            messages.error(request, 'Acesso negado. Apenas administradores podem acessar esta área.')
            return redirect('app_igreja:admin_area')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_required
@admin_required
def relatorio_aniversariantes(request):
    """
    Relatório de Aniversariantes - Área Administrativa
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
                        'id': dizimista.pk,
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
        'titulo_relatorio': 'RELATÓRIO DE ANIVERSARIANTES',
        'titulo_filtro': 'Aniversariantes',
    }
    
    return render(request, 'admin_area/tpl_relatorio_aniversariantes.html', context)


@login_required
@admin_required
def relatorio_escala_mensal_missas(request):
    """
    Relatório de Escala Mensal de Missas - Área Administrativa
    Filtros: mês, ano, colaborador, função, status, grupo, situação
    Só busca dados quando o usuário clicar em "Buscar"
    """
    from datetime import date
    
    # Buscar paróquia
    paroquia = TBPAROQUIA.objects.first()
    
    # Buscar listas para os filtros
    colaboradores = TBCOLABORADORES.objects.filter(COL_status='ATIVO').order_by('COL_nome_completo')
    funcoes = TBFUNCAO.objects.all().order_by('FUN_nome_funcao')
    grupos = TBGRUPOS.objects.all().order_by('GRU_nome_grupo')
    
    # Valores iniciais
    itens_escala = []
    busca_realizada = False
    
    # Verificar se há parâmetros de busca (usuário clicou em "Buscar")
    mes_str = request.GET.get('mes', '').strip()
    ano_str = request.GET.get('ano', '').strip()
    colaborador_id = request.GET.get('colaborador', '').strip()
    funcao_id = request.GET.get('funcao', '').strip()
    status = request.GET.get('status', '').strip()
    grupo_id = request.GET.get('grupo', '').strip()
    situacao = request.GET.get('situacao', '').strip()
    
    # Só busca se houver pelo menos mês e ano
    if mes_str and ano_str:
        busca_realizada = True
        
        try:
            mes = int(mes_str)
            ano = int(ano_str)
            
            # Validar mês e ano
            if mes < 1 or mes > 12:
                mes = None
                ano = None
            elif ano < 2000 or ano > 2100:
                mes = None
                ano = None
            else:
                # Buscar escala master
                primeiro_dia_mes = date(ano, mes, 1)
                escala_master = TBESCALA.objects.filter(ESC_MESANO=primeiro_dia_mes).first()
                
                if escala_master:
                    # Buscar itens da escala com filtros
                    itens = TBITEM_ESCALA.objects.filter(
                        ITE_ESC_ESCALA=escala_master
                    )
                    
                    # Aplicar filtros
                    if colaborador_id:
                        try:
                            colaborador_id_int = int(colaborador_id)
                            itens = itens.filter(ITE_ESC_COLABORADOR=colaborador_id_int)
                        except (ValueError, TypeError):
                            pass
                    
                    if funcao_id:
                        try:
                            funcao_id_int = int(funcao_id)
                            itens = itens.filter(ITE_ESC_FUNCAO=funcao_id_int)
                        except (ValueError, TypeError):
                            pass
                    
                    if status:
                        itens = itens.filter(ITE_ESC_STATUS=status)
                    
                    if grupo_id:
                        try:
                            grupo_id_int = int(grupo_id)
                            itens = itens.filter(ITE_ESC_GRUPO=grupo_id_int)
                        except (ValueError, TypeError):
                            pass
                    
                    if situacao:
                        if situacao == 'true':
                            itens = itens.filter(ITE_ESC_SITUACAO=True)
                        elif situacao == 'false':
                            itens = itens.filter(ITE_ESC_SITUACAO=False)
                    
                    itens = itens.order_by('ITE_ESC_DATA', 'ITE_ESC_HORARIO')
                    
                    # Organizar por dia para exibição
                    dias_semana_pt = {
                        0: 'Segunda-feira',
                        1: 'Terça-feira',
                        2: 'Quarta-feira',
                        3: 'Quinta-feira',
                        4: 'Sexta-feira',
                        5: 'Sábado',
                        6: 'Domingo'
                    }
                    
                    meses_pt = [
                        '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
                    ]
                    
                    # Adicionar informações para cada item
                    for item in itens:
                        item.dia_semana_nome = dias_semana_pt.get(item.ITE_ESC_DATA.weekday(), '')
                        
                        # Buscar nome do colaborador
                        if item.ITE_ESC_COLABORADOR:
                            try:
                                colaborador = TBCOLABORADORES.objects.get(COL_id=item.ITE_ESC_COLABORADOR)
                                item.colaborador_nome = colaborador.COL_nome_completo
                            except TBCOLABORADORES.DoesNotExist:
                                item.colaborador_nome = '-'
                        else:
                            item.colaborador_nome = '-'
                        
                        # Buscar nome da função
                        if item.ITE_ESC_FUNCAO:
                            try:
                                funcao = TBFUNCAO.objects.get(FUN_id=item.ITE_ESC_FUNCAO)
                                item.funcao_nome = funcao.FUN_nome_funcao
                            except TBFUNCAO.DoesNotExist:
                                item.funcao_nome = '-'
                        else:
                            item.funcao_nome = '-'
                        
                        # Buscar nome do grupo
                        if item.ITE_ESC_GRUPO:
                            try:
                                grupo = TBGRUPOS.objects.get(GRU_id=item.ITE_ESC_GRUPO)
                                item.grupo_nome = grupo.GRU_nome_grupo
                            except TBGRUPOS.DoesNotExist:
                                item.grupo_nome = '-'
                        else:
                            item.grupo_nome = '-'
                    
                    itens_escala = list(itens)
                    
        except (ValueError, TypeError):
            mes = None
            ano = None
    
    # Preparar valores para exibição nos campos
    if mes_str:
        mes_value = mes_str
    else:
        hoje = date.today()
        mes_value = str(hoje.month)
    
    if ano_str:
        ano_value = ano_str
    else:
        hoje = date.today()
        ano_value = str(hoje.year)
    
    meses_pt = [
        '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    
    mes_nome = ''
    if mes_str and mes_str.isdigit():
        try:
            mes_int = int(mes_str)
            if 1 <= mes_int <= 12:
                mes_nome = meses_pt[mes_int]
        except:
            pass
    
    context = {
        'paroquia': paroquia,
        'itens_escala': itens_escala,
        'mes': mes_value,
        'ano': ano_value,
        'mes_nome': mes_nome,
        'colaborador_id': colaborador_id,
        'funcao_id': funcao_id,
        'status': status,
        'grupo_id': grupo_id,
        'situacao': situacao,
        'colaboradores': colaboradores,
        'funcoes': funcoes,
        'grupos': grupos,
        'total_encontrado': len(itens_escala),
        'busca_realizada': busca_realizada,
        'titulo_relatorio': 'RELATÓRIO DE ESCALA MENSAL DE MISSAS',
        'titulo_filtro': 'Escala Mensal',
    }
    
    return render(request, 'admin_area/tpl_relatorio_escala_mensal_missas.html', context)


@login_required
@admin_required
def relatorio_aniversariantes_pdf(request):
    """
    Gera PDF do Relatório de Aniversariantes
    """
    try:
        from weasyprint import HTML
        from django.template.loader import render_to_string
        from io import BytesIO
        
        # Buscar paróquia
        paroquia = TBPAROQUIA.objects.first()
        
        # Buscar dados (mesma lógica da view principal)
        aniversariantes = []
        data_filtro_str = request.GET.get('data', '').strip()
        tipo_filtro = request.GET.get('tipo', '').strip().upper()
        mes_ano = None
        
        if data_filtro_str:
            try:
                if len(data_filtro_str) == 7:
                    mes_ano = datetime.strptime(data_filtro_str, '%Y-%m')
                elif len(data_filtro_str) == 10:
                    mes_ano = datetime.strptime(data_filtro_str, '%Y-%m-%d')
            except ValueError:
                pass
        
        if not mes_ano:
            hoje = timezone.now().date()
            mes = hoje.month
        else:
            mes = mes_ano.month
        
        if not tipo_filtro:
            tipo_filtro = 'TODOS'
        
        # Buscar Dizimistas
        if tipo_filtro in ['TODOS', 'DIZIMISTA']:
            dizimistas = TBDIZIMISTAS.objects.filter(
                DIS_data_nascimento__isnull=False,
                DIS_status=True
            ).filter(DIS_data_nascimento__month=mes)
            
            for dizimista in dizimistas:
                if dizimista.DIS_data_nascimento:
                    aniversariantes.append({
                        'nome': dizimista.DIS_nome,
                        'data_aniversario': dizimista.DIS_data_nascimento,
                        'tipo': 'Dizimista',
                        'id': dizimista.pk,
                    })
        
        # Buscar Colaboradores
        if tipo_filtro in ['TODOS', 'COLABORADOR']:
            colaboradores = TBCOLABORADORES.objects.filter(
                COL_data_nascimento__isnull=False,
                COL_status='ATIVO'
            ).filter(COL_data_nascimento__month=mes)
            
            for colaborador in colaboradores:
                if colaborador.COL_data_nascimento:
                    aniversariantes.append({
                        'nome': colaborador.COL_nome_completo,
                        'data_aniversario': colaborador.COL_data_nascimento,
                        'tipo': 'Colaborador',
                        'id': colaborador.COL_id,
                    })
        
        aniversariantes.sort(key=lambda x: x['data_aniversario'].day if x['data_aniversario'] else 0)
        
        # Preparar data para exibição
        if data_filtro_str and len(data_filtro_str) >= 7:
            data_input_value = data_filtro_str[:7]
        else:
            hoje = timezone.now().date()
            data_input_value = hoje.strftime('%Y-%m')
        
        if not tipo_filtro:
            tipo_filtro = 'TODOS'
        
        context = {
            'paroquia': paroquia,
            'aniversariantes': aniversariantes,
            'data_filtro': data_input_value,
            'tipo_filtro': tipo_filtro,
            'total_encontrado': len(aniversariantes),
            'titulo_relatorio': 'RELATÓRIO DE ANIVERSARIANTES',
        }
        
        # Renderizar template HTML para PDF
        html_string = render_to_string('admin_area/tpl_relatorio_aniversariantes_pdf.html', context)
        
        # Gerar PDF
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf_file = html.write_pdf()
        
        # Criar resposta HTTP
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="relatorio_aniversariantes_{data_input_value.replace("-", "_")}.pdf"'
        
        return response
        
    except ImportError:
        logger.error("WeasyPrint não está instalado. Execute: pip install weasyprint")
        return HttpResponse("Erro: Biblioteca WeasyPrint não está instalada. Execute: pip install weasyprint", status=500)
    except Exception as e:
        logger.error(f"Erro ao gerar PDF de aniversariantes: {e}", exc_info=True)
        return HttpResponse(f"Erro ao gerar PDF: {str(e)}", status=500)


@login_required
@admin_required
def relatorio_escala_mensal_missas_pdf(request):
    """
    Gera PDF do Relatório de Escala Mensal de Missas
    Aplica os mesmos filtros da view principal
    """
    try:
        from weasyprint import HTML
        from django.template.loader import render_to_string
        from io import BytesIO
        
        # Buscar paróquia
        paroquia = TBPAROQUIA.objects.first()
        
        # Buscar dados (mesma lógica da view principal com filtros)
        itens_escala = []
        mes_str = request.GET.get('mes', '').strip()
        ano_str = request.GET.get('ano', '').strip()
        colaborador_id = request.GET.get('colaborador', '').strip()
        funcao_id = request.GET.get('funcao', '').strip()
        status = request.GET.get('status', '').strip()
        grupo_id = request.GET.get('grupo', '').strip()
        situacao = request.GET.get('situacao', '').strip()
        
        if mes_str and ano_str:
            try:
                mes = int(mes_str)
                ano = int(ano_str)
                
                if 1 <= mes <= 12 and 2000 <= ano <= 2100:
                    primeiro_dia_mes = date(ano, mes, 1)
                    escala_master = TBESCALA.objects.filter(ESC_MESANO=primeiro_dia_mes).first()
                    
                    if escala_master:
                        # Buscar itens da escala com filtros
                        itens = TBITEM_ESCALA.objects.filter(
                            ITE_ESC_ESCALA=escala_master
                        )
                        
                        # Aplicar filtros
                        if colaborador_id:
                            try:
                                colaborador_id_int = int(colaborador_id)
                                itens = itens.filter(ITE_ESC_COLABORADOR=colaborador_id_int)
                            except (ValueError, TypeError):
                                pass
                        
                        if funcao_id:
                            try:
                                funcao_id_int = int(funcao_id)
                                itens = itens.filter(ITE_ESC_FUNCAO=funcao_id_int)
                            except (ValueError, TypeError):
                                pass
                        
                        if status:
                            itens = itens.filter(ITE_ESC_STATUS=status)
                        
                        if grupo_id:
                            try:
                                grupo_id_int = int(grupo_id)
                                itens = itens.filter(ITE_ESC_GRUPO=grupo_id_int)
                            except (ValueError, TypeError):
                                pass
                        
                        if situacao:
                            if situacao == 'true':
                                itens = itens.filter(ITE_ESC_SITUACAO=True)
                            elif situacao == 'false':
                                itens = itens.filter(ITE_ESC_SITUACAO=False)
                        
                        itens = itens.order_by('ITE_ESC_DATA', 'ITE_ESC_HORARIO')
                        
                        dias_semana_pt = {
                            0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira',
                            3: 'Quinta-feira', 4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo'
                        }
                        
                        meses_pt = [
                            '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
                        ]
                        
                        for item in itens:
                            item.dia_semana_nome = dias_semana_pt.get(item.ITE_ESC_DATA.weekday(), '')
                            
                            if item.ITE_ESC_COLABORADOR:
                                try:
                                    colaborador = TBCOLABORADORES.objects.get(COL_id=item.ITE_ESC_COLABORADOR)
                                    item.colaborador_nome = colaborador.COL_nome_completo
                                except TBCOLABORADORES.DoesNotExist:
                                    item.colaborador_nome = '-'
                            else:
                                item.colaborador_nome = '-'
                            
                            # Buscar nome da função
                            if item.ITE_ESC_FUNCAO:
                                try:
                                    funcao = TBFUNCAO.objects.get(FUN_id=item.ITE_ESC_FUNCAO)
                                    item.funcao_nome = funcao.FUN_nome_funcao
                                except TBFUNCAO.DoesNotExist:
                                    item.funcao_nome = '-'
                            else:
                                item.funcao_nome = '-'
                            
                            if item.ITE_ESC_GRUPO:
                                try:
                                    grupo = TBGRUPOS.objects.get(GRU_id=item.ITE_ESC_GRUPO)
                                    item.grupo_nome = grupo.GRU_nome_grupo
                                except TBGRUPOS.DoesNotExist:
                                    item.grupo_nome = '-'
                            else:
                                item.grupo_nome = '-'
                        
                        itens_escala = list(itens)
                        
            except (ValueError, TypeError):
                pass
        
        meses_pt = [
            '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        
        mes_nome = ''
        if mes_str and mes_str.isdigit():
            try:
                mes_int = int(mes_str)
                if 1 <= mes_int <= 12:
                    mes_nome = meses_pt[mes_int]
            except:
                pass
        
        context = {
            'paroquia': paroquia,
            'itens_escala': itens_escala,
            'mes': mes_str,
            'ano': ano_str,
            'mes_nome': mes_nome,
            'total_encontrado': len(itens_escala),
            'titulo_relatorio': 'RELATÓRIO DE ESCALA MENSAL DE MISSAS',
        }
        
        # Renderizar template HTML para PDF
        html_string = render_to_string('admin_area/tpl_relatorio_escala_mensal_missas_pdf.html', context)
        
        # Gerar PDF
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf_file = html.write_pdf()
        
        # Criar resposta HTTP
        response = HttpResponse(pdf_file, content_type='application/pdf')
        filename = f"relatorio_escala_mensal_{mes_str}_{ano_str}.pdf" if mes_str and ano_str else "relatorio_escala_mensal.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except ImportError:
        logger.error("WeasyPrint não está instalado. Execute: pip install weasyprint")
        return HttpResponse("Erro: Biblioteca WeasyPrint não está instalada. Execute: pip install weasyprint", status=500)
    except Exception as e:
        logger.error(f"Erro ao gerar PDF de escala mensal: {e}", exc_info=True)
        return HttpResponse(f"Erro ao gerar PDF: {str(e)}", status=500)
