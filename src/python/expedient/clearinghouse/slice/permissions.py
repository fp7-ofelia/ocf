'''
Created on Jun 1, 2010

@author: jnaous
'''
from expedient.common.permissions.decorators import require_obj_permissions

class require_obj_permissions_for_slice(require_obj_permissions):
    """
    Decorator that checks that the passed in C{slice} keyword argument
    to the decorated method has the named permissions in the required
    permissions list for the object.
    
    This is a subclass of
    L{expedient.common.permissions.decorators.require_obj_permissions}
    that uses "slice" as the C{user_kw} parameter for the decorator.
    """
    
    def __init__(self, perm_names, pop_user_kw=True):
        super(require_obj_permissions_for_slice, self).__init__(
            "slice", perm_names, pop_user_kw)