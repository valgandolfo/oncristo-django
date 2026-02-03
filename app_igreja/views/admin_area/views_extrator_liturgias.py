"""
==================== EXTRATOR DE LITURGIAS ====================
View para extrair liturgias do site da Arquidiocese de Joinville
e salvar no banco de dados TBLITURGIA
"""

import requests
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import logging
import re

from ...models.area_admin.models_extrator_liturgias import TBLITURGIA

logger = logging.getLogger(__name__)


def admin_required(view_func):
    """Decorator para verificar se o usuário é admin"""
    from functools import wraps
    
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_superuser:
            messages.error(request, 'Acesso negado. Apenas administradores podem acessar esta área.')
            return redirect('app_igreja:admin_area')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


class ExtratorLiturgiaJoinville:
    """Classe para extrair liturgias do site da Arquidiocese de Joinville"""
    
    BASE_URL = "https://www.arquidiocesejoinville.com.br/liturgia-diaria"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extrair_data_da_url(self, url):
        """Extrai a data da URL (formato: /liturgia-diaria/2025-11-20)"""
        try:
            # Padrão: /liturgia-diaria/2025-11-20
            match = re.search(r'/(\d{4})-(\d{2})-(\d{2})', url)
            if match:
                ano, mes, dia = match.groups()
                return date(int(ano), int(mes), int(dia))
            
            # Se não encontrar, usa data atual
            logger.warning("Não foi possível extrair data da URL, usando data atual")
            return date.today()
        except Exception as e:
            logger.error(f"Erro ao extrair data: {e}")
            return date.today()
    
    def construir_url(self, data_liturgia):
        """Constrói URL para uma data específica"""
        data_str = data_liturgia.strftime('%Y-%m-%d')
        return f"{self.BASE_URL}/{data_str}"
    
    def extrair_liturgia_da_pagina(self, url, data_liturgia):
        """Extrai todas as leituras de uma página"""
        try:
            logger.info(f"Acessando URL: {url}")
            print(f"--- [EXTRATOR] Acessando: {url}") # Debug visual
            
            response = self.session.get(url, timeout=30)
            print(f"--- [EXTRATOR] Status Code: {response.status_code}")
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            print(f"--- [EXTRATOR] HTML lido: {len(response.text)} bytes")
            
            # Estrutura do site da Arquidiocese de Joinville:
            # Usa classes: .primeira, .segunda, .salmo, .evangelho
            # E IDs: #primeira, #segunda, #salmo, #evangelho
            
            liturgias = {}
            
            # Extrair Primeira Leitura (por classe ou ID)
            primeira_leitura = self._extrair_por_classe_id(soup, "primeira", "Primeira Leitura")
            if primeira_leitura:
                print("--- [EXTRATOR] Primeira Leitura ENCONTRADA")
                liturgias['Primeira Leitura'] = primeira_leitura
            else:
                print("--- [EXTRATOR] Primeira Leitura NÃO encontrada")
            
            # Extrair Segunda Leitura (se houver)
            segunda_leitura = self._extrair_por_classe_id(soup, "segunda", "Segunda Leitura")
            if segunda_leitura:
                print("--- [EXTRATOR] Segunda Leitura ENCONTRADA")
                liturgias['Segunda Leitura'] = segunda_leitura
            
            # Extrair Salmo (por classe ou ID)
            salmo = self._extrair_por_classe_id(soup, "salmo", "Salmo", "Responsório")
            if salmo:
                print("--- [EXTRATOR] Salmo ENCONTRADO")
                liturgias['Salmo Responsorial'] = salmo
            
            # Extrair Evangelho (por classe ou ID)
            evangelho = self._extrair_por_classe_id(soup, "evangelho", "Evangelho")
            if evangelho:
                print("--- [EXTRATOR] Evangelho ENCONTRADO")
                liturgias['Evangelho'] = evangelho
            
            print(f"--- [EXTRATOR] Total itens extraídos: {len(liturgias)}")
            return liturgias
            
        except Exception as e:
            logger.error(f"Erro ao extrair liturgia: {e}")
            print(f"--- [EXTRATOR] ERRO: {e}")
            return {}
    
    def _extrair_por_classe_id(self, soup, classe_id, titulo_principal, titulo_alternativo=None):
        """Extrai seção por classe ou ID específico do site"""
        try:
            # Método 1: Buscar por ID (#primeira, #segunda, #salmo, #evangelho)
            elemento_id = soup.find(id=classe_id)
            if elemento_id:
                # Usar separator \n para garantir que titulos fiquem em linhas separadas de parágrafos
                texto_bruto = elemento_id.get_text(separator='\n', strip=True)
                
                # Dividir em linhas
                linhas = texto_bruto.split('\n')
                
                # Lista de títulos para tentar remover
                titulos_remover = [titulo_principal]
                if titulo_alternativo:
                    titulos_remover.append(titulo_alternativo)
                
                # Verificar primeira linha
                if linhas:
                    primeira_linha = linhas[0].strip()
                    # Se primeira linha contém algum dos títulos (case insensitive)
                    if any(t.lower() in primeira_linha.lower() for t in titulos_remover):
                        # E se a linha for relativamente curta (título + ref bíblica geralmente < 100 chars)
                        if len(primeira_linha) < 100:
                            linhas = linhas[1:] # Remove a primeira linha
                
                texto = '\n'.join(linhas).strip()

                if texto and len(texto) > 50:
                    logger.info(f"✅ {titulo_principal} encontrado por ID #{classe_id}")
                    return texto
            
            # Método 2: Buscar por classe (.primeira, .segunda, .salmo, .evangelho)
            elementos_classe = soup.find_all(class_=re.compile(rf'\b{classe_id}\b', re.IGNORECASE))
            if elementos_classe:
                print(f"--- [EXTRATOR] Encontrados {len(elementos_classe)} elementos com classe '{classe_id}'")
            else:
                print(f"--- [EXTRATOR] NENHUM elemento com classe '{classe_id}'")

            for elemento in elementos_classe:
                # Usar separator \n para garantir que titulos fiquem em linhas separadas de parágrafos
                texto_bruto = elemento.get_text(separator='\n', strip=True)
                
                # Dividir em linhas
                linhas = texto_bruto.split('\n')
                
                # Lista de títulos para tentar remover
                titulos_remover = [titulo_principal]
                if titulo_alternativo:
                    titulos_remover.append(titulo_alternativo)
                
                # Verificar primeira linha
                if linhas:
                    primeira_linha = linhas[0].strip()
                    # Se primeira linha contém algum dos títulos (case insensitive)
                    if any(t.lower() in primeira_linha.lower() for t in titulos_remover):
                        # E se a linha for relativamente curta (título + ref bíblica geralmente < 100 chars)
                        if len(primeira_linha) < 100:
                            linhas = linhas[1:] # Remove a primeira linha
                
                texto = '\n'.join(linhas).strip()

                if texto and len(texto) > 50:
                    logger.info(f"✅ {titulo_principal} encontrado por classe .{classe_id}")
                    return texto
            
            # Método 3: Buscar por texto (fallback)
            return self._extrair_secao(soup, titulo_principal, titulo_alternativo)
            
        except Exception as e:
            logger.error(f"Erro ao extrair por classe/ID {classe_id}: {e}")
            return None
    
    def _extrair_secao(self, soup, titulo_principal, titulo_alternativo=None):
        """Extrai uma seção específica da página do site da Arquidiocese de Joinville"""
        try:
            textos_busca = [titulo_principal]
            if titulo_alternativo:
                textos_busca.append(titulo_alternativo)
            
            # Estrutura do site: <strong>Primeira Leitura (1Mc 2,15-29)</strong> seguido do texto
            # Ou: <h3>Primeira Leitura</h3> seguido do texto
            
            for texto_busca in textos_busca:
                # Método 1: Procurar por strong com o título
                strong_elements = soup.find_all('strong', string=re.compile(texto_busca, re.IGNORECASE))
                for strong in strong_elements:
                    # Pegar o próximo elemento que contenha o texto
                    proximo = strong.find_next_sibling()
                    if not proximo:
                        # Se não tem irmão, pegar do pai
                        proximo = strong.parent
                    
                    if proximo:
                        # Pegar todos os parágrafos seguintes até encontrar próximo título
                        texto_completo = []
                        atual = proximo
                        limite = 10  # Limite de elementos para evitar loop
                        
                        while atual and limite > 0:
                            limite -= 1
                            texto_atual = atual.get_text(strip=True)
                            
                            # Parar se encontrar outro título de liturgia
                            if any(titulo in texto_atual for titulo in ['Primeira Leitura', 'Segunda Leitura', 'Salmo', 'Evangelho', 'Responsório']):
                                if texto_busca not in texto_atual:
                                    break
                            
                            if texto_atual and len(texto_atual) > 20 and texto_busca not in texto_atual:
                                texto_completo.append(texto_atual)
                            
                            atual = atual.find_next_sibling()
                        
                        if texto_completo:
                            texto_final = '\n'.join(texto_completo)
                            # Limpar texto (remover referências bíblicas do início)
                            texto_final = re.sub(r'^\([^)]+\)\s*', '', texto_final).strip()
                            if len(texto_final) > 50:
                                return texto_final
                
                # Método 2: Procurar por h3, h4 com o título
                for tag in ['h3', 'h4', 'h5']:
                    headers = soup.find_all(tag, string=re.compile(texto_busca, re.IGNORECASE))
                    for header in headers:
                        texto_completo = []
                        atual = header.find_next_sibling()
                        limite = 10
                        
                        while atual and limite > 0:
                            limite -= 1
                            texto_atual = atual.get_text(strip=True)
                            
                            # Parar se encontrar outro título
                            if any(titulo in texto_atual for titulo in ['Primeira Leitura', 'Segunda Leitura', 'Salmo', 'Evangelho', 'Responsório']):
                                if texto_busca not in texto_atual:
                                    break
                            
                            if texto_atual and len(texto_atual) > 20 and texto_busca not in texto_atual:
                                texto_completo.append(texto_atual)
                            
                            atual = atual.find_next_sibling()
                        
                        if texto_completo:
                            texto_final = '\n'.join(texto_completo)
                            texto_final = re.sub(r'^\([^)]+\)\s*', '', texto_final).strip()
                            if len(texto_final) > 50:
                                return texto_final
                
                # Método 3: Procurar por qualquer texto que contenha o título
                textos_encontrados = soup.find_all(string=re.compile(texto_busca, re.IGNORECASE))
                for texto_encontrado in textos_encontrados:
                    elemento_pai = texto_encontrado.parent
                    if elemento_pai:
                        # Pegar texto do elemento pai e próximos irmãos
                        texto_completo = []
                        atual = elemento_pai
                        limite = 5
                        
                        while atual and limite > 0:
                            limite -= 1
                            texto_atual = atual.get_text(strip=True)
                            
                            # Parar se encontrar outro título
                            if any(titulo in texto_atual for titulo in ['Primeira Leitura', 'Segunda Leitura', 'Salmo', 'Evangelho', 'Responsório']):
                                if texto_busca not in texto_atual:
                                    break
                            
                            if texto_atual and len(texto_atual) > 20 and texto_busca not in texto_atual:
                                texto_completo.append(texto_atual)
                            
                            atual = atual.find_next_sibling()
                        
                        if texto_completo:
                            texto_final = '\n'.join(texto_completo)
                            texto_final = re.sub(r'^\([^)]+\)\s*', '', texto_final).strip()
                            if len(texto_final) > 50:
                                return texto_final
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao extrair seção {titulo_principal}: {e}")
            return None
    
    def salvar_liturgias(self, data_liturgia, liturgias):
        """Salva as liturgias no banco de dados"""
        try:
            print(f"--- [EXTRATOR] Tentando salvar liturgias para {data_liturgia}")
            # Remover liturgias existentes para esta data
            TBLITURGIA.objects.filter(LIT_DATALIT=data_liturgia).delete()
            
            # Salvar cada liturgia
            for tipo, texto in liturgias.items():
                print(f"--- [EXTRATOR] Salvando {tipo} (len={len(texto)})")
                TBLITURGIA.objects.create(
                    LIT_DATALIT=data_liturgia,
                    LIT_TIPOLIT=tipo,
                    LIT_TEXTO=texto,
                    LIT_STATUSLIT=True
                )
            
            logger.info(f"✅ Liturgias salvas para {data_liturgia}")
            print("--- [EXTRATOR] Salvo com SUCESSO!")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar liturgias: {e}")
            print(f"--- [EXTRATOR] ERRO AO SALVAR: {e}")
            return False
    
    def extrair_por_periodo(self, data_inicio, data_fim):
        """Extrai liturgias para um período de datas de forma paralela"""
        import concurrent.futures
        
        print(f"--- [EXTRATOR] Iniciando extração PARALELA período: {data_inicio} até {data_fim}")
        
        resultados = {
            'sucesso': 0,
            'erro': 0,
            'datas': []
        }
        
        # Gerar lista de datas
        datas = []
        curr = data_inicio
        while curr <= data_fim:
            datas.append(curr)
            curr += timedelta(days=1)
            
        # Função auxiliar para processar uma data (worker)
        def processar_data(data_alvo):
            try:
                # Criar nova instância para garantir isolamento na thread
                # Não podemos usar self.session pois requests.Session não é thread-safe para escritas simultâneas
                # (embora leituras sejam ok, o handshake SSL pode dar conflito)
                extrator_thread = ExtratorLiturgiaJoinville()
                
                url = extrator_thread.construir_url(data_alvo)
                liturgias = extrator_thread.extrair_liturgia_da_pagina(url, data_alvo)
                
                if liturgias:
                    return {'data': data_alvo, 'sucesso': True, 'liturgias': liturgias}
                else:
                    return {'data': data_alvo, 'sucesso': False, 'status': 'erro_extrair'}
            except Exception as exc:
                return {'data': data_alvo, 'sucesso': False, 'status': 'erro', 'mensagem': str(exc)}

        # Executar em paralelo (max 5 workers para não sobrecarregar o site destino)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_data = {executor.submit(processar_data, d): d for d in datas}
            
            for future in concurrent.futures.as_completed(future_to_data):
                data = future_to_data[future]
                try:
                    res = future.result()
                    
                    if res['sucesso']:
                        # Salvar na thread principal (aqui) para evitar problemas de Lock no SQLite
                        if self.salvar_liturgias(res['data'], res['liturgias']):
                            resultados['sucesso'] += 1
                            resultados['datas'].append({
                                'data': res['data'],
                                'status': 'sucesso',
                                'leituras': list(res['liturgias'].keys())
                            })
                        else:
                            resultados['erro'] += 1
                            resultados['datas'].append({
                                'data': res['data'],
                                'status': 'erro_salvar'
                            })
                    else:
                        resultados['erro'] += 1
                        resultados['datas'].append(res)
                        
                except Exception as exc:
                    resultados['erro'] += 1
                    resultados['datas'].append({
                        'data': data,
                        'status': 'erro',
                        'mensagem': str(exc)
                    })
        
        return resultados


