'''
Created on Aug 3, 2010

@author: jnaous
'''
from expedient.common.permissions.shortcuts import create_permission
from expedient.clearinghouse.permissionmgmt.utils import \
    request_permission_wrapper

def run():
    create_permission(
        "can_edit_user",
        description=\
            "Owners of this permission can modify information about "
            "or delete a user.",
        view=request_permission_wrapper,
    )
