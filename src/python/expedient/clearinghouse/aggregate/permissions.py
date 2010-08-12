'''
Created on Jun 2, 2010

@author: jnaous
'''
from expedient.common.permissions.shortcuts import create_permission
from expedient.clearinghouse.permissionmgmt.utils import \
    request_permission_wrapper
from expedient.clearinghouse.aggregate.views import get_can_use_permission

def run():
    create_permission(
        "can_add_aggregate",
        description="Owners of this permission can add aggregates to Expedient.",
        view=request_permission_wrapper,
    )
    create_permission(
        "can_edit_aggregate",
        description=\
            "Owners of this permission can edit or delete "
            "the related aggregates in Expedient.",
        view=request_permission_wrapper,
    )
    create_permission(
        "can_use_aggregate",
        description=\
            "Projects, slices, and users that are owners of this permission "
            "can use the aggregate by starting or stopping slices on it, and "
            "by calling other methods.",
        view=get_can_use_permission,
    )
