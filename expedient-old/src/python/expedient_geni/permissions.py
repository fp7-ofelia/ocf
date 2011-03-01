'''
Created on Sep 13, 2010

@author: jnaous
'''
from expedient.common.permissions.shortcuts import create_permission
from expedient.clearinghouse.permissionmgmt.utils import \
    request_permission_wrapper

def run():
    create_permission(
        "can_change_user_cert",
        description=\
            "Owners of this permission can view/modify users' GCF"
            "certificates.",
        view=request_permission_wrapper,
    )
