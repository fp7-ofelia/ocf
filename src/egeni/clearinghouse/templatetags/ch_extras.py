from django import template

register = template.Library()

@register.filter
def check_in_set(value, arg):
    '''returns "checked" if the value is in QuerySet arg else ""'''
    
    if arg.filter(pk=value.pk).count():
        return "checked"
    else:
        return ""

@register.filter
def is_in_set(value, arg):
    '''returns "True" if the value is in QuerySet arg else "False"'''
    
    if arg.filter(pk=value.pk).count():
        return True
    else:
        return False

@register.filter
def contains(value, arg):
    '''returns result of arg in value'''
    
    return arg in value
