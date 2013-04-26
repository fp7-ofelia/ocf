'''
Created on Aug 9, 2010

@author: jnaous
'''
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import simple
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from expedient.clearinghouse.roles.models import ProjectRole,\
    ProjectRoleRequest
from expedient.clearinghouse.roles.utils import get_users_for_role
from expedient.common.messaging.models import DatedMessage
from expedient.clearinghouse.project.models import Project
from expedient.clearinghouse.roles.forms import SelectRoleForm, ProjectRoleForm
from expedient.common.utils.views import generic_crud
from expedient.common.permissions.models import ObjectPermission, Permittee
from expedient.common.permissions.shortcuts import must_have_permission

TEMPLATE_PATH="roles"

def create(request, proj_id):
    """Create a new role for a project."""
    
    project = get_object_or_404(Project, pk=proj_id)
    
    # require permission to proceed
    must_have_permission(request.user, project, "can_create_roles")
    
    obj_permissions = ObjectPermission.objects.filter_from_instance(project)
    
    project_url = reverse("project_detail", args=[project.id])
    
    def pre_save(instance, created):
        instance.project = project
    
    return generic_crud(
        request,
        obj_id=None,
        model=ProjectRole,
        template=TEMPLATE_PATH+"/create.html",
        redirect=lambda instance: project_url,
        form_class=ProjectRoleForm,
        pre_save=pre_save,
        extra_form_params={
            "obj_permissions": obj_permissions,
        },
        extra_context={
            "project": project,
            "breadcrumbs": (
                ("Home", reverse("home")),
                ("Project %s" % project.name,
                 project_url),
                ("Create Role", request.path),
            )
        }
    )

def update(request, role_id):
    """Update the permissions in the role"""

    role = get_object_or_404(ProjectRole, pk=role_id)

    # require permission to proceed
    must_have_permission(request.user, role.project, "can_edit_roles")

    permittee = Permittee.objects.get_as_permittee(request.user)

    initial_set = list(role.obj_permissions.values_list("pk", flat=True))

    # Get the permissions that the user can delegate to others as well
    # as the ones that are already in the role. Obtain DISTINCT values.
    obj_permissions = ObjectPermission.objects.filter_from_instance(
        role.project).filter(
            Q(permissionownership__permittee=permittee,
              permissionownership__can_delegate=True) |
            Q(id__in=initial_set)
        ).distinct()

    project_url = reverse("project_detail", args=[role.project.id])

    # Use to update the permissions in the ProjectRole object so
    # users with that role are affected from the time this is updated
    def post_save(instance, created):
        from expedient.clearinghouse.roles.models import ObjectPermission
        new_obj_permissions_pks = [ p.pk for p in instance.obj_permissions.all() ]
        for permission in obj_permissions:
            # Add and delete permissions accordingly...
            try:
                instance.remove_permission(permission)
            except:
                pass
            if permission.pk in new_obj_permissions_pks:
                instance.add_permission(permission)

    return generic_crud(
        request,
        obj_id=role_id,
        model=ProjectRole,
        template=TEMPLATE_PATH+"/update.html",
        redirect=lambda instance: project_url,
        template_object_name="role",
        form_class=ProjectRoleForm,
        extra_form_params={
            "obj_permissions": obj_permissions,
        },
        extra_context={
            "project": role.project,
            "breadcrumbs": (
                ("Home", reverse("home")),
                ("Project %s" % role.project.name, project_url),
                ("Update Role %s" % role.name, request.path),
            )
        },
        post_save = post_save,
    )

def delete(request, role_id):
    """Delete a role"""

    role = get_object_or_404(ProjectRole, pk=role_id)
    project = role.project
    
    # require permission to proceed
    must_have_permission(request.user, project, "can_edit_roles")

    if role.name == "owner" or role.name == "researcher":
        return simple.direct_to_template(
            request,
            template=TEMPLATE_PATH+"/delete_default.html",
            extra_context={"role": role})
    
    if request.method == "POST":
        role.delete()
        return HttpResponseRedirect(
            reverse("project_detail", args=[project.id]))
    
    return simple.direct_to_template(
        request,
        template=TEMPLATE_PATH+"/delete.html",
        extra_context={
            "breadcrumbs": (
                ("Home", reverse("home")),
                ("Project %s" % role.project.name,
                 reverse("project_detail", args=[role.project.id])),
                ("Delete Role %s" % role.name, request.path),
            ),
            "role": role},
    )

def make_request(request, permission, permittee, target_obj_or_class,
                 redirect_to=None):
    """When a permission is missing allow user to request a role.
    
    Show the user a list of roles that have the missing permission, and
    allow her to request the permission from a user who can give that role.
    
    @see: L{ExpedientPermission} for information about permission redirection.
    """
    
    if permittee != request.user:
        raise PermissionDenied
    
    assert(isinstance(permittee, User))
    try:
        done_url = request.session["breadcrumbs"][-1][1]
    except IndexError:
        done_url = reverse("home")
    # get all the roles that have this permission
    roles = ProjectRole.objects.filter_for_permission(
        permission.name, target_obj_or_class)
   
    if not roles:
       return simple.direct_to_template(
        request,
        template=TEMPLATE_PATH+"/no_permission.html",
        extra_context={
            "cancel_url": done_url,
            "target": target_obj_or_class,
        }
        )
 
    # for each role get the users that can delegate it
    roles_to_users = {}
    for r in roles:
        givers = get_users_for_role(r, can_delegate=True)
        roles_to_users[r.id] = givers

    if request.method == "POST":
        req = ProjectRoleRequest(requester=request.user)
        form = SelectRoleForm(
            roles, roles_to_users, request.POST, instance=req)
        if form.is_valid():
            req = form.save()
            DatedMessage.objects.post_message_to_user(
                "Request for '%s' role in project '%s' sent to user '%s'"
                    % (req.requested_role.name,
                       req.requested_role.project,
                       req.giver.username),
                user=request.user,
                msg_type=DatedMessage.TYPE_SUCCESS)
            return HttpResponseRedirect(done_url)
    else:
        form = SelectRoleForm(
            roles, roles_to_users)

    return simple.direct_to_template(
        request,
        template=TEMPLATE_PATH+"/make_request.html",
        extra_context={
            "cancel_url": done_url,
            "form": form,
            "target": target_obj_or_class,
        }
    )

def confirm_request(request, proj_id, req_id, allow, delegate):
    project = get_object_or_404(Project, pk=proj_id)
    role_req = get_object_or_404(ProjectRoleRequest, pk=req_id)
    
    if request.user != role_req.giver:
        raise PermissionDenied

    allow = int(allow)
    delegate = int(delegate)
    
    if request.method == "POST":
        if allow:
            role_req.approve(delegate)
        else:
            role_req.deny()
        return HttpResponseRedirect(reverse("project_detail", args=[proj_id]))
    else:
        return simple.direct_to_template(
            request,
            template=TEMPLATE_PATH+"/confirm_request.html",
            extra_context={
                "project": project,
                "role_req": role_req,
                "allow": allow,
                "delegate": delegate,
            }
        )
