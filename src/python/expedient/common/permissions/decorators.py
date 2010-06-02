'''
Created on May 31, 2010

@author: jnaous
'''
from exceptions import PermissionDenied, PermissionSignatureError, \
    PermissionDecoratorUsageError
from django.contrib.auth.models import User
from models import ExpedientPermission, ControlledModel
from django.db import DatabaseError

class require_obj_permissions(object):
    """
    Decorator that checks that one model has permissions to use another.
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
        def wrapper(f, obj, *args, **kw):
            """
            Wrapper for the called method that checks the permissions before
            calling the method.
            """
            # checks if some permission name does not exist
            self.perms_req = ExpedientPermission.objects.get_perms(self.perm_names)

            # check for the permission
            try:
                if self.pop_user_kw:
                    user = kw.pop(self.user_kw)
                else:
                    user = kw[self.user_kw]
            except KeyError:
                raise PermissionSignatureError(self.user_kw)

            # make sure the object is the right type
            if not isinstance(obj, ControlledModel):
                raise PermissionDecoratorUsageError(obj)
            
            missing = user.check_permissions(
                self.perms_req.filter(targets=obj))

            if missing:
                raise PermissionDenied(
                    missing.name, f.func_name, obj, user, missing.url_name)
            
            # All is good. Call the function
            return f(obj, *args, **kw)
        
        # call the prewrapper if it is defined
        if prewrapper_func:
            return prewrapper_func(wrapper)
        else:
            return wrapper

class require_obj_permissions_for_user(require_obj_permissions):
    """
    Decorator that checks that the passed in C{user} keyword argument
    to the decorated method has the named permissions in the required
    permissions list for the object.
    
    This is a subclass of L{require_obj_permissions} that uses C{user}
    as the C{user_kw} parameter for the decorator and allows the C{user}
    value to be either the username or the user object. It also bypasses
    the check if the user is a superuser.
    
    Using this decorator requires that the a user profile model is registered
    for users, and that the user profile model inherits from
    L{models.ControlledModel}.
    
    @param perm_names: a list of permission names that are required.
    @type perm_names: L{list} of L{str}
    @keyword pop_user_kw: Should the C{user} keyword be removed from the
        keyword arguments or left in when calling the decorated method? Default
        is True.
    @type pop_user_kw: L{bool}
    """
    
    def __init__(self, perm_names, pop_user_kw=True):
        super(require_obj_permissions_for_user, self).__init__(
            "user", perm_names, pop_user_kw)
    
    def __call__(self, f):
        def prewrapper(wrapper):
            def new_wrapper(f, obj, *args, **kw):
                try:
                    if self.pop_user_kw:
                        user = kw.pop(self.user_kw)
                    else:
                        user = kw[self.user_kw]
                except KeyError:
                    raise PermissionSignatureError(self.user_kw)
                
                # get the user first, and check is_superuser so we don't have
                # profile does not exist errors for superusers.
                if type(user) == str:
                    user = User.objects.get(username=user)
                
                if user.is_superuser:
                    return f(obj, *args, **kw)
                else:
                    kw[self.user_kw] = user.get_profile()
                    return wrapper(f, obj, *args, **kw)
                
            return new_wrapper
        
        return super(
            require_obj_permissions_for_user, self).__call__(f, prewrapper)
