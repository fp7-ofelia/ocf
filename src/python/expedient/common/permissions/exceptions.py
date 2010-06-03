'''
Created on May 31, 2010

@author: jnaous
'''

class PermissionRegistrationConflict(Exception):
    """
    Raised when a permission is registered with two different URLs.
    """
    def __init__(self, perm_name, new_url, old_url):
        message = "Permission %s is already registered " % perm_name
        message += "with url name %s. Cannot register " % old_url
        message += "again with url %s." % new_url
        super(PermissionRegistrationConflict, self).__init__(message)

class PermissionDenied(Exception):
    """
    Raised when a permission is denied/not found. Has a URL to be redirected to
    to obtain the required permission if possible.
    """
    def __init__(self, perm_name, target, user, url_name):
        message = "Permission %s was not found for permission user %s for \
target object %s" % (perm_name, user, target)
        self.url_name = url_name
        self.target = target
        self.user = user
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
    
    def __init__(self, object):
        message = "Permissions cannot be used for object class \
%s which does not inherit from ControlledModel" % object.__class__
        super(PermissionDecoratorUsageError, self).__init__(message)

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
        
class ModelNotRegisteredAsControlledType(Exception):
    """
    Raised when the ControlledContentType for a model is not found.
    """
    
    def __init__(self, model):
        super(ModelNotRegisteredAsControlledType, self).__init__(
            "Model %s is not registered as a controlled type" % model,
        )
        self.model = model
