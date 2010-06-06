'''
Created on Jun 6, 2010

@author: jnaous
'''
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from expedient.common.permissions.exceptions import PermissionDenied
from expedient.common.permissions.models import ExpedientPermission,\
    PermissionRequest, PermissionUser
from expedient.common.permissions.utils import get_object_from_ids,\
    register_permission_for_obj_or_class
from django.core.urlresolvers import get_callable
from expedient.common.permissions.forms import PermissionRequestForm
from django.views.generic import simple, create_update
from django.contrib.auth.models import User

def reraise_permission_denied(request, perm_name=None,
                              target_ct_id=None, target_id=None,
                              user_ct_id=None, user_id=None):
    """
    Raises a PermissionDenied exception for the given parameters.
    """
    target_obj_or_class = get_object_from_ids(target_ct_id, target_id)
    user = get_object_from_ids(user_ct_id, user_id)
    raise PermissionDenied(perm_name, target_obj_or_class, user, False)

def redirect_permissions_request(request, perm_name=None,
                                 target_ct_id=None, target_id=None,
                                 user_ct_id=None, user_id=None):
    """
    Gets the target and user objects and passes them along with the 
    L{ExpedientPermission} object named by C{perm_name} to the view that's
    used by the permission.
    """
    permission = get_object_or_404(ExpedientPermission, name=perm_name)
    target_obj_or_class = get_object_from_ids(target_ct_id, target_id)
    # Change from ContentType to class
    if type(target_obj_or_class) == ContentType:
        target_obj_or_class = target_obj_or_class.model_class()
    user = get_object_from_ids(user_ct_id, user_id)
    if not permission.view:
        raise PermissionDenied(perm_name, target_obj_or_class, user, False)
    
    view = get_callable(permission.view)
    
    # no urls allowed in redirection.
    redirect_to = request.GET.get("next", '')
    if not redirect_to or ' ' in redirect_to or "//" in redirect_to:
        redirect_to = None
    
    return view(request, permission, user, target_obj_or_class,
                redirect_to=redirect_to)

def request_permission(always_redirect_to,
                       permission_owners_func=None,
                       template="permissions/get_permission.html"):
    """
    Get a generic view to use for creating PermissionRequests.
    
    The view's template context will have:
    - C{form}: the form to show the user. By default, this is a
        L{PermissionRequestForm}
    - C{obj_perm}: the L{ObjectPermission} instance requested.
    
    The form will show all users that can delegate the requested permission by
    default. To change the shown set, specify C{permission_owners_func} which
    should return the set to show.
    
    @param always_redirect_to: path to redirect to after the permission request
        is saved.
    @keyword permission_owners_func: A callable with the following signature::
        
            permission_owners_func(request, obj_permission, user)
            
        Where C{request} is the request object passed to the view,
        C{obj_permission} is the requested L{ObjectPermission} instance, and
        C{user} is the object that the permission is being requested for. The
        function should return {django.contrib.auth.models.User} C{QuerySet}.
    @keyword template: Path of the template to use. By default, this is
        "permissions/get_permission.html".
    """
    def request_permission_view(request, permission, user,
                                target_obj_or_class, redirect_to=None):
        # Get the object permission
        obj_perm = register_permission_for_obj_or_class(
            target_obj_or_class, permission)[0]
        
        # Get the users who can delegate the permission
        if permission_owners_func:
            user_qs = permission_owners_func(request, obj_perm, user)
        else:
            user_qs = PermissionUser.objects.get_objects_queryset(
                User,
                dict(
                    permissioninfo__obj_permission=obj_perm,
                    permissioninfo__can_delegate=True),
                {})
        
        # process the request
        if request.method == "POST":
            perm_request = PermissionRequest(requesting_user=request.user,
                                             requested_permission=obj_perm)
            form = PermissionRequestForm(user_qs, request.POST,
                                         instance=perm_request)
            if form.is_valid():
                # Post a permission request for the permission owner
                perm_request = form.save()
                return simple.redirect_to(request, always_redirect_to,
                                          permanent=False)
        else:
            form = PermissionRequestForm(user_qs)
        
        return simple.direct_to_template(
            request, template=template,
            extra_context={"form": form, "obj_perm": obj_perm})
    return request_permission_view
