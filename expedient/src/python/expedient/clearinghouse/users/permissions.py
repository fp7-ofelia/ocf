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
            "or delete a particular user.",
        view=request_permission_wrapper,
    )
    create_permission(
        "can_manage_users",
        description=\
            "Owners of this permission can view/modify/delete users in the"
            " user management page.",
        view=request_permission_wrapper,
    )
