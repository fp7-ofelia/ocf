'''
@author: jnaous
'''
import logging
from django.views.generic import simple
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q
from django.db.models.loading import cache
from django.conf import settings
from expedient.common.messaging.models import DatedMessage
from expedient.common.utils.views import generic_crud
from expedient.common.xmlrpc_serverproxy.forms import PasswordXMLRPCServerProxyForm
from expedient.common.permissions.decorators import require_objs_permissions_for_view
from expedient.common.permissions.utils import \
    get_queryset_from_class, get_user_from_req, get_queryset
from expedient.clearinghouse.slice.models import Slice
from expedient.clearinghouse.resources.models import Resource
from expedient.clearinghouse.aggregate.models import Aggregate
from models import OpenFlowAggregate, OpenFlowSliceInfo, OpenFlowConnection
from models import NonOpenFlowConnection
from forms import OpenFlowAggregateForm, OpenFlowSliceInfoForm
from forms import OpenFlowStaticConnectionForm, OpenFlowConnectionSelectionForm
from forms import NonOpenFlowStaticConnectionForm
from expedient.common.permissions.shortcuts import give_permission_to,\
    must_have_permission

logger = logging.getLogger("OpenFlow plugin views")
TEMPLATE_PATH = "openflow/plugin"

@require_objs_permissions_for_view(
    perm_names=["can_add_aggregate"],
    permittee_func=get_user_from_req,
    target_func=get_queryset_from_class(Aggregate),
    methods=["POST"])    
def aggregate_create(request):
    return aggregate_crud(request)

@require_objs_permissions_for_view(
    perm_names=["can_edit_aggregate"],
    permittee_func=get_user_from_req,
    target_func=get_queryset(OpenFlowAggregate, "agg_id"),
    methods=["POST"])
def aggregate_edit(request, agg_id):
    return aggregate_crud(request, agg_id=agg_id)
    
def aggregate_crud(request, agg_id=None):
    '''
    Create/update an OpenFlow Aggregate.
    '''
    
    if agg_id != None:
        aggregate = get_object_or_404(OpenFlowAggregate, pk=agg_id)
        client = aggregate.client
    else:
        aggregate = None
        client = None
        
    if request.method == "GET":
        agg_form = OpenFlowAggregateForm(instance=aggregate)
        client_form = PasswordXMLRPCServerProxyForm(instance=client)
        
    elif request.method == "POST":
        logger.debug("aggregate_crud got post")
        agg_form = OpenFlowAggregateForm(
            data=request.POST, instance=aggregate)
        client_form = PasswordXMLRPCServerProxyForm(
            data=request.POST, instance=client)
        logger.debug("Validating")
        if client_form.is_valid() and agg_form.is_valid():
            logger.debug("Forms are valid")
            logger.debug("Got logo %s" % request.POST.get("logo", ""))
            # Save the client first
            client = client_form.save()
            # Then save the aggregate and add the client
            aggregate = agg_form.save(commit=False)
            aggregate.client = client
            aggregate.save()
            agg_form.save_m2m()
            err = aggregate.setup_new_aggregate(request.build_absolute_uri("/"))
            if err:
                transaction.rollback()
                if agg_id:
                    msg = "Problem setting up the updated aggregate. %s" % err
                else:
                    msg = "Problem setting up the new aggregate. %s" % err
                DatedMessage.objects.post_message_to_user(
                    msg, user=request.user, msg_type=DatedMessage.TYPE_ERROR,
                )
                print err
            else:
                aggregate.save()
                DatedMessage.objects.post_message_to_user(
                    "Successfully created/updated aggregate %s" % aggregate.name,
                    user=request.user, msg_type=DatedMessage.TYPE_SUCCESS,
                )
            
                return HttpResponseRedirect(reverse("openflow_aggregate_add_links", args=[aggregate.id]))
        logger.debug("Validation failed")
    else:
        return HttpResponseNotAllowed("GET", "POST")
    
    available = aggregate.check_status() if agg_id else False
    return simple.direct_to_template(
        request,
        template=TEMPLATE_PATH+"/aggregate_crud.html",
        extra_context={
            "agg_form": agg_form,
            "client_form": client_form,
            "create": not agg_id,
            "aggregate": aggregate,
            "available": available,
            "breadcrumbs": (
                ('Home', reverse("home")),
                ("%s OpenFlow Aggregate" % ("Update" if agg_id else "Add"),
                 request.path),
            )
        },
    )
    
@require_objs_permissions_for_view(
    perm_names=["can_edit_aggregate"],
    permittee_func=get_user_from_req,
    target_func=get_queryset(OpenFlowAggregate, "agg_id"),
    methods=["POST"])
