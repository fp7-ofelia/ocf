'''
Created on Jun 1, 2010

@author: jnaous
'''
from django.db import models
from expedient.common.permissions.models import \
    ExpedientPermission, PermissionInfo, ObjectPermission, PermissionUser
from django.contrib.contenttypes.models import ContentType
from expedient.common.permissions.exceptions import PermissionCannotBeDelegated,\
    PermissionRegistrationConflict, PermissionDoesNotExist
from django.http import Http404
from expedient.common.permissions.middleware import PermissionMiddleware

def _stringify_func(f):
    if callable(f):
        return "%s.%s" % (f.__module__, f.__name__)
    else:
        return f

def register_permission_for_obj_or_class(obj_or_class, permission):
    """
    Add L{ObjectPermission}s for a model.
    
    @param obj_or_class: the object instance or class which we wish to add 
        the permission for.
    @param permission: the permission's name or the L{ExpedientPermission} instance
    """
    
    if not isinstance(obj_or_class, models.Model):
        # assume it's a model class, so get the contenttype for it.
        obj_or_class = ContentType.objects.get_for_model(obj_or_class)
        
    if not isinstance(permission, ExpedientPermission):
        try:
            permission = ExpedientPermission.objects.get(name=permission)
        except ExpedientPermission.DoesNotExist:
            raise PermissionDoesNotExist(permission)

    return ObjectPermission.objects.get_or_create_from_instance(
        obj_or_class,
        permission=permission,
    )

def create_permission(name, view=None):
    """
    Create a new L{ExpedientPermission}.
    
    @param name: The name of the permission. Must be globally unique.
    @type name: L{str}
    @keyword view: View to redirect to if a permission is missing. Default None.
        The view function should have the signature::
            
            view(request, permission, user, target_obj_or_class, redirect_to=None)
        
        where C{permission} is an L{ExpedientPermission} instance, C{user} is
        the user object (not necessarily a C{django.contrib.auth.models.User}
        instance), and C{target_obj_or_class} is the object instance or class
        that the user does not have the permission C{permission} for.
        C{redirect_to} is a field used to indicate the original URL that caused
        the L{PermissionDenied} exception. The view should redirect there
        when done.
        
    @type view: Full import path of the view as L{str} or the view function
        object itself. Note that the view must be importable by its a path
        (i.e. cannot use nested functions).
        
    @return: the new L{ExpedientPermission}.
    """
    view = _stringify_func(view)
    # check if the permission is registered with a different view somewhere else
    perm, created = ExpedientPermission.objects.get_or_create(
        name=name, defaults=dict(view=view))
    if not created and perm.view != view:
        raise PermissionRegistrationConflict(name, view, perm.view)
    
    return perm

def give_permission_to(receiver, permission, obj_or_class,
                       giver=None, delegatable=False):
    """
    Gives permission over object or class to a permission user instance.
    
    @param receiver: The permission user receiving the permission.
    @type receiver: object registered as permission user or L{PermissionUser}
    @param permission: The permission's name or the permission object
    @type permission: L{str} or L{ExpedientPermission} instance
    @param obj_or_class: The object or the class to give permission to.
    @type obj_or_class: model instance or class
    @keyword giver: The permission user giving the permission.
    @type giver: object registered as permission user or L{PermissionUser}
    @keyword delegatable: Can the receiver in turn give the permission out?
        Default is False.
    @type delegatable: L{bool}
    """
    
    if not isinstance(obj_or_class, models.Model):
        # assume it's a model class, so get the contenttype for it.
        obj_or_class = ContentType.objects.get_for_model(obj_or_class)
    
    if not isinstance(receiver, PermissionUser):
        receiver, created = PermissionUser.objects.get_or_create_from_instance(
            receiver,
        )
        
    if not isinstance(permission, ExpedientPermission):
        try:
            permission = ExpedientPermission.objects.get(name=permission)
        except ExpedientPermission.DoesNotExist:
            raise PermissionDoesNotExist(permission)

    # Is someone delegating the permission?
    if giver:
        # Is the giver a PermissionUser already?
        if not isinstance(giver, PermissionUser):
            giver, created = PermissionUser.objects.get_or_create_from_instance(
                giver,
            )
            # Just created the PermissionUser, so giver cannot have the
            # permission to delegate
            if created:
                raise PermissionCannotBeDelegated(giver, permission.name)
        
        # Check the giver's permissions
        try:
            perm_info = giver.permissioninfo_set.all().get(
                obj_permission__permission=permission,
                obj_permission__object_type=ContentType.objects.get_for_model(
                    obj_or_class),
                obj_permission__object_id=obj_or_class.id,
                can_delegate=True,
            )
            obj_perm = perm_info.obj_permission
        except PermissionInfo.DoesNotExist:
            raise PermissionCannotBeDelegated(giver, permission.name)
    else:
        obj_perm, creatd = ObjectPermission.objects.get_or_create_from_instance(
            obj_or_class, permission=permission)
    
    pi, created = PermissionInfo.objects.get_or_create(
        obj_permission=obj_perm,
        user=receiver,
        defaults=dict(can_delegate=delegatable),
    )
    if not created and pi.can_delegate != delegatable:
        pi.can_delegate = delegatable
        pi.save()

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

def get_queryset(klass, index, filter="pk"):
    """
    Returns a function that can be used for the require_*_permission_for_view
    decorators to get a queryset from some argument.
    
    The returned function has a signature (*args, **kwargs) and mainly does
    the following::
    
        klass.objects.filter(**{filter: arg})
        
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
    
    def wrapper(*args, **kwargs):
        if type(index) == int:
            arg = args[index]
        else:
            arg = kwargs[index]
        return klass.objects.filter(**{filter: arg})
    
    return wrapper

def get_queryset_from_class(klass):
    """
    Returns a function usable as the C{target_func} of the
    L{require_objs_permissions_for_view} decorator. The returned function
    returns the C{ContentType} queryset for a class. This can be used to
    enforce class level permissions on views.
     
    @param klass: the model class for which we want the queryset. 
    """
    def target_func(*args, **kwargs):
        ct = ContentType.objects.get_for_model(klass)
        return ContentType.objects.filter(pk=ct.pk)
    return target_func

def get_queryset_from_id(klass, id):
    """
    Returns a function usable as a C{target_func} parameter. The returned
    function returns a C{QuerySet} containing one object with the given C{id}.
    
    @param klass: the class of the queryset's model.
    @param id: the object's id.
    """
    def target_func(*args, **kwargs):
        return klass.objects.filter(id=id)
    return target_func

def get_object_from_ids(ct_id, id):
    """
    Get an object from the ContentType id and from the object's id.
    
    @param ct_id: ContentType's id for the object class.
    @param id: object's id.
    """
    try:
        ct = ContentType.objects.get_for_id(ct_id)
    except ContentType.DoesNotExist:
        raise Http404()
    try:
        return ct.get_object_for_this_type(pk=id)
    except ct.model_class().DoesNotExist:
        raise Http404()

def require_objs_permissions_for_url(url, perm_names, user_func,
                                     target_func, methods=["GET", "POST"]):
    """
    Convenience wrapper around L{PermissionMiddleware}.
    """
    PermissionMiddleware.add_required_url_permissions(
        url, perm_names, user_func, target_func, methods)
