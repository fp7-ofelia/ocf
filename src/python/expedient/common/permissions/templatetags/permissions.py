'''
Created on Aug 3, 2010

@author: jnaous
'''
from expedient.common.permissions.models import Permittee
from django.contrib.contenttypes.models import ContentType
from django import template

register = template.Library()

@register.filter
def has_obj_perm(obj_or_class, perm_name):
    """
    Return a queryset of all permittees that own the permission with name
    C{perm_name} for target C{obj_or_class}.
    """
    return Permittee.objects.filter_for_permission_name(
        perm_name, obj_or_class)

@register.filter
def as_class(permittee_qs, klass):
    """Get the permittee queryset as a queryset of model class C{klass}.
    
    Only those objects whose class is C{klass} are returned.
    
    @param permittee_qs: Permitte queryset to filter.
    @param klass: C{class} or C{ContentType} to filter for.
    """
    
    if not isinstance(klass, ContentType):
        klass = ContentType.objects.get_for_model(klass)

    ids = permittee_qs.filter(
        object_type=klass).values_list("object_id", flat=True)
        
    return klass.model_class().objects.filter(pk__in=ids)
