'''
Created on Jun 1, 2010

@author: jnaous
'''
from django.contrib.contenttypes.models import ContentType
from django.http import Http404

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
