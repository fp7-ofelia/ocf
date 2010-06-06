'''
Created on Jun 1, 2010

@author: jnaous
'''
from django.db import models
from expedient.common.permissions.models import ControlledContentType,\
    ExpedientPermission, PermissionInfo, ObjectPermission, PermissionUser
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from expedient.common.permissions.exceptions import PermissionCannotBeDelegated,\
    PermissionRegistrationConflict
from django.contrib.auth.models import User
from django.conf.urls.defaults import patterns, url

DEFAULT_CONTROLLED_TYPE_PERMISSIONS = ["can_add", "can_view", "can_delete", "can_modify"]
CONTROLLED_TYPE_URL_NAME = "permissions-controlled-type"

def type_permission_url(view_func, model, perm_name):
    """
    Get the url pattern to be used for type permissions.
    """
    ct_ct = ContentType.objects.get_for_model(model)
    model_ct = ContentType.objects.get_for_model(model)
    return url(
        r"^/%s/%d/%d/(?P<usr_id>\d+)/$" % (perm_name, ct_ct.id, model_ct.id),
        view_func,
    )

def register_type_default_permissions():
    """
    Creates default permissions: can_add/can_view/can_delete/can_modify for classes.
    """
    for perm_name in DEFAULT_CONTROLLED_TYPE_PERMISSIONS:
        register_type_permission(perm_name)

def register_type_permission(perm_name):
    """
    Add a new class level permission called C{perm_name}.
    
    @param perm_name: name of the new permission
    @type perm_name: C{str}
    """
    new_url = "%s-%s" % (CONTROLLED_TYPE_URL_NAME, perm_name)
    register_permission(perm_name, new_url)

def register_permission_for_type(model, perm_name):
    """
    Add L{ObjectPermission}s for a model.
    
    @param model: the model which we wish to add the permission for.
    @param perm_name: the permission name.
    """
    
    model_ct = ContentType.objects.get_for_model(model)
    
    ObjectPermission.objects.get_or_create(
        permission=ExpedientPermission.objects.get(name=perm_name),
        target=model_ct,
    )

def register_permission(name, url_name=None):
    """
    Create a new L{ExpedientPermission}.
    
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

def register_permission_for_object(object, perm_name):
    """
    Wrapper around creating a L{ObjectPermission}.
    """
    ObjectPermission.objects.get_or_create(
        permission=ExpedientPermission.objects.get(name=perm_name),
        target=object,
    )

def give_permission_to(giver, receiver, perm_name, obj_or_class, delegatable=False):
    """
    Gives permission over object or class to a permission user instance.
    
    @param giver: The permission user giving the permission.
    @type giver: object registered as permission user or L{PermissionUser}
    @param receiver: The permission user receiving the permission.
    @type receiver: object registered as permission user or L{PermissionUser}
    @param perm_name: The permission's name
    @type perm_name: L{str}
    @param obj_or_class: The object or the class to give permission to.
    @type obj_or_class: model instance or class
    @keyword delegatable: Can the receiver in turn give the permission out?
        Default is False.
    @type delegatable: L{bool}
    """
    
    if not isinstance(obj_or_class, models.Model):
        # assume it's a model class, so get the contenttype for it.
        obj_or_class = ContentType.objects.get_for_model(obj_or_class)
    
    if not isinstance(giver, PermissionUser):
        giver, created = PermissionUser.objects.get_or_create_from_instance(
            giver,
        )
        if created:
            raise PermissionCannotBeDelegated(giver, perm_name)
    
    if not isinstance(receiver, PermissionUser):
        receiver, created = PermissionUser.objects.get_or_create_from_instance(
            receiver,
        )

    # Check the giver's permissions
    try:
        perm_info = giver.permissioninfo_set.all().get(
            obj_permission__permission__name=perm_name,
            obj_permission__object_type=ContentType.objects.get_for_model(
                obj_or_class),
            obj_permission__object_id=obj_or_class.id,
            can_delegate=True,
        )
    except PermissionInfo.DoesNotExist:
        raise PermissionCannotBeDelegated(giver, perm_name)

    PermissionInfo.objects.create(
        obj_permission=perm_info.obj_permission,
        user=receiver,
        can_delegate=delegatable,
    )

def get_user_from_req(request, *args, **kwargs):
    '''
    Get the user profile from the request. This function is helpful when
    using the require_*_permission_for_view decorators.

    For example::
    
        @require_objs_permissions_for_view(
            ["can_view_obj_detail"],
            get_user_from_req,
            get_objects_from_filter_func(Obj, 1),
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
    
    