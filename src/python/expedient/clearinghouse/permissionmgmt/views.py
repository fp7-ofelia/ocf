'''
Created on Jul 27, 2010

@author: jnaous
'''
from expedient.common.permissions.models import PermissionRequest,\
    ObjectPermission, ExpedientPermission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic import simple
from django.db.models import Q
from django.views.generic.simple import direct_to_template

TEMPLATE_PATH = "permissionmgmt"

def permissions_dashboard(request):
    """
    Display a list of current requests and buttons to approve/deny. Also
    display table of user's permissions.
    """
    
    perm_reqs = PermissionRequest.objects.filter(
        permission_owner=request.user)
    
    my_perms = ObjectPermission.objects.filter(
        users__user_type=ContentType.objects.get_for_model(User),
        users__user_id=request.user.id)
    
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
    
    # list of permission requests for this user
    perm_reqs = PermissionRequest.objects.filter(
        permission_owner=request.user)
    
    approved_req_ids = request.session.get("approved_req_ids", [])
    delegatable_req_ids = request.session.get("delegatable_req_ids", [])
    denied_req_ids = request.session.get("denied_req_ids", [])

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
            for req, delegatable in approved_reqs:
                req.allow(delegatable=delegatable)
        
            for req in denied_reqs:
                req.deny()
                
        # After this post we will be done with all this information
        request.session["approved_req_ids"] = approved_req_ids
        request.session["delegatable_req_ids"] = delegatable_req_ids
        request.session["denied_req_ids"] = denied_req_ids

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

# TODO: Add the URLs
# TODO: Add tests
# TODO: Run tests
