'''
Created on Jun 6, 2010

@author: jnaous
'''
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import get_callable
from django.views.generic import simple
from expedient.common.permissions.exceptions import PermissionDenied
from expedient.common.permissions.models import ExpedientPermission,\
    PermissionRequest, Permittee, ObjectPermission
from expedient.common.permissions.utils import get_object_from_ids
from expedient.common.permissions.forms import PermissionRequestForm, ProjectRequestForm
from expedient.common.messaging.models import DatedMessage
from django.contrib.auth.models import User
import logging
from expedient.common.utils.mail import send_mail # Wrapper for django.core.mail__send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.http import QueryDict

logger = logging.getLogger("permissions.views")

def reraise_permission_denied(request, perm_name=None,
                              target_ct_id=None, target_id=None,
                              permittee_ct_id=None, permittee_id=None):
    """
    Raises a PermissionDenied exception for the given parameters.
    """
    target_obj_or_class = get_object_from_ids(target_ct_id, target_id)
    permittee = get_object_from_ids(permittee_ct_id, permittee_id)
    raise PermissionDenied(perm_name, target_obj_or_class, permittee, False)

def redirect_permissions_request(request, perm_name=None,
                                 target_ct_id=None, target_id=None,
                                 permittee_ct_id=None, permittee_id=None):
    """
    Gets the target and permittee objects and passes them along with the 
    L{ExpedientPermission} object named by C{perm_name} to the view that's
    used by the permission.
    """
    permission = get_object_or_404(ExpedientPermission, name=perm_name)
    target_obj_or_class = get_object_from_ids(target_ct_id, target_id)
    # Change from ContentType to class
    if type(target_obj_or_class) == ContentType:
        target_obj_or_class = target_obj_or_class.model_class()
    permittee = get_object_from_ids(permittee_ct_id, permittee_id)
    if not permission.view:
        raise PermissionDenied(perm_name, target_obj_or_class, permittee, False)

    view = get_callable(permission.view)

    logger.debug("Calling permission view %s" % permission.view)

    # no urls allowed in redirection.
    redirect_to = request.session.get("from_url", '')
    if not redirect_to or ' ' in redirect_to or "//" in redirect_to:
        redirect_to = None

    return view(request, permission, permittee, target_obj_or_class,
                redirect_to=redirect_to)

def request_permission(always_redirect_to=None,
                       permission_owners_func=None,
                       extra_context={},
                       template="permissions/get_permission.html"):
    """
    Get a generic view to use for creating PermissionRequests. Because of the
    way the permissions app stores views, this function will need to
    be wrapped in another function. For example::
    
        def req_perm_wrapper(*args, **kwargs):
            return request_permission()(*args, **kwargs)
    
    The view's template context will have:
        - C{form}: the form to show the user. By default, this is a
            L{PermissionRequestForm}
        - C{obj_perm}: the L{ObjectPermission} instance requested.
        - Any extra items defined in C{extra_context}.
    
    The form will show all users that can delegate the requested permission by
    default. To change the shown set, specify C{permission_owners_func} which
    should return the set to show.
    
    @keyword always_redirect_to: path to redirect to after the permission
        request is saved. If None, then use the redirect_to parameter given to
        the view from the permission redirection. Default None. This can also
        be a callable that takes the request as argument.
    @keyword permission_owners_func: A callable with the following signature::
        
            permission_owners_func(request, obj_permission, permittee)
            
        Where C{request} is the request object passed to the view,
        C{obj_permission} is the requested L{ObjectPermission} instance, and
        C{permittee} is the object that will own the permission. The
        function should return a C{django.contrib.auth.models.User} C{QuerySet}.
    @keyword extra_context: A dictionary of values to add to the template
        context. By default, this is an empty dictionary. If a value in the
        dictionary is callable, the generic view will call it just before
        rendering the template.
    @keyword template: Path of the template to use. By default, this is
        "permissions/get_permission.html".
    """
    def request_permission_view(request, permission, permittee,
                                target_obj_or_class, redirect_to=None):

        # Get the object permission
        obj_perm = ObjectPermission.objects.get_or_create_for_object_or_class(
            permission, target_obj_or_class)[0]

        # Get the object permission name
        perm_name = obj_perm.permission.name 

        # Get the users who can delegate the permission
        if permission_owners_func:
            user_qs = permission_owners_func(request, obj_perm, permittee)
        else:
            #user_qs = Permittee.objects.filter_for_class_and_permission_name(
            #    klass=User,
            #    permission=obj_perm.permission,
            #    target_obj_or_class=obj_perm.target,
            #    can_delegate=True)
            #ONLY ISLAND MANAGER/S
            user_qs=User.objects.filter(is_superuser=1)

        # process the request
        if request.method == "POST":
            permittee = Permittee.objects.get_or_create_from_instance(
                permittee)[0]
            perm_request = PermissionRequest(requesting_user=request.user,
                                             permittee=permittee,
                                             requested_permission=obj_perm)

            posted_message = "permission %s" % permission.name
            if perm_name == "can_create_project":
                form = ProjectRequestForm(user_qs, request.POST,
                                         instance=perm_request)
                posted_message = "project %s" % str(request.POST["name"])
            else:
                form = PermissionRequestForm(user_qs, request.POST,
                                         instance=perm_request)
            if form.is_valid():
                # Post a permission request for the permission owner
                perm_request = form.save()
                DatedMessage.objects.post_message_to_user(
                    "Sent request for %s to user %s" %
                    (posted_message, perm_request.permission_owner),
                    user=request.user, msg_type=DatedMessage.TYPE_SUCCESS)
                try:
                     send_mail(
                         settings.EMAIL_SUBJECT_PREFIX + "Request for %s from user %s" % (posted_message, request.user),
                         "You have a new request for permission %s from user %s (%s). Please go to the Permission Management section in your Dashboard to manage it: https://%s\n\n Original User Message:\n\"%s\"" % (permission.name,request.user, request.user.email, settings.SITE_IP_ADDR, perm_request.message),
                         from_email=settings.DEFAULT_FROM_EMAIL,
                         recipient_list=[perm_request.permission_owner.email],
                         #recipient_list=[settings.ROOT_EMAIL],
                     )
                except Exception as e:
                    print "Email \"Request for permission %s from user %s\" could no be sent" % (permission.name,request.user)


                if callable(always_redirect_to):
                    redirect_to = always_redirect_to(request)
                else:
                    redirect_to = always_redirect_to or redirect_to
                return simple.redirect_to(request, redirect_to,
                                          permanent=False)
        # GET
        else:
            # Show the project form when the user can create projects
            if perm_name == "can_create_project":
                form = ProjectRequestForm(user_qs)
            else:
                form = PermissionRequestForm(user_qs)

        ec = {"form": form, "obj_perm": obj_perm, "perm_name": perm_name}
        ec.update(extra_context)

        return simple.direct_to_template(
            request, template=template,
            extra_context=ec)

    return request_permission_view
