"""
Função auxiliar para preservar filtros GET ao redirecionar após salvar/excluir
"""
from django.urls import reverse


def reconstruir_url_com_filtros(request, nome_view, filtros_list):
    """
    Reconstrói URL com filtros preservados do POST (campos hidden).
    
    Args:
        request: HttpRequest do Django
        nome_view: Nome da view para reverse (ex: 'app_igreja:listar_dizimistas')
        filtros_list: Lista de nomes dos parâmetros de filtro (ex: ['q', 'status', 'page'])
    
    Returns:
        URL completa com query string ou URL simples se não houver filtros
    """
    params = []
    for filtro in filtros_list:
        valor = request.POST.get(filtro, '')
        if valor:  # Só adiciona se tiver valor
            params.append(f"{filtro}={valor}")
    
    query_string = '&'.join(params)
    if query_string:
        return f"{reverse(nome_view)}?{query_string}"
    return reverse(nome_view)

