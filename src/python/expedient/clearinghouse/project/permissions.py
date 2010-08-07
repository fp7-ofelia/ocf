'''
Created on Aug 3, 2010

@author: jnaous
'''
from expedient.common.permissions.shortcuts import create_permission
from expedient.clearinghouse.permissionmgmt.utils import \
    request_permission_wrapper
from expedient.clearinghouse.roles.views import make_request

def run():
    create_permission(
        "can_create_project",
        description=\
            "Owners of this permission can create projects in Expedient.",
        view=request_permission_wrapper,
    )
    
    create_permission(
        "can_edit_project",
        description=\
            "Owners of this permission can edit basic project properties.",
        view=make_request,
        force=True,
    )
    
    create_permission(
        "can_delete_project",
        description=\
            "Owners of this permission can edit basic project properties.",
        view=make_request,
        force=True,
    )
    
    create_permission(
        "can_view_project",
        description=\
            "Owners of this permission can view the project. Without "
            "other permissions, they are non-functional members.",
        view=make_request,
        force=True,
    )
    
    create_permission(
        "can_add_members",
        description=\
            "Owners of this permission can add members to "
            "the project and assign to them roles.",
        view=make_request,
        force=True,
    )
    
    create_permission(
        "can_remove_members",
        description=\
            "Owners of this permission can remove members from "
            "the project. They can also remove permissions from roles and "
            "remove roles from users.",
        view=make_request,
        force=True,
    )
    
    create_permission(
        "can_create_slices",
        description=\
            "Owners of this permission can create new slices.",
        view=make_request,
        force=True,
    )
    
    create_permission(
        "can_edit_slices",
        description=\
            "Owners of this permission can modify existing slices.",
        view=make_request,
        force=True,
    )
    
    create_permission(
        "can_delete_slices",
        description=\
            "Owners of this permission can delete existing slices.",
        view=make_request,
        force=True,
    )
    
    create_permission(
        "can_stop_slices",
        description=\
            "Owners of this permission can start slices.",
        view=make_request,
        force=True,
    )
    
    create_permission(
        "can_start_slices",
        description=\
            "Owners of this permission can stop slices.",
        view=make_request,
        force=True,
    )
    
    create_permission(
        "can_add_aggregates",
        description=\
            "Owners of this permission can add aggregates "
            "to the project.",
        view=make_request,
        force=True,
    )
    
    create_permission(
        "can_remove_aggregates",
        description=\
            "Owners of this permission can remove aggregates "
            "from the project.",
        view=make_request,
        force=True,
    )
    
    create_permission(
        "can_create_roles",
        description=\
            "Owners of this permission can create roles "
            "in the project",
        view=make_request,
        force=True,
    )
    
    create_permission(
        "can_edit_roles",
        description=\
            "Owners of this permission can modify and delete roles "
            "in the project",
        view=make_request,
        force=True,
    )
