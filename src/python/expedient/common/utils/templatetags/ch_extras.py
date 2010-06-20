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
def contains(value, arg):
    '''returns result of arg in value'''
    
    return arg in value

@register.filter
def get_meta_field(object, fieldname):
    '''return getattr(object._meta, fieldname)'''
    
    return getattr(object._meta, fieldname)

@register.filter
def get_verbose_name(object):
    '''return object's class's verbose name'''
    
    return getattr(object._meta, "verbose_name")

@register.filter
def get_class_field(object, fieldname):
    '''return getattr(object.__class__, fieldname)'''
    
    return getattr(object.__class__, fieldname)

@register.filter
def equals(object1, object2):
    return object1 == object2

@register.filter
def leaf_class_is(obj, klass):
    return obj.content_type.model_class() == type(klass)
