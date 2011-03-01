'''
Created on May 31, 2010

@author: jnaous
'''
import exceptions
from models import ExpedientPermission
from expedient.common.permissions.shortcuts import get_permittee_from_threadlocals

class require_obj_permissions_for_method(object):
    """
    Decorator that checks that one model has permissions to use another.
    
    The decorator requires the following parameters on initialization:
    
    @param permittee_kw: the keyword used to store the permittee object in threadlocals.
    @type permittee_kw: C{str}
    @param perm_names: a list of permission names that are required.
    @type perm_names: C{list} of C{str}
    
    For example::
    
        class TestModel(models.Model):
            @require_obj_permissions_for_method(
                "user", ["can_call_methods", "can_call_test"])
            def test_method(self, paramA, paramB):
                pass
        
    """
    
    def __init__(self, permittee_kw, perm_names):
        self.perm_names = set(perm_names)
        self.permittee_kw = permittee_kw
    
    def __call__(self, f):
        """
        This method is called on execution of the decorator to get the wrapper
        defined inside.
        """
        def require_obj_permissions_wrapper(obj, *args, **kw):
            """
            Wrapper for the called method that checks the permissions before
            calling the method.
            """
            # check if the permittee exists in the request
            permittee = get_permittee_from_threadlocals(self.permittee_kw)

            missing = ExpedientPermission.objects.get_missing_for_target(
                permittee, self.perm_names, obj)

            if missing:
                raise exceptions.PermissionDenied(missing.name, obj, permittee)
            
            # All is good. Call the function
            return f(obj, *args, **kw)
        
        return require_obj_permissions_wrapper

class require_objs_permissions_for_view(object):
    """
    Decorator to be used on views. The decorator checks that a permittee
    has the permissions listed in C{perm_names} for some targets. The permittee and
    targets are returned respectively by the C{permittee_func} and C{target_func}
    parameters of the decorator. These should be callables that can take
    the parameters of the decorated function. The decorator also accepts an
    optional fourth parameter C{methods} that is a list of method names
    for which the permission applies. C{target_func} must return a QuerySet.
    
    For example::
    
        @require_objs_permissions_for_view(
            ["can_delete_comment"],
            lambda(request, blog_id, comment_id): get_object_or_404(Blog, pk=blog_id),
            lambda(request, blog_id, comment_id): Comment.objects.filter(pk=comment_id),
            ["POST"],
        )
        def delete_blog_comment(request, blog_id, comment_id):
            ...
    
    @param perm_names: a list of permission names that are required.
    @type perm_names: L{list} of L{str}
    @param permittee_func: a callable that accepts the decorated methods arguments
        and returns a model instance not necessarily a L{PermissionUser}
        instance.
    @type permittee_func: callable
    @param target_func: a callable that accepts the decorated methods arguments
        and returns a C{QuerySet} instance of targets.
    @type target_func: callable
    @keyword methods: list of methods for which the requirement applies.
        Default is ["GET", "POST"].
    @type methods: C{list} of C{str}
    """
    
    def __init__(self, perm_names, permittee_func, target_func,
                 methods=["GET", "POST"]):
        self.perm_names = set(perm_names)
        self.permittee_func = permittee_func
        self.target_func = target_func
        self.methods = methods
        
    def __call__(self, f):
        from middleware import PermissionMiddleware
        PermissionMiddleware.add_required_view_permissions(
            f, self.perm_names, self.permittee_func, self.target_func, self.methods,
        )
        return f
