from django import template
from django.utils.safestring import mark_safe
from expedient.common.permissions.shortcuts import has_permission
from django.contrib.auth.models import User

register = template.Library()

@register.filter
def is_super_user(user):
    """
    Checks if the given user is superuser.

        @param user User object
        @return boolean True or False depending on permissions for user
    """
    isSuperUser = False
    if (has_permission(user, User, "can_manage_users")):
        return True
    else:
        return False

@register.filter
def cat(obj1, obj2):
    return "%s%s" % (obj1, obj2)

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
    return (obj.leaf_name == type(klass).__name__ 
            and obj.module_name == type(klass).__module__)

