from django import template

register = template.Library()

@register.filter
def get_field_value(obj, field_name):
    """
    Obtém o valor de um campo de um objeto dinamicamente
    """
    try:
        # Tentar acessar o campo diretamente
        if hasattr(obj, field_name):
            value = getattr(obj, field_name)
            # Se for um método, chamar ele
            if callable(value):
                value = value()
            return value
        return "-"
    except:
        return "-"

@register.filter
def get_field_display(obj, field_name):
    """
    Obtém o valor de exibição de um campo (get_XXX_display)
    """
    try:
        if hasattr(obj, field_name):
            # Tentar usar get_XXX_display primeiro
            display_method = f"get_{field_name}_display"
            if hasattr(obj, display_method):
                return getattr(obj, display_method)()
            # Senão, retornar o valor direto
            value = getattr(obj, field_name)
            if callable(value):
                value = value()
            return value
        return "-"
    except:
        return "-"