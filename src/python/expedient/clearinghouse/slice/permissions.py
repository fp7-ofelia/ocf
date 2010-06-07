'''
Created on Jun 1, 2010

@author: jnaous
'''
from expedient.common.permissions.decorators import require_obj_permissions

class require_obj_permissions_for_slice(require_obj_permissions):
    """
    Wrapper around require_obj_permissions that sets the C{user_kw} parameter
    to "slice"
    """
    def __init__(self, perm_names, pop_user_kw=True):
        super(require_obj_permissions_for_slice, self).__init__(
            "slice", perm_names, pop_user_kw)
