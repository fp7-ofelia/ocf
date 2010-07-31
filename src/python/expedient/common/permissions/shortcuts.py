'''
Created on Jul 30, 2010

@author: jnaous
'''
from expedient.common.permissions.models import ExpedientPermission,\
    ObjectPermission

def has_permission(permittee, target_obj_or_class, perm_name):
    """
    Does the object C{permittee} have the permission named by C{perm_name}
    over target object or class C{target_obj_or_class}.
    
    @param permittee: object that should own the permission.
    @type permittee: L{Permittee} or C{Model} instance.
    @param target_obj_or_class: The object or class for whose the permission
        is being checked.
    @type target_obj_or_class: C{Model} instance or C{class}.
    @param perm_name: The name of the permission
    @type permission: C{str}.
    @return: Whether or not the permittee has the permission
    @rtype: C{bool}
    """
    return ExpedientPermission.objects.get_missing_for_target(
        permittee, [perm_name], target_obj_or_class) == None

def create_permission(perm_name, description="", view=None):
    """
    Shortcut to create a new permission. See
    L{ExpedientPermissionManager.create_permission}.
    """
    return ExpedientPermission.objects.create_permission(
        perm_name, description=description, view=view)
    
    
def give_permission_to(permission, obj_or_class, receiver, giver=None, can_delegate=False):
    """
    Give reciever the permission name by C{perm_name} over the object or class
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
        ObjectPermission.objects.get_for_object_or_class(
            permission, obj_or_class)
        
    return obj_permission.give_to(
        receiver, giver=giver, can_delegate=can_delegate)
    