@login_required
@admin_required
def extrator_liturgias(request):
    """View principal para extrair liturgias"""
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        
        if acao == 'extrair_data':
            # Extrair liturgia de uma data específica
            data_str = request.POST.get('data')
            url = request.POST.get('url', '')
            
            try:
                if url:
                    # Extrair de URL fornecida
                    extrator = ExtratorLiturgiaJoinville()
                    data_liturgia = extrator.extrair_data_da_url(url)
                    liturgias = extrator.extrair_liturgia_da_pagina(url, data_liturgia)
                elif data_str:
                    # Extrair de data fornecida
                    data_liturgia = datetime.strptime(data_str, '%Y-%m-%d').date()
                    extrator = ExtratorLiturgiaJoinville()
                    url = extrator.construir_url(data_liturgia)
                    liturgias = extrator.extrair_liturgia_da_pagina(url, data_liturgia)
                else:
                    messages.error(request, 'Informe uma data ou URL')
                    return redirect('app_igreja:extrator_liturgias')
                
                if liturgias:
                    if extrator.salvar_liturgias(data_liturgia, liturgias):
                        messages.success(request, f'Liturgia de {data_liturgia.strftime("%d/%m/%Y")} extraída e salva com sucesso!')
                    else:
                        messages.error(request, 'Erro ao salvar liturgia no banco de dados')
                else:
                    messages.warning(request, f'Nenhuma liturgia encontrada para {data_liturgia.strftime("%d/%m/%Y")}')
                    
            except Exception as e:
                logger.error(f"Erro ao extrair liturgia: {e}")
                messages.error(request, f'Erro ao extrair liturgia: {str(e)}')
        
        elif acao == 'extrair_periodo':
            # Extrair liturgias de um período
            data_inicio_str = request.POST.get('data_inicio')
            data_fim_str = request.POST.get('data_fim')
            
            try:
                data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
                data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
                
                if data_fim < data_inicio:
                    messages.error(request, 'Data final deve ser maior que data inicial')
                    return redirect('app_igreja:extrator_liturgias')
                
                # Limitar período a 30 dias
                dias = (data_fim - data_inicio).days + 1
                if dias > 30:
                    messages.error(request, 'Período máximo é de 30 dias')
                    return redirect('app_igreja:extrator_liturgias')
                
                extrator = ExtratorLiturgiaJoinville()
                resultados = extrator.extrair_por_periodo(data_inicio, data_fim)
                
                messages.success(
                    request, 
                    f'Extração concluída! Sucesso: {resultados["sucesso"]}, Erros: {resultados["erro"]}'
                )
                
            except Exception as e:
                logger.error(f"Erro ao extrair período: {e}")
                messages.error(request, f'Erro ao extrair período: {str(e)}')
        
        return redirect('app_igreja:extrator_liturgias')
    
    # GET - Mostrar formulário
    context = {
        'hoje': date.today(),
        'ultimas_liturgias': TBLITURGIA.objects.all().order_by('-LIT_DATALIT')[:10]
    }
    
    return render(request, 'admin_area/tpl_extrator_liturgias.html', context)


