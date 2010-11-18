'''
Created on Jul 30, 2010

@author: jnaous
'''
import logging
from expedient.common.permissions.models import ExpedientPermission,\
    ObjectPermission, PermissionOwnership
from expedient.common.middleware import threadlocals
from expedient.common.permissions.exceptions import PermitteeNotInThreadLocals,\
    PermissionDenied, NonePermitteeException
from expedient.common.permissions.middleware import PermissionMiddleware

logger = logging.getLogger("permissions.shortcuts")

def get_permittee_from_threadlocals(kw):
    """
    Wrapper to get a permittee keyword from threadlocals and make sure it is
    usable. 
    """
    # Just skip if perm checks are disabled
    if not ExpedientPermission.objects.are_checks_enabled():
        return None
    
    d = threadlocals.get_thread_locals()
    logger.debug("Got threadlocals %s" % d)
    try:
        permittee = d[kw]
    except KeyError:
        raise PermitteeNotInThreadLocals(kw)
    if not permittee:
        raise NonePermitteeException(kw)
    
    return permittee
    
    
def has_permission(permittee, target_obj_or_class, perm_name):
    """
    Does the object C{permittee} have the permission named by C{perm_name}
    over target object or class C{target_obj_or_class}.
    
    @param permittee: object that should own the permission or the keyword
        argument for that object that was stored in the threadlocals
        middleware.
    @type permittee: L{Permittee} or C{Model} instance.
    @param target_obj_or_class: The object or class for whose the permission
        is being checked.
    @type target_obj_or_class: C{Model} instance or C{class}.
    @param perm_name: The name of the permission
    @type perm_name: C{str}.
    @return: Whether or not the permittee has the permission
    @rtype: C{bool}
    """
    if isinstance(permittee, str):
        permittee = get_permittee_from_threadlocals(permittee)
        
    return ExpedientPermission.objects.get_missing_for_target(
        permittee, [perm_name], target_obj_or_class) == None


def must_have_permission(permittee, target_obj_or_class, perm_name, allow_redirect=True):
    """
    Does the object C{permittee} have the permission named by C{perm_name}
    over target object or class C{target_obj_or_class}. If not, then raise
    a PermissionDenied exception.
    
    @param permittee: object that should own the permission or the keyword
        argument for that object that was stored in the threadlocals
        middleware.
    @type permittee: L{Permittee} or C{Model} instance.
    @param target_obj_or_class: The object or class for whose the permission
        is being checked.
    @type target_obj_or_class: C{Model} instance or C{class}.
    @param perm_name: The name of the permission
    @type perm_name: C{str}.
    @keyword allow_redirect: Should the user be redirected if the permission
        is denied to the permission's redirection URL? Default True
    @type allow_redirect: C{bool}
    @return: Whether or not the permittee has the permission
    @rtype: C{bool}
    """
    if isinstance(permittee, str):
        permittee = get_permittee_from_threadlocals(permittee)
        
    if not has_permission(permittee, target_obj_or_class, perm_name):
        raise PermissionDenied(
            perm_name, target_obj_or_class,
            permittee, allow_redirect=allow_redirect)

def create_permission(perm_name, description="", view=None, force=True):
    """
    Shortcut to create a new permission. See
    L{ExpedientPermissionManager.create_permission}.
    """
    return ExpedientPermission.objects.create_permission(
        perm_name, description=description, view=view, force=force)
    
    
def give_permission_to(permission, obj_or_class, receiver, giver=None, can_delegate=False):
    """
    Give receiver the permission C{permission} over the object or class
    C{obj_or_class}. If C{giver} is specified, then the function checks that
    the giver is allowed to give the permission to the receiver. If
    C{can_delegate} is C{True}, the receiver is given the ability to further
    give the permission to others.
    
    @param permission: The name of the permission to give to C{reciever} or
        the L{ExpedientPermission} instance.
    @type permission: C{str} or L{ExpedientPermission}.
    @param obj_or_class: The object or class for which the permission is given.
    @type obj_or_class: C{Model} instance or C{class}.
    @param receiver: The permittee receiving the permission. If not a
        L{Permittee} instance, one will be created if not found.
    @type receiver: L{Permittee} or C{Model} instance.
    @keyword giver: The permission owner giving the permission. If not a
        L{Permittee} instance, one will be created (if not found).
        defaults to C{None}.
    @type giver: L{Permittee} or C{Model} instance.
    @keyword can_delegate: Can the receiver in turn give the permission
        out? Default is False.
    @type can_delegate: L{bool}
    @return: The new C{PermissionOwnership} instance.
    """
    
    obj_permission =\
        ObjectPermission.objects.get_or_create_for_object_or_class(
            permission, obj_or_class)[0]
        
    return obj_permission.give_to(
        receiver, giver=giver, can_delegate=can_delegate)
    

def delete_permission(permission, obj_or_class, owner):
    """Take permission away from an owner.
    
    Remove the permission C{permission} to use object or class
    C{obj_or_class} from the owner C{owner}. If the owner doesn't
    have the permission to begin with, nothing happens.
    
    @param permission: The name of the permission to remove or its
        L{ExpedientPermission} instance.
    @type permission: C{str} or L{ExpedientPermission}.
    @param obj_or_class: The object or class for which the permission
        is being removed
    @type obj_or_class: C{Model} instance or C{class}.
    @param owner: The permittee currently owning the permission.
    @type owner: L{Permittee} or C{Model} instance.
    """
    PermissionOwnership.objects.delete_ownership(
        permission, obj_or_class, owner)
    
def require_objs_permissions_for_url(url, perm_names, permittee_func,
                                     target_func, methods=["GET", "POST"]):
    """
    Convenience wrapper around L{PermissionMiddleware}.
    """
    PermissionMiddleware.add_required_url_permissions(
        url, perm_names, permittee_func, target_func, methods)
