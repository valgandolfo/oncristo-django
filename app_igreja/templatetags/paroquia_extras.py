from django import template

register = template.Library()

@register.filter
def get_horario_dia(paroquia, dia):
    """Retorna os horários de um dia específico da paróquia"""
    horarios = paroquia.get_horarios_fixos()
    return horarios.get(dia, [])

@register.filter
def format_horarios(horarios_list):
    """Formata uma lista de horários para exibição"""
    if not horarios_list:
        return "Não definido"
    return ", ".join(horarios_list)

@register.filter
def add_class(field, css_class):
    """Adiciona uma classe CSS a um campo de formulário"""
    return field.as_widget(attrs={'class': css_class})
