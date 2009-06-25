from django import template

register = template.Library()

@register.filter
def is_in_set(value, arg):
    '''returns "yes" if the value is in QuerySet arg else "no"'''
    
    if arg.filter(pk=value.pk).count(): return "checked"
    else: return ""

@register.filter
def contains(value, arg):
    '''returns result of arg in value'''
    
    return arg in value
