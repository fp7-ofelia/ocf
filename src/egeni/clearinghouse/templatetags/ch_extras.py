from django import template
from django.utils.safestring import mark_safe

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
def has_interface(value, arg):
    '''returns true if the slice has the interface'''
    return value.has_interface(arg)

@register.filter
def contains(value, arg):
    '''returns result of arg in value'''
    
    return arg in value

@register.filter
def flowspace_tag(flowspace, field):
    '''return a tag from the flowspace for the field'''

    if field.startswith("nw"):
        xml_field = field.replace("nw", "ip")
    else:
        xml_field = field

    try:
        val = flowspace.__getattribute__(field)
    except Exception, e:
        print e
        return mark_safe("")
    
    if val == "*":
        return mark_safe("")
    else:
        return mark_safe("<tns:%s>%s</tns:%s>" % (xml_field, val, xml_field))