@login_required
@admin_required
@require_http_methods(["POST"])
def extrator_liturgias_api(request):
    """API para extrair liturgias (retorna JSON)"""
    try:
        import json
        data = json.loads(request.body)
        acao = data.get('acao')
        
        if acao == 'extrair_data':
            data_str = data.get('data')
            url = data.get('url', '')
            
            extrator = ExtratorLiturgiaJoinville()
            
            if url:
                data_liturgia = extrator.extrair_data_da_url(url)
                liturgias = extrator.extrair_liturgia_da_pagina(url, data_liturgia)
            elif data_str:
                data_liturgia = datetime.strptime(data_str, '%Y-%m-%d').date()
                url = extrator.construir_url(data_liturgia)
                liturgias = extrator.extrair_liturgia_da_pagina(url, data_liturgia)
            else:
                return JsonResponse({'success': False, 'message': 'Informe data ou URL'}, status=400)
            
            if liturgias:
                if extrator.salvar_liturgias(data_liturgia, liturgias):
                    return JsonResponse({
                        'success': True,
                        'message': f'Liturgia de {data_liturgia.strftime("%d/%m/%Y")} extraída com sucesso!',
                        'data': data_liturgia.strftime('%Y-%m-%d'),
                        'leituras': list(liturgias.keys())
                    })
                else:
                    return JsonResponse({'success': False, 'message': 'Erro ao salvar no banco'}, status=500)
            else:
                return JsonResponse({'success': False, 'message': 'Nenhuma liturgia encontrada'}, status=404)
        
        elif acao == 'extrair_periodo':
            data_inicio_str = data.get('data_inicio')
            data_fim_str = data.get('data_fim')
            
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            
            if (data_fim - data_inicio).days > 30:
                return JsonResponse({'success': False, 'message': 'Período máximo é 30 dias'}, status=400)
            
            extrator = ExtratorLiturgiaJoinville()
            resultados = extrator.extrair_por_periodo(data_inicio, data_fim)
            
            return JsonResponse({
                'success': True,
                'message': f'Extração concluída! Sucesso: {resultados["sucesso"]}, Erros: {resultados["erro"]}',
                'resultados': resultados
            })
        
        return JsonResponse({'success': False, 'message': 'Ação inválida'}, status=400)
        
    except Exception as e:
        logger.error(f"Erro na API: {e}")
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
