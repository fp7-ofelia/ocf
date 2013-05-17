'''
Created on Jul 27, 2010

@author: jnaous
'''
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.views.generic import simple
from django.db.models import Q
from django.views.generic.simple import direct_to_template
from expedient.common.permissions.models import PermissionRequest,\
    ObjectPermission
from expedient.common.messaging.models import DatedMessage
from expedient.clearinghouse.project.views import create, create_project_roles
from expedient.clearinghouse.project.models import Project
import uuid
from expedient.common.utils.mail import send_mail # Wrapper for django.core.mail__send_mail
from django.conf import settings

TEMPLATE_PATH = "permissionmgmt"

def permissions_dashboard(request):
    """
    Display a list of current requests and buttons to approve/deny.
    """
    
    perm_reqs = PermissionRequest.objects.filter(
        permission_owner=request.user)
    
    my_perms = ObjectPermission.objects.filter(
        permittees__object_type=ContentType.objects.get_for_model(User),
        permittees__object_id=request.user.id)
    
    def filter_id(id):
        try:
            return int(id)
        except ValueError:
            pass
    
    if request.method == "POST":
        # list of approved requests
        approved_req_ids = set(map(filter_id, request.POST.getlist("approved")))
        # list of delegated requests
        delegatable_req_ids = set(map(filter_id, request.POST.getlist("delegate")))
        # list of denied requests
        denied_req_ids = set(map(filter_id, request.POST.getlist("denied")))
        # check that all ids exist
        found_ids = set(
            perm_reqs.filter(
                Q(pk__in=approved_req_ids) | Q(pk__in=denied_req_ids)
            ).values_list("pk", flat=True))
        
        for req_id in approved_req_ids.union(denied_req_ids):
            if req_id not in found_ids:
                raise Http404(
                    "Permission request with ID %s not found." % req_id)
        
        # store the request and redirect to a confirmation page
        request.session["approved_req_ids"] = approved_req_ids
        request.session["delegatable_req_ids"] = delegatable_req_ids
        request.session["denied_req_ids"] = denied_req_ids

        return HttpResponseRedirect(reverse(confirm_requests))
    
    else:
        return simple.direct_to_template(
            request,
            template=TEMPLATE_PATH+"/dashboard.html",
            extra_context=dict(
                perm_reqs=perm_reqs,
                my_perms=my_perms,
            ),
        )

def confirm_requests(request):
    """Confirm the approval of the permission requests."""
    
    approved_req_ids = request.session.setdefault("approved_req_ids", [])
    delegatable_req_ids = request.session.setdefault("delegatable_req_ids", [])
    denied_req_ids = request.session.setdefault("denied_req_ids", [])

    approved_reqs = []
    for req_id in approved_req_ids:
        req = get_object_or_404(PermissionRequest, id=req_id)
        delegatable = req_id in delegatable_req_ids
        approved_reqs.append((req, delegatable))
    
    denied_reqs = []
    for req_id in denied_req_ids:
        denied_reqs.append(
            get_object_or_404(PermissionRequest, id=req_id))

    if request.method == "POST":
        # check if confirmed and then do actions.
        if request.POST.get("post", "no") == "yes":
            for req in denied_reqs:
                req.deny()
#                DatedMessage.objects.post_message_to_user(
#                    "Request for permission %s for object %s denied."
#                    % (req.requested_permission.permission.name,
#                       req.requested_permission.target),
#                    user=req.requesting_user,
#                    sender=req.permission_owner,
#                    msg_type=DatedMessage.TYPE_WARNING)

                post_message = "Request for %s denied." % str(req.requested_permission.target).capitalize()
                if req.requested_permission.permission.name == "can_create_project":
                    # Removes "* Project name: "
                    try:
                        project_name = req.message.split("||")[0].strip()[16:]
                        post_message = "Request for project %s creation denied." % project_name

                        # Notify requesting user
                        try:
                            send_mail(
                                     settings.EMAIL_SUBJECT_PREFIX + "Denied project request for '%s'" % (project_name),
                                     "Your request for the creation of project '%s' has been denied.\n\n\nYou may want to get in contact with the Island Manager for further details." % project_name, 
                                     from_email = settings.DEFAULT_FROM_EMAIL,
                                     recipient_list = [req.requesting_user.email],
                             )
                        except Exception as e:
                            print "[WARNING] User e-mail notification could not be sent. Details: %s" % str(e)

                    except:
                        pass
                # -------------------------------------------
                # It is not about permission granting anymore
                # -------------------------------------------
                # Notify requesting user
                DatedMessage.objects.post_message_to_user(
                    post_message,
                    user = req.requesting_user,
                    sender = req.permission_owner,
                    msg_type = DatedMessage.TYPE_WARNING)

                # Notify user with permission (e.g. root)
                DatedMessage.objects.post_message_to_user(
                    post_message,
                    user = request.user,
                    sender = req.permission_owner,
                    msg_type = DatedMessage.TYPE_WARNING)

            for req, delegate in approved_reqs:
                # --------------------------------------------------------
                # Do NOT grant permission to create projects in the future
                # --------------------------------------------------------
