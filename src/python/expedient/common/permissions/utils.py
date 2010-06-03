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

DEFAULT_CONTROLLED_TYPE_PERMISSIONS = ["can_add", "can_view", "can_delete"]

def register_controlled_type(
                             model, can_add_url=None,
                             can_view_url=None, can_delete_url=None):
    """
    Creates a ControlledContentType object for the model with default
    permission names: <module>.<modelname>.can_add/can_view/can_delete.
    
    @param model: the model whose class we wish to control.
    @type model: L{class}
    @keyword can_add_url: url name for the can_add permission
    @keyword can_view_url: url name for the can_view permission
    @keyword can_delete_url: url name for the can_delete permission
    """
    
    ct = ContentType.objects.get_for_model(model)
    
    try:
        ControlledContentType.objects.create(content_type=ct)
        register_permission(
            "%s.%s.can_add" % (model.__module__, model.__name__),
            can_add_url)
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

def get_user_from_req(request, *args, **kwargs):
    '''
    Get the user profile from the request. This function is helpful when
    using the require_*_permission_for_view decorators.

    For example::
    
        @require_obj_permission_for_view(
            ["can_view_obj_detail"],
            get_user_from_req,
            get_object_from_filter_func(Obj, 1),
            ["GET"],
        )
        def view_obj_detail(request, obj_id):
            ...
    '''
    return request.user

def get_object_from_filter_func(klass, index, filter="pk"):
    """
    Returns a function that can be used for the require_*_permission_for_view
    decorators to get an object from some argument.
    
    The returned function has a signature (*args, **kwargs) and mainly does
    the following::
    
        klass.objects.get(**{filter: arg})
        
    where C{arg} is obtained from the arguments. If C{index} is an
    C{int}, C{arg} is assumed to be positional. Otherwise, it is assumed to be
    a keyword.
    
    For example::
    
        @require_obj_permission_for_view(
            ["can_view_obj_detail"],
            get_user_from_req,
            get_object_from_filter_func(Obj, 1),
            ["GET"],
        )
        def view_obj_detail(request, obj_id):
            ...
    
    @param klass: The class of the object to be returned.
    @type klass: class
    @param index: location of the id in the arguments when the arguments are
        given as (*args, **kwargs).
    @type index: C{int} for positional, hashable for keyword.
    @keyword filter: a filter to be used for obtaining the object.
    @type filter: C{str}
    
    @return: A callable that returns an object from (*args, **kwargs)
    """
    
    