'''
Created on May 31, 2010

@author: jnaous
'''

class PermissionRegistrationConflict(Exception):
    """
    Raised when a permission is registered with two different views.
    """
    def __init__(self, perm_name, new_view, old_view):
        message = "Permission %s is already registered " % perm_name
        message += "with view name %s. Cannot register " % old_view
        message += "again with view %s." % new_view
        super(PermissionRegistrationConflict, self).__init__(message)

class PermissionDenied(Exception):
    """
    Raised when a permission is denied/not found.
    """
    def __init__(self, perm_name, target, user, allow_redirect=True):
        message = "Permission %s was not found for permission user %s for \
target object %s" % (perm_name, user, target)
        self.perm_name = perm_name
        self.target = target
        self.user = user
        self.allow_redirect = allow_redirect
        super(PermissionDenied, self).__init__(message)

class PermissionSignatureError(Exception):
    """
    Raised when a function decorated with one of the require_* decorators
    does not have the right arguments for the call.
    """
    
    def __init__(self, function, keyword):
        message = "Permission checking for function %s requires the \
missing keyword argument %s.""" % (function.func_name, keyword)
        super(PermissionSignatureError, self).__init__(message)

class PermissionDecoratorUsageError(Exception):
    """
    Raised when the decorators are misused.
    """
    pass

class PermissionDoesNotExist(Exception):
    """
    Raised when a permission with a given name does not exist.
    """
    
    def __init__(self, perm_name, target=None):
        message = "Permission %s has not been created" % perm_name
        if target:
            message += " for target %s." % target
        else:
            message += "."
        super(PermissionDoesNotExist, self).__init__(message)

class PermissionCannotBeDelegated(Exception):
    """
    Raised when a permission user tries to give permission to another when
    the permission cannot be delegated.
    """
    
    def __init__(self, giver, perm_name):
        message = "Giver %s cannot delegate permission %s." % (
            giver, perm_name)
        super(PermissionCannotBeDelegated, self).__init__(message)