#                req.allow(can_delegate=delegate)
                req.deny()
#                DatedMessage.objects.post_message_to_user(
#                    "Request for permission %s for object %s approved."
#                    % (req.requested_permission.permission.name,
#                       req.requested_permission.target),
#                    user=req.requesting_user,
#                    sender=req.permission_owner,
#                    msg_type=DatedMessage.TYPE_SUCCESS)

                post_message = "Request for %s approved." % str(req.requested_permission.target).capitalize()
                permission_user_post = post_message
                requesting_user_post = post_message
                email_header = post_message
                email_body = "%s." % post_message
                message_type = DatedMessage.TYPE_SUCCESS
                # ---------------------------------------
                # Project will be created in a direct way
                # ---------------------------------------
                if req.requested_permission.permission.name == "can_create_project":
                    project_name = ""
                    try:
                        project = Project()
                        project.uuid = uuid.uuid4()
                        message = req.message.split("||")
                        # Removes "* Project name: "
                        project.name = message[0].strip()[16:]
                        project_name = project.name
                        # Removes "* Project description: "
                        project.description = message[3].strip()[23:]
                        post_message = "Successfully created project %s" % project.name
                        project.save()
                        create_project_roles(project, req.requesting_user)
                        project.save()
                        email_header = "Approved project request for '%s'" % project_name
                        email_body = "Your request for the creation of project '%s' has been approved." % project_name
                    except Exception as e:
                        # Any error when creating a project results into:
                            # 1. Denying the petition
                            # 2. Notifying user in their Expedient
                            # 3. Notifying user via e-mail
                        post_message = "Project '%s' could not be created" % project_name
                        permission_user_post = post_message
                        requesting_user_post = post_message

                        # Handle exception text for user
                        if "duplicate entry" in str(e).lower():
                            email_body = "There is already a project with name '%s'. Try using a different name" % project_name
                            requesting_user_post += ". Details: project '%s' already exists" % project_name
                        else:
                            email_body = "There might have been a problem when interpreting the information for project '%s'" % str(project_name)
                        requesting_user_post += ". Contact your Island Manager for further details"

                        # Handle exception text for admin
                        if "Details" not in post_message:
                            permission_user_post = "%s. Details: %s" % (post_message, str(e))

                        message_type = DatedMessage.TYPE_ERROR
                        # Email for requesting user
                        email_header = "Denied project request for '%s'" % project_name
                        email_body = "Your request for the creation of project '%s' has been denied because of the following causes:\n\n%s\n\n\nYou may want to get in contact with the Island Manager for further details." % (project_name, email_body)

                    # Notify requesting user
                    DatedMessage.objects.post_message_to_user(
                        requesting_user_post,
                        user = req.requesting_user,
                        sender = req.permission_owner,
                        msg_type = message_type)

                    try:
                        send_mail(
                                 settings.EMAIL_SUBJECT_PREFIX + email_header,
                                 email_body,
                                 from_email = settings.DEFAULT_FROM_EMAIL,
                                 recipient_list = [req.requesting_user.email],
                         )
                    except Exception as e:
                        print "[WARNING] User e-mail notification could not be sent. Details: %s" % str(e)

                    # Notify user with permission (e.g. root)
                    DatedMessage.objects.post_message_to_user(
                        permission_user_post,
                        user = request.user,
                        sender = req.permission_owner,
                        msg_type = message_type)
                    

        # After this post we will be done with all this information
        del request.session["approved_req_ids"]
        del request.session["delegatable_req_ids"]
        del request.session["denied_req_ids"]
        
        return HttpResponseRedirect(reverse("home"))
    
    else:
        return direct_to_template(
            request=request,
            template=TEMPLATE_PATH+"/confirm_requests.html",
            extra_context={
                "approved_reqs": approved_reqs,
                "denied_reqs": denied_reqs,
            }
        )
