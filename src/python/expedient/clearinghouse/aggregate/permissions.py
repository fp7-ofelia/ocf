'''
Created on Jun 2, 2010

@author: jnaous
'''
from expedient.common.permissions.shortcuts import create_permission
from expedient.clearinghouse.permissionmgmt.utils import \
    request_permission_wrapper

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
