'''
@author: jnaous
'''
from django.views.generic import simple, create_update
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.db import transaction
from expedient.clearinghouse.slice.models import Slice
from expedient.common.messaging.models import DatedMessage
from expedient.common.utils.views import generic_crud
from expedient.common.xmlrpc_serverproxy.forms import PasswordXMLRPCServerProxyForm
from models import OpenFlowAggregate, OpenFlowSliceInfo
from forms import OpenFlowAggregateForm, OpenFlowSliceInfoForm
import logging
from django.forms.models import modelformset_factory
from openflow.plugin.models import OpenFlowConnection
from django.db.models import Q
from openflow.plugin.forms import OpenFlowStaticConnectionForm,\
    OpenFlowConnectionSelectionForm

logger = logging.getLogger("OpenFlow plugin views")
TEMPLATE_PATH = "openflow/plugin"

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
        aggregate = aggregate or OpenFlowAggregate(owner=request.user)
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
                ("%s OpenFlow Aggregate" % "Update" if agg_id else "Add",
                 request.path),
            )
        },
    )
    
def aggregate_add_links(request, agg_id):
    """
    Show page to add static connections to other aggregates.
    """
    aggregate = get_object_or_404(OpenFlowAggregate, id=agg_id)
    
    filter = (
        (     Q(src_iface__aggregate__id=aggregate.id)
              & ~Q(dst_iface__aggregate__id=aggregate.id)  )
        |
        (     Q(dst_iface__aggregate__id=aggregate.id)
              & ~Q(src_iface__aggregate__id=aggregate.id)  )
    )
    
    existing_links = OpenFlowConnection.objects.filter(filter)
    
    if request.method == "POST":
        new_cnxn_form = OpenFlowStaticConnectionForm(aggregate, request.POST)
        existing_links_form = OpenFlowConnectionSelectionForm(existing_links, request.POST)
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
                    "Added %s to OpenFlow aggregate %s" % (aggregate.name, msg),
                    user=request.user, msg_type=DatedMessage.TYPE_SUCCESS)
                return HttpResponseRedirect(request.path)
        else: # must be deleting links
            if existing_links_form.is_valid():
                cnxns = existing_links_form.cleaned_data["connections"]
                for c in cnxns:
                    c.delete()
                DatedMessage.objects.post_message_to_user(
                    "Deleted %s static links to OpenFlow aggregate %s" % (
                        len(cnxns), aggregate.name),
                    user=request.user, msg_type=DatedMessage.TYPE_SUCCESS)
                return HttpResponseRedirect(request.path)
    else:
        new_cnxn_form = OpenFlowStaticConnectionForm(aggregate)
        if existing_links.count():
            existing_links_form = \
                OpenFlowConnectionSelectionForm(existing_links)
        else:
            existing_links_form = None
        logger.debug("new connection form: %s" % new_cnxn_form)
    
    return simple.direct_to_template(
        request,
        template=TEMPLATE_PATH+"/aggregate_add_links.html",
        extra_context={
            "existing_links_form": existing_links_form,
            "new_connection_form": new_cnxn_form,
            "aggregate": aggregate,
            "breadcrumbs": (
                ('Home', reverse("home")),
                ("Update OpenFlow Aggregate", reverse("openflow_aggregate_edit", args=[agg_id])),
                ("Edit Static Links", reverse("openflow_aggregate_add_links", args=[agg_id])),
            ),
        },
    )
    
def aggregate_delete(request, agg_id):
    """
    Delete an aggregate.
    """
    aggregate = get_object_or_404(OpenFlowAggregate, id=agg_id)
    req = create_update.delete_object(
        request,
        OpenFlowAggregate,
        reverse("aggregate_all"),
        agg_id,
        template_name=TEMPLATE_PATH+"/aggregate_confirm_delete.html",
    )
    if req.status_code == HttpResponseRedirect.status_code:
        DatedMessage.objects.post_message_to_user(
            "Successfully deleted aggregate %s" % aggregate.name,
            request.user, msg_type=DatedMessage.TYPE_ERROR,
        )
    return req

def aggregate_add_to_slice(request, agg_id, slice_id):
    """
    Add the aggregate to the slice. Check if the slice already has
    OpenFlowSliceInfo information related to it. If there is, then reuse that.
    """
    
    aggregate = get_object_or_404(OpenFlowAggregate, id=agg_id)
    slice = get_object_or_404(Slice, id=slice_id)
    
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
        slice.aggregates.add(aggregate)
    
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