def aggregate_add_links(request, agg_id):
    """
    Show page to add static connections to other aggregates.
    """
    aggregate = get_object_or_404(OpenFlowAggregate, id=agg_id)
    
    # Get the queryset of all openflow connections to/from this aggregate
    of_iface_filter = (
        (     Q(src_iface__aggregate__id=aggregate.id)
              & ~Q(dst_iface__aggregate__id=aggregate.id)  )
        |
        (     Q(dst_iface__aggregate__id=aggregate.id)
              & ~Q(src_iface__aggregate__id=aggregate.id)  )
    )
    of_cnxn_qs = OpenFlowConnection.objects.filter(of_iface_filter)

    # Get the queryset of all non-openflow connections to aggregate
    non_of_cnxn_qs = NonOpenFlowConnection.objects.filter(
        of_iface__aggregate__id=aggregate.id)
    
    # get the set of resources openflow interfaces connect to
    types = []
    for app, model_name in getattr(settings, "OPENFLOW_OTHER_RESOURCES", []):
        app_label = app.rpartition(".")[2]
        logger.debug(
            "getting model for app %s model %s" % (app_label, model_name))
        model = cache.get_model(app_label, model_name)
        if not model:
            raise Exception(
                "Error in settings: "
                "Could not find model %s in application %s."
                % (model_name, app))
        types.append(model)
    resource_qs = Resource.objects.filter_for_classes(types)
    
    if request.method == "POST":
        new_cnxn_form = OpenFlowStaticConnectionForm(
            aggregate, request.POST)
        existing_links_form = OpenFlowConnectionSelectionForm(
            of_cnxn_qs, non_of_cnxn_qs, request.POST)
        new_other_cnxn_form = NonOpenFlowStaticConnectionForm(
            aggregate, resource_qs, request.POST)
        
        # see if it's a request to delete or add links
        if "add_links" in request.POST:
            if new_cnxn_form.is_valid():
                cnxns = new_cnxn_form.save_connections()
                if not cnxns[0] and not cnxns[1]:
                    msg = "links for both directions"
                elif not cnxns[0] or not cnxns[1]:
                    msg = "link for one direction"
                else:
                    msg = "no new links"
                DatedMessage.objects.post_message_to_user(
                    "Added %s to OpenFlow aggregate %s" % (msg, aggregate.name),
                    user=request.user, msg_type=DatedMessage.TYPE_SUCCESS)
                return HttpResponseRedirect(request.path)
            
        elif "add_other_links" in request.POST:
            if new_other_cnxn_form.is_valid():
                cnxn = new_other_cnxn_form.save()
                DatedMessage.objects.post_message_to_user(
                    "Added static connection %s to OpenFlow aggregate %s"
                        % (cnxn, aggregate.name),
                    user=request.user, msg_type=DatedMessage.TYPE_SUCCESS)
                return HttpResponseRedirect(request.path)
            
        else: # must be deleting links
            if existing_links_form.is_valid():
                cnxns = list(existing_links_form.\
                             cleaned_data["of_connections"])
                cnxns.extend(
                    list(existing_links_form.\
                         cleaned_data["non_of_connections"]))
                for c in cnxns:
                    c.delete()
                DatedMessage.objects.post_message_to_user(
                    "Deleted %s static links to OpenFlow aggregate %s" % (
                        len(cnxns), aggregate.name),
                    user=request.user, msg_type=DatedMessage.TYPE_SUCCESS)
                return HttpResponseRedirect(request.path)
    else:
        new_cnxn_form = OpenFlowStaticConnectionForm(aggregate)
        new_other_cnxn_form = NonOpenFlowStaticConnectionForm(
            aggregate, resource_qs)
        if of_cnxn_qs.count() + non_of_cnxn_qs.count():
            existing_links_form = \
                OpenFlowConnectionSelectionForm(
                    of_cnxn_qs, non_of_cnxn_qs).as_table()
        else:
            existing_links_form = None

    return simple.direct_to_template(
        request,
        template=TEMPLATE_PATH+"/aggregate_add_links.html",
        extra_context={
            "existing_links_form": existing_links_form,
            "new_connection_form": new_cnxn_form.as_table(),
            "new_other_connection_form": new_other_cnxn_form.as_table(),
            "aggregate": aggregate,
            "breadcrumbs": (
                ('Home', reverse("home")),
                ("Update OpenFlow Aggregate", reverse("openflow_aggregate_edit", args=[agg_id])),
                ("Edit Static Links", reverse("openflow_aggregate_add_links", args=[agg_id])),
            ),
        },
    )

def aggregate_add_to_slice(request, agg_id, slice_id):
    """
    Add the aggregate to the slice. Check if the slice already has
    OpenFlowSliceInfo information related to it. If there is, then reuse that.
    """
    
    aggregate = get_object_or_404(OpenFlowAggregate, id=agg_id)
    slice = get_object_or_404(Slice, id=slice_id)
    
    must_have_permission(request.user, aggregate, "can_use_aggregate")
    must_have_permission(slice.project, aggregate, "can_use_aggregate")
    
    next = request.GET.get("next", None)
    
    # check if there's info already.
    try:
        info = OpenFlowSliceInfo.objects.get(slice=slice)
    except OpenFlowSliceInfo.DoesNotExist:
        info = None
    
    id = info.id if info else None
    creating = info != None
    
    def pre_save(instance, created):
        instance.slice = slice
    
    def post_save(instance, created):
        give_permission_to("can_use_aggregate", aggregate, slice)
    
    return generic_crud(
        request, id, OpenFlowSliceInfo,
        form_class=OpenFlowSliceInfoForm,
        template=TEMPLATE_PATH+"/aggregate_add_to_slice.html",
        redirect=lambda instance: next if next else reverse(
            "slice_detail", args=[slice.id]),
        extra_context={"creating": creating,
                       "slice": slice,
                       "aggregate": aggregate},
        template_object_name="info",
        pre_save=pre_save,
        post_save=post_save,
        success_msg=lambda instance: "Successfully added OpenFlow aggregate %s to slice %s" % (aggregate.name, slice.name),
    )
