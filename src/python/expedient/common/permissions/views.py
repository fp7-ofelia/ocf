'''
Created on Jun 6, 2010

@author: jnaous
'''
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from expedient.common.permissions.exceptions import PermissionDenied

def reraise_permission_denied(request, perm_name=None,
                              target_ct_id=None, target_id=None,
                              user_ct_id=None, user_id=None):
    """
    Raises a PermissionDenied exception for the given parameters.
    """
    target_ct = get_object_or_404(ContentType, id=target_ct_id)
    target = get_object_or_404(target_ct.model_class, id=target_id)
    user_ct = get_object_or_404(ContentType, id=user_ct_id)
    user = get_object_or_404(user_ct.model_class, id=user_id)
    raise PermissionDenied(perm_name, target, user, None)

def reraise_class_permission_denied(request, perm_name=None,
                                    target_id=None,
                                    user_ct_id=None, user_id=None):
    """
    Wrapper around L{reraise_permission_denied} to provide the ContentType's
    ContentType instance's id.
    """
    target_ct = get_object_or_404(ContentType, id=target_ct_id)
    return reraise_permission_denied(request, perm_name, target_ct.id,
                                     target_id, user_ct_id, user_id)
