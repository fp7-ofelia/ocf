'''
Created on Jun 6, 2010

@author: jnaous
'''
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from expedient.common.permissions.exceptions import PermissionDenied
from expedient.common.permissions.models import ExpedientPermission
from expedient.common.permissions.utils import get_object_from_ids
from django.core.urlresolvers import get_callable

def reraise_permission_denied(request, perm_name=None,
                              target_ct_id=None, target_id=None,
                              user_ct_id=None, user_id=None):
    """
    Raises a PermissionDenied exception for the given parameters.
    """
    target_obj_or_class = get_object_from_ids(target_ct_id, target_id)
    user = get_object_from_ids(user_ct_id, user_id)
    raise PermissionDenied(perm_name, target_obj_or_class, user, False)

def redirect_permissions_request(request, perm_name=None,
                                 target_ct_id=None, target_id=None,
                                 user_ct_id=None, user_id=None):
    """
    Gets the target and user objects and passes them along with the 
    L{ExpedientPermission} object named by C{perm_name} to the view that's
    used by the permission.
    """
    permission = get_object_or_404(ExpedientPermission, name=perm_name)
    target_obj_or_class = get_object_from_ids(target_ct_id, target_id)
    user = get_object_from_ids(user_ct_id, user_id)
    if not permission.view:
        raise PermissionDenied(perm_name, target_obj_or_class, user, False)
    
    view = get_callable(permission.view)
    
    # no urls allowed in redirection.
    redirect_to = request.GET.get("next", '')
    if not redirect_to or ' ' in redirect_to or "//" in redirect_to:
        redirect_to = None
    
    return view(request, permission, user, target_obj_or_class,
                redirect_to=redirect_to)
