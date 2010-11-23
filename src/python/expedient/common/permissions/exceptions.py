'''
Created on May 31, 2010

@author: jnaous
'''

from django.db import models
from django.contrib.contenttypes.models import ContentType

class PermissionException(Exception):
    """
    Base class for all exceptions from the permissions application.
    """
    pass

class UnexpectedParameterType(PermissionException):
    """
    Raised when a function receives an unexpected parameter type.
    @ivar found: the class that was found.
    @type found: C{class}
    @ivar expected: list of expected types.
    @type expected: C{[class]}
    @ivar index: position or keyword argument
    @type index: C{int} or C{str}
    """
    def __init__(self, found, expected, index):
        super(UnexpectedParameterType, self).__init__(
            "Found type '%s' as argument '%s'. Allowed types are %s" %
            (found, index, expected)
        )
        self.found = found
        self.expected = expected
        self.index = index
        
class PermitteeNotInThreadLocals(PermissionException):
    """
    Raised when the permittee was not parsed and stored in thread local storage.
    """
    def __init__(self, permittee_kw):
        self.permittee_kw = permittee_kw
        super(PermitteeNotInThreadLocals, self).__init__(
            "Threadlocal storage does not have the permittee keyword '%s'. "
            "This might be caused by not adding a parser to the Threadlocals "
            "middleware to parse the request for this keyword."
             % permittee_kw
        )

class NonePermitteeException(PermissionException):
    """
    Raised when the permittee is None.
    """
    pass

class PermissionRegistrationConflict(PermissionException):
    """
    Raised when a permission is registered with two different views.
    """
    def __init__(self, perm_name, new_view, old_view):
        message = "Permission %s is already registered " % perm_name
        message += "with view name %s. Cannot register " % old_view
        message += "again with view %s." % new_view
        super(PermissionRegistrationConflict, self).__init__(message)

class PermissionDenied(PermissionException):
    """
    Raised when a permission is denied/not found.
    """
    def __init__(self, perm_name, target, permittee, allow_redirect=True):
        from expedient.common.permissions.models import Permittee
        if not isinstance(target, models.Model):
            # assume class
            target = ContentType.objects.get_for_model(target)
        self.perm_name = perm_name
        self.target = target
        self.permittee = Permittee.objects.get_as_permittee(permittee)
        self.allow_redirect = allow_redirect
        super(PermissionDenied, self).__init__(
            "Permission '%s' was not found for permittee '%s' for "
            "target object '%s'" % (perm_name, permittee, target))

class PermissionSignatureError(PermissionException):
    """
    Raised when a function decorated with one of the require_* decorators
    does not have the right arguments for the call.
    """
    
    def __init__(self, function, keyword):
        message = "Permission checking for function %s requires the \
missing keyword argument %s.""" % (function.func_name, keyword)
        super(PermissionSignatureError, self).__init__(message)

class PermissionDecoratorUsageError(PermissionException):
    """
    Raised when the decorators are misused.
    """
    pass

class PermissionDoesNotExist(PermissionException):
    """
    Raised when a permission with a given name does not exist.
    """
    
    def __init__(self, perm_name, target=None):
        message = "Permission '%s' has not been created" % perm_name
        if target:
            message += " for target '%s'." % target
        else:
            message += "."
        message += " If you already have a line to create the permission in " \
            "a permissions.py file, then you might have not run syncdb to " \
            "create the permission."
        super(PermissionDoesNotExist, self).__init__(message)

class PermissionCannotBeDelegated(PermissionException):
    """
    Raised when a permittee tries to give permission to another when
    the permission cannot be delegated.
    """
    
    def __init__(self, giver, perm_name):
        message = "Giver '%s' cannot delegate permission '%s'." % (
            giver, perm_name)
        super(PermissionCannotBeDelegated, self).__init__(message)
