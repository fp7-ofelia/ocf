'''
Created on Jun 1, 2010

@author: jnaous
'''
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from expedient.common.permissions.shortcuts import must_have_permission,\
    give_permission_to
from expedient.common.middleware import threadlocals
from expedient.common.permissions.models import ObjectPermission

def get_user_from_req(request, *args, **kwargs):
    '''
    Get the user from the request. This function is helpful when
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
            
    @param request: the request object
    @type request: C{HttpRequest}
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
            get_queryset(Obj, 1),
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

def get_leaf_queryset(parent_klass, index, filter="pk"):
    """
    Same as L{get_queryset} but also calls the C{as_leaf_class} function
    on the first element in the queryset and returns a queryset with the
    returned object's class.
    """
    def wrapper(*args, **kwargs):
        if type(index) == int:
            arg = args[index]
        else:
            arg = kwargs[index]
            
        parent_qs = parent_klass.objects.filter(**{filter: arg})
        parents = list(parent_qs)
        if parents:
            ids = [p.id for p in parents]
            return parents[0].as_leaf_class().\
                __class__.objects.filter(id__in=ids)
        return parent_qs
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

def permissions_save_override(permittee_kw, model_func, create_perm, edit_perm, delete_perm):
    """Get a save function that can be used to enforce create, edit, and
    delete permissions.
    
    For example::
    
        class ModelX(models.Model):
            ...
            save = permissions_save_override(
                "user", lambda: ModelX, "can_create", "can_edit", "can_delete")
            
    @param permittee_kw: the keyword used to store the permittee in
        threadlocals
    @type permittee_kw: C{str}.
    @param model_func: A callable that returns the the class.
    @type model_func: C{Model} subclass
    @param create_perm: The name of the creation permission for the class.
    @type create_perm: C{str}
    @param edit_perm: The name of the edit permission for the instance.
    @type edit_perm: C{str}
    @param delete_perm: the name of the delete permission for the instance.
    @type delete_perm: C{str}
    @return: a save function that can be used to enforce permissions.
    @rtype: a callable.
    """
    def save(self, *args, **kwargs):
        """
        Override the default save method to enforce permissions.
        """
        pk = getattr(self, "pk", None)
        if not pk:
            # it's a new instance being created
            must_have_permission(permittee_kw, model_func(), create_perm)
        else:
            must_have_permission(permittee_kw, self, edit_perm)
            
        super(model_func(), self).save(*args, **kwargs)
        
        if not pk:
            # it was just created so give creator edit permissions
            d = threadlocals.get_thread_locals()
            give_permission_to(
                edit_perm, self, d[permittee_kw], can_delegate=True)
            give_permission_to(
                delete_perm, self, d[permittee_kw], can_delegate=True)
    return save

def permissions_delete_override(permittee_kw, model_func, delete_perm):
    """Get a delete function that can be used to enforce
    delete permissions.
    
    For example::
    
        class ModelX(models.Model):
            ...
            delete = permissions_delete_override(
                "user", lambda: ModelX, "can_delete")
            
    @param permittee_kw: the keyword used to store the permittee in
        threadlocals
    @type permittee_kw: C{str}.
    @param model_func: A callable that returns the class.
    @type model_func: C{Model} subclass
    @param delete_perm: the name of the delete permission for the instance.
    @type delete_perm: C{str}
    """
    def delete(self, *args, **kwargs):
        """
        Override the default delete method to enforce permissions.
        """
        must_have_permission(permittee_kw, self, delete_perm)
        # delete all permissions for the object
        ObjectPermission.objects.filter_from_instance(self).delete()
        super(model_func(), self).delete(*args, **kwargs)
    return delete
