'''
Created on May 31, 2010

@author: jnaous
'''
from exceptions import PermissionDenied, PermissionSignatureError
from models import ExpedientPermission
from django.contrib.contenttypes.models import ContentType

class require_obj_permissions(object):
    """
    Decorator that checks that one model has permissions to use another.
    This should be used on object methods.
    
    The decorator requires the following parameters on initialization:
    
    @param user_kw: the keyword used to pass the user object.
    @type user_kw: L{str}
    @param perm_names: a list of permission names that are required.
    @type perm_names: L{list} of L{str}
    @keyword pop_user_kw: Should the C{user_kw} keyword be removed from the
        keyword arguments or left in when calling the decorated method? Default
        is True. Useful in case the decorated function uses the same keyword.
    @type pop_user_kw: L{bool}
    
    For example::
    
        class TestModel(models.Model):
            @require_obj_permissions("user", ["can_call_methods", "can_call_test"])
            def test_method(self, paramA, paramB):
                pass
            
    Then to call test_method::
    
        >>> t = TestModel()
        >>> t.test_method(paramA, paramB, user=some_user_object)
        
    """
    
    def __init__(self, user_kw, perm_names, pop_user_kw=True):
        self.perm_names = set(perm_names)
        self.user_kw = user_kw
        self.pop_user_kw = pop_user_kw
    
    def __call__(self, f, prewrapper_func=None):
        """
        This method is called on execution of the decorator to get the wrapper
        defined inside. The C{prewrapper_func} keyword argument is available for
        subclasses. If defined, the output of the prewrapper function is
        returned instead of the wrapper function. The prewrapper function 
        should have one argument: C{wrapper} which is the original function
        that would have been returned.
        """
        def require_obj_permissions_wrapper(obj, *args, **kw):
            """
            Wrapper for the called method that checks the permissions before
            calling the method.
            """
            # check for the permission
            try:
                if self.pop_user_kw:
                    user = kw.pop(self.user_kw)
                else:
                    user = kw[self.user_kw]
            except KeyError:
                raise PermissionSignatureError(self.user_kw)

            missing, temp = ExpedientPermission.objects.get_missing_for_target(
                user, self.perm_names, obj)

            if missing:
                raise PermissionDenied(missing.name, obj, user)
            
            # All is good. Call the function
            return f(obj, *args, **kw)
        
        # call the prewrapper if it is defined
        if prewrapper_func:
            return prewrapper_func(require_obj_permissions_wrapper)
        else:
            return require_obj_permissions_wrapper

class require_obj_permissions_for_user(require_obj_permissions):
    """
    Wrapper around require_obj_permissions that sets the C{user_kw} parameter
    to "user"
    """
    
    def __init__(self, perm_names, pop_user_kw=True):
        super(require_obj_permissions_for_user, self).__init__(
            "user", perm_names, pop_user_kw)

class require_objs_permissions_for_view(object):
    """
    Decorator to be used on views. The decorator checks that a permission user
    has the permissions listed in C{perm_names} for some targets. The user and
    targets are returned respectively by the C{user_func} and C{target_func}
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
    @param user_func: a callable that accepts the decorated methods arguments
        and returns a model instance not necessarily a L{PermissionUser}
        instance.
    @type user_func: callable
    @param target_func: a callable that accepts the decorated methods arguments
        and returns a C{QuerySet} instance of targets.
    @type target_func: callable
    @keyword methods: list of methods for which the requirement applies.
        Default is ["GET", "POST"].
    @type methods: C{list} of C{str}
    """
    
    def __init__(self, perm_names, user_func, target_func,
                 methods=["GET", "POST"]):
        self.perm_names = set(perm_names)
        self.user_func = user_func
        self.target_func = target_func
        self.methods = methods
        
    def __call__(self, f):
        from middleware import PermissionMiddleware
        PermissionMiddleware.add_required_view_permissions(
            f, self.perm_names, self.user_func, self.target_func, self.methods,
        )
        return f
