'''
@author: jnaous
'''
from django.views.generic import list_detail, create_update, simple
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, Http404,\
    HttpResponse
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.clearinghouse.aggregate.forms import AggregateTypeForm
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from expedient.common.messaging.models import DatedMessage
import logging
from expedient.common.permissions.decorators import require_objs_permissions_for_view
from expedient.common.permissions.utils import get_user_from_req, get_queryset,\
    get_queryset_from_class, get_leaf_queryset, get_object_from_ids
from django.contrib.auth.models import User
from expedient.clearinghouse.project.models import Project
from expedient.clearinghouse.slice.models import Slice
import traceback

logger = logging.getLogger("AggregateViews")

TEMPLATE_PATH = "expedient/clearinghouse/aggregate"

@require_objs_permissions_for_view(
    perm_names=["can_add_aggregate"],
    permittee_func=get_user_from_req,
    target_func=get_queryset_from_class(Aggregate),
    methods=["POST"])
def list(request, agg_id=None):
    '''
    Get a list of aggregates. agg_id specifies id to highlight. On POST,
    get the type of aggregate to be created and redirect to that model's
    create url.
    '''
    
    qs = Aggregate.objects.all().order_by('name')
    
    if request.method == "GET":
        form = AggregateTypeForm()
    elif request.method == "POST":
        form = AggregateTypeForm(request.POST)
        if form.is_valid():
            model = form.cleaned_data["type"].model_class()
            return HttpResponseRedirect(model.get_create_url())
    else:
        return HttpResponseNotAllowed("GET", "POST")
    
    return list_detail.object_list(
        request,
        queryset=qs,
        template_name=TEMPLATE_PATH+"/list.html",
        template_object_name="aggregate",
        extra_context={
            'form': form,
            'highlight_id': agg_id,
        },
    )

@require_objs_permissions_for_view(
    perm_names=["can_edit_aggregate"],
    permittee_func=get_user_from_req,
    target_func=get_leaf_queryset(Aggregate, "agg_id"),
    methods=["GET", "POST"])
def delete(request, agg_id):
    """
    Display a confirmation page then stop all slices and delete the aggregate.
    """
    next = request.GET.get("next", None) or reverse("home")
    aggregate = get_object_or_404(Aggregate, id=agg_id).as_leaf_class()
    # Stop all slices using the aggregate
    if request.method == "POST":
        for s in aggregate.slice_set.all():
            aggregate.stop_slice(s)
    # Delete the aggregate.
    req = create_update.delete_object(
        request,
        model=aggregate.__class__,
        post_delete_redirect=next,
        object_id=agg_id,
        extra_context={"next": next},
        template_name=TEMPLATE_PATH+"/delete.html",
    )
    if req.status_code == HttpResponseRedirect.status_code:
        DatedMessage.objects.post_message_to_user(
            "Successfully deleted aggregate %s" % aggregate.name,
            request.user, msg_type=DatedMessage.TYPE_SUCCESS,
        )
    return req

def info(request, ct_id):
    """
    Return a page that shows the information on the aggregate.
    """
    try:
        ct = ContentType.objects.get_for_id(ct_id)
    except:
        raise Http404()
    model = ct.model_class()
    info = model.information
    
    return simple.direct_to_template(
        request, template=TEMPLATE_PATH+"/info.html",
        extra_context={"info": info, "type": model._meta.verbose_name})

def get_can_use_permission(request, permission, permittee,
                           target_obj_or_class, redirect_to=None):
    """Get the 'can_use_aggregate' permission.
    
    For project, slice, or user permittees, call the corresponding
    add_to_* method of the target aggregate.
    """
    assert(isinstance(target_obj_or_class, Aggregate))
    assert(
        isinstance(permittee, User) or
        isinstance(permittee, Project) or
        isinstance(permittee, Slice)
    )
    assert(permission.name == "can_use_aggregate")

    aggregate = target_obj_or_class
    
    try:
        next = request.session["breadcrumbs"][-1][1]
    except IndexError:
        next = redirect_to or reverse("home")
    
    if isinstance(permittee, Project):
        return HttpResponseRedirect(
            aggregate.as_leaf_class().add_to_project(permittee, next))
    elif isinstance(permittee, Slice):
        return HttpResponseRedirect(
            aggregate.as_leaf_class().add_to_slice(permittee, next))
    else: # isinstance(permittee, User)
        return HttpResponseRedirect(
            aggregate.as_leaf_class().add_to_user(permittee, next))

def status_img_url(request, agg_id):
    """Get the url for the status image of the aggregate"""
    
    aggregate = get_object_or_404(Aggregate, pk=agg_id)
    
    success = HttpResponse(reverse("img_media", args=["active.png"]))
    fail = HttpResponse(reverse("img_media", args=["inactive.png"]))
    
    try:
        # Check aggregate status and update model if it changed
        agg_status = aggregate.as_leaf_class().check_status()
        if agg_status != aggregate.available:
            aggregate.available = agg_status
            aggregate.save()
        if agg_status:
            return success
        else:
            return fail
    except:
        logger.error(traceback.format_exc())
        return fail
 
