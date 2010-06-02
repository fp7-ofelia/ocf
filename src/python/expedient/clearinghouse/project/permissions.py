'''
Created on Jun 1, 2010

@author: jnaous
'''
from expedient.common.permissions.decorators import require_obj_permissions
from expedient.common.permissions.utils import register_controlled_type
from models import Project

class require_obj_permissions_for_project(require_obj_permissions):
    """
    Decorator that checks that the passed in C{project} keyword argument
    to the decorated method has the named permissions in the required
    permissions list for the object.
    
    This is a subclass of
    L{expedient.common.permissions.decorators.require_obj_permissions}
    that uses "project" as the C{user_kw} parameter for the decorator.
    """
    
    def __init__(self, perm_names, pop_user_kw=True):
        super(require_obj_permissions_for_project, self).__init__(
            "project", perm_names, pop_user_kw)

