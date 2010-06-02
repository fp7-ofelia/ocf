'''
Created on Jun 1, 2010

@author: jnaous
'''
from expedient.common.permissions.models import ControlledContentType,\
    ExpedientPermission, PermissionInfo
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from expedient.common.permissions.exceptions import PermissionCannotBeDelegated,\
    PermissionRegistrationConflict
from django.contrib.auth.models import User

def register_controlled_type(
                             model, can_change_url=None,
                             can_view_url=None, can_delete_url=None):
    """
    Creates a ControlledContentType object for the model with default
    permission names: <module>.<modelname>.can_change/can_view/can_delete.
    
    @param model: the model whose class we wish to control.
    @type model: L{class}
    @keyword can_change_url: url name for the can_change permission
    @keyword can_view_url: url name for the can_view permission
    @keyword can_delete_url: url name for the can_delete permission
    """
    
    ct = ContentType.objects.get_for_model(model)
    
    try:
        ControlledContentType.objects.create(content_type=ct)
        register_permission(
            "%s.%s.can_change" % (model.__module__, model.__name__),
            can_change_url)
        register_permission(
            "%s.%s.can_view" % (model.__module__, model.__name__),
            can_view_url)
        register_permission(
            "%s.%s.can_delete" % (model.__module__, model.__name__),
            can_delete_url)
    except IntegrityError:
        pass
        
def register_permission(name, url_name=None):
    """
    Create a new permission.
    
    @param name: The name of the permission. Must be globally unique.
    @type name: L{str}
    @keyword url_name: The name of the URL to redirect to if a permission is missing. Default None.
    @type url_name: L{str}
    """
    
    # check if the permission is registered with a different url somewhere else
    try:
        perm = ExpedientPermission.objects.get(name=name)
    except ExpedientPermission.DoesNotExist:
        ExpedientPermission.objects.create(name=name, url_name=url_name)
    else:
        if perm.url_name != url_name:
            raise PermissionRegistrationConflict(name, url_name, perm.url_name)
    
def give_permission_to(giver, receiver, perm_name, delegatable=False):
    """
    Gives permission to a permission user instance.
    
    @param giver: The permission user model giving the permission.
    @type giver: L{expedient.common.permissions.models.PermissionUserModel} or
        L{django.contrib.auth.models.User}.
    @param receiver: The permission user model receiving the permission.
    @type receiver: L{expedient.common.permissions.models.PermissionUserModel}
    @param perm_name: The permission's name
    @type perm_name: L{str}
    @keyword delegatable: Can the receiver in turn give the permission out?
        Default is False.
    @type delegatable: L{bool}
    """
    
    # Check the giver's permissions
    if type(giver) != User or not giver.is_superuser:
        try:
            perm_info = giver.permissioninfo_set.all().get(
                permission__name=perm_name, can_delegate=True)
        except PermissionInfo.DoesNotExist:
            raise PermissionCannotBeDelegated(giver, perm_name)

    PermissionInfo.objects.create(
        permission=perm_info.permission,
        perm_user=receiver,
        can_delegate=delegatable,
    )
