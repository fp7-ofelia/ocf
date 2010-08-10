'''
Created on Aug 9, 2010

@author: jnaous
'''
from expedient.common.permissions.utils import get_object_from_ids
from expedient.clearinghouse.roles.models import ProjectRole,\
    ProjectRoleRequest
from expedient.clearinghouse.roles.utils import get_users_for_role
from expedient.common.messaging.models import DatedMessage
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import simple
from django.shortcuts import get_object_or_404
from expedient.clearinghouse.project.models import Project
from expedient.clearinghouse.roles.forms import SelectRoleForm
from django.contrib.auth.models import User

TEMPLATE_PATH="roles"

def make_request(request, permission, permittee, target_obj_or_class,
                 redirect_to=None):
    """When a permission is missing allow user to request a role.
    
    Show the user a list of roles that have the missing permission, and
    allow her to request the permission from a user who can give that role.
    
    @see: L{ExpedientPermission} for information about permission redirection.
    """
    
    assert(isinstance(permittee, User))
    try:
        done_url = request.session["breadcrumbs"][-1][1]
    except IndexError:
        done_url = reverse("home")
    
    # get all the roles that have this permission
    roles = ProjectRole.objects.filter_for_permission(
        permission.name, target_obj_or_class)
    
    # for each role get the users that can delegate it
    roles_to_users = {}
    for r in roles:
        givers = get_users_for_role(r.name, can_delegate=True)
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
