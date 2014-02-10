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
from django import forms
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

from openflow.plugin.vlans import *
from openflow.plugin.models import OpenFlowAggregate, OpenFlowSwitch,\
    OpenFlowInterface, OpenFlowInterfaceSliver, FlowSpaceRule,\
    OpenFlowConnection, NonOpenFlowConnection
from expedient_geni.planetlab.models import PlanetLabNode, PlanetLabSliver,\
    PlanetLabAggregate

from expedient.common.utils.plugins.resources.node import Node
from expedient.common.utils.plugins.resources.link import Link

logger = logging.getLogger("OpenFlow plugin views")

@require_objs_permissions_for_view(
    perm_names=["can_add_aggregate"],
    permittee_func=get_user_from_req,
    target_func=get_queryset_from_class(Aggregate),
    methods=["POST", "GET"])
def aggregate_create(request):
    return aggregate_crud(request)

@require_objs_permissions_for_view(
    perm_names=["can_edit_aggregate"],
    permittee_func=get_user_from_req,
    target_func=get_queryset(OpenFlowAggregate, "agg_id"),
    methods=["POST", "GET"])
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
            try:
                err = ' '
                aggregate.client.proxy.checkFlowVisor() 
                aggregate.setup_new_aggregate(request.build_absolute_uri("/"))
            except Exception as e:
                 err = str(e)
            if err is not ' ':
                #transaction.rollback()
                if "check_fv_set" in err:
                    msg_type = DatedMessage.TYPE_WARNING
                    if agg_id:
                        flowvisor_msg = "Topology could not be updated because could not connect to FlowVisor."
                    else:
                        flowvisor_msg = "New Aggregate set, but there is no FlowVisor connected to it."
                else:
                    flowvisor_msg = err
                    msg_type = DatedMessage.TYPE_ERROR
                DatedMessage.objects.post_message_to_user(
                    flowvisor_msg, user=request.user, msg_type=msg_type,
                )
                return HttpResponseRedirect("/")
            aggregate.save()
            give_permission_to(
                "can_use_aggregate",
                aggregate,
                request.user,
                can_delegate=True
            )
            give_permission_to(
                "can_edit_aggregate",
                aggregate,
                request.user,
                can_delegate=True
            )
            DatedMessage.objects.post_message_to_user(
                "Successfully created/updated aggregate %s. %s" % (aggregate.name,err),
                user=request.user, msg_type=DatedMessage.TYPE_SUCCESS,
            )
            return HttpResponseRedirect(reverse("openflow_aggregate_add_links", args=[aggregate.id]))
        logger.debug("Validation failed")
    else:
        return HttpResponseNotAllowed("GET", "POST")
    
    available = aggregate.check_status() if agg_id else False
    return simple.direct_to_template(
        request,
        template="openflow_aggregate_crud.html",
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
    
def aggregate_add_links(request, agg_id):
    """
    Show page to add static connections to other aggregates.
    """
    aggregate = get_object_or_404(OpenFlowAggregate, id=agg_id)
    
    return handle_add_links(
        request, aggregate,
        extra_context={
            "breadcrumbs": (
                ('Home', reverse("home")),
                ("Update OpenFlow Aggregate", reverse("openflow_aggregate_edit", args=[agg_id])),
                ("Edit Static Links", reverse("openflow_aggregate_add_links", args=[agg_id])),
            ),
        }
    )
    
def handle_add_links(request, aggregate,
                     template="openflow_aggregate_add_links.html",
                     extra_context={}):
    """Perform the actual request."""

    must_have_permission(
        request.user, aggregate, "can_edit_aggregate")
    
    # Get the queryset of all openflow connections to/from this aggregate
    of_iface_filter = (
        (     Q(src_iface__aggregate__id=aggregate.id)
              & ~Q(dst_iface__aggregate__id=aggregate.id)  )
        |
        (     Q(dst_iface__aggregate__id=aggregate.id)
              & ~Q(src_iface__aggregate__id=aggregate.id)  )
    )
    of_cnxn_qs = OpenFlowConnection.objects.filter(
        of_iface_filter).filter(
            src_iface__available=True, dst_iface__available=True)

    # Get the queryset of all non-openflow connections to aggregate
    non_of_cnxn_qs = NonOpenFlowConnection.objects.filter(
        of_iface__aggregate__id=aggregate.id,
        of_iface__available=True,
    )
    
    # get the set of resources openflow interfaces connect to
    types = []
    for app, model_name in getattr(settings, "OPENFLOW_OTHER_RESOURCES", []):
        app_label = app.rpartition(".")[2]
#        logger.debug(
#            "getting model for app %s model %s" % (app_label, model_name))
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
                    "Added static connection %s" % cnxn,
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

    ctx = {
        "existing_links_form": existing_links_form,
        "new_connection_form": new_cnxn_form.as_table(),
        "new_other_connection_form": new_other_cnxn_form.as_table(),
        "aggregate": aggregate,
    }
    ctx.update(**extra_context)
    return simple.direct_to_template(
        request,
        template=template,
        extra_context=ctx,
    )

def aggregate_add_to_slice(request, agg_id, slice_id):
    """
    Add the aggregate to the slice. Check if the slice already has
    OpenFlowSliceInfo information related to it. If there is, then reuse that.
    """
    
    aggregate = get_object_or_404(OpenFlowAggregate, id=agg_id)
    slice = get_object_or_404(Slice, id=slice_id)
    
    return handle_add_to_slice(request, aggregate, slice)
    
def handle_add_to_slice(request, aggregate, slice):
    """Perform that actual add_to_slice request."""
    
    must_have_permission(request.user, aggregate, "can_use_aggregate")
    must_have_permission(slice.project, aggregate, "can_use_aggregate")
    
    next = request.GET.get("next", None)
    
    give_permission_to("can_use_aggregate", aggregate, slice)

    #success_msg=lambda instance: "Successfully added OpenFlow aggregate %s to slice %s" % (aggregate.name, slice.name)    
    return HttpResponseRedirect(next if next else reverse("slice_detail", args=[slice.id])) 

def add_controller_to_slice(request, agg_id, slice_id):
    """Perform the actual add_controllr_to_slice request."""
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
        # Leo added this. Probably due to issue #121 (allow updating
        # (the slice controller without having to start/update it)
        if not created:
            try:
                #aggregate.change_slice_controller(slice)
                for agg in Aggregate.objects.all():
                    agg = agg.as_leaf_class()
                    if agg.leaf_name == "OpenFlowAggregate":
                        agg.change_slice_controller(slice)
            except Exception,e:
                error_msg = str(e)
                print e
    return generic_crud(
        request, id, OpenFlowSliceInfo,
        form_class=OpenFlowSliceInfoForm,
        template="openflow_aggregate_add_to_slice.html",
        redirect=lambda instance: next if next else reverse(
            "slice_detail", args=[slice.id]),
        extra_context={"creating": creating,
                       "slice": slice,
                       "aggregate": aggregate},
        template_object_name="info",
        pre_save=pre_save,
        post_save=post_save,
        success_msg=lambda instance: "Successfully added OpenFlow controller to slice %s" % (slice.name),
    )

def book_openflow(request, slice_id):
    """
    Display the list of planetlab and openflow aggregates and their resources.
    On submit, create slivers and make reservation.
    """

    slice = get_object_or_404(Slice, id=slice_id)
    enable_simple_mode = not check_existing_flowspace_in_slice(slice)

    if request.method == "POST":
        _update_openflow_resources(request, slice)
        _update_planetlab_resources(request, slice)

        slice.modified = True
        slice.save()
        free_vlan = 'None'
        alertMessage = ''

        fsmode = request.POST['fsmode']
        if fsmode == 'simple' and enable_simple_mode:
            try:
                free_vlan = calculate_free_vlan(slice)
            except Exception as e:
                fsmode = 'failed'
                DatedMessage.objects.post_message_to_user(
                         "Could not find free vlan to slice your experiment in all the affected AMs",
                         request.user, msg_type=DatedMessage.TYPE_ERROR,
                     )
                alertMessage = "Could not find free vlan to slice your experiment in all the affected AMs. It has been switched to advanced mode, choose your flowspace and wait for the admins decision."
  
            return flowspace(request, slice_id, fsmode, free_vlan, alertMessage)
        else:
            return HttpResponseRedirect(reverse("flowspace",
                                            args=[slice_id]))
    else:
        ui_extra_context = {
            "slice": slice,
            "enable_simple_mode":enable_simple_mode,
            "breadcrumbs": (
                ("Home", reverse("home")),
                ("Project %s" % slice.project.name, reverse("project_detail", args=[slice.project.id])),
                ("Slice %s" % slice.name, reverse("slice_detail", args=[slice_id])),
                ("Allocate Openflow and PlanetLab resources", reverse("book_openflow", args=[slice_id])),
            )
        }

        # Need to show topology for own plugin? Call to main method to get EVERY resource
        from expedient.clearinghouse.urls import TOPOLOGY_GENERATOR
        return simple.direct_to_template(
            request,
            template = "openflow_select_resources.html",
            # TopologyGenerator class instance
            extra_context = dict(TOPOLOGY_GENERATOR.load_ui_data(slice).items() + ui_extra_context.items()),
        )

def flowspace(request, slice_id, fsmode = 'advanced', free_vlan = None, alertMessage=""):
    """
    Add flowspace.
    """
    slice = get_object_or_404(Slice, id=slice_id)

    class SliverMultipleChoiceField(forms.ModelMultipleChoiceField):
        def label_from_instance(self, obj):
            return "%s" % obj.resource.as_leaf_class()

        def widget_attrs(self, widget):
            return {"class": "wide"}

    def formfield_callback(f):
        if f.name == "slivers":
            return SliverMultipleChoiceField(
                queryset=OpenFlowInterfaceSliver.objects.filter(slice=slice))
        else:
            return f.formfield()

    # create a formset to handle all flowspaces
    FSFormSet = forms.models.modelformset_factory(
        model=FlowSpaceRule,
        formfield_callback=formfield_callback,
        can_delete=True,
        extra=0, # No extra forms apart from the one being shown
#        extra=2,
    )

    if request.method == "POST":
        continue_to_start_slice = False
        # Default formset
        formset = FSFormSet(
            queryset=FlowSpaceRule.objects.filter(
                slivers__slice=slice).distinct(),
        )
        if formset.is_valid():
            formset.save()

        if fsmode == 'advanced':
            formset = FSFormSet(
                request.POST,
                queryset=FlowSpaceRule.objects.filter(
                    slivers__slice=slice).distinct(),
            )
            if formset.is_valid():
                formset.save()
                continue_to_start_slice = True
        elif fsmode == 'simple':
            #create a simple flowspacerule containing only the vlans tags and the OF ports
            try:
                create_simple_slice_vlan_based(free_vlan[0], slice)
                continue_to_start_slice = True
            except:
                #continue_to_start_slice flag will deal with this
                pass

        if continue_to_start_slice:
            slice.modified = True
            slice.save()
            exp=""
            try:
                if slice.started:
                    #slice.stop(request.user)
                    slice.start(request.user)
            except Exception as e:
                exp=str(e)
            finally:
                if exp:
                     DatedMessage.objects.post_message_to_user(
                         "Successfully set flowspace for slice %s,  but the following warning was raised: \"%s\". You may still need to start/update your slice after solving the problem." % (slice.name, exp),
                         request.user, msg_type=DatedMessage.TYPE_WARNING,
                     )
                else:
                    DatedMessage.objects.post_message_to_user(
                        "Successfully set flowspace for slice %s" % slice.name,
                        request.user, msg_type=DatedMessage.TYPE_SUCCESS,
                    )
            if fsmode == 'simple':
                return HttpResponseRedirect(reverse("slice_detail", args=[slice_id]))
            else:
                return HttpResponseRedirect(request.path)

    elif request.method == "GET":
        flowspace_form_contents = FlowSpaceRule.objects.filter(slivers__slice=slice).distinct()
        flowspace_form_number = 1

        # When coming from the OpenFlow switches topology selection page...
        if "HTTP_REFERER" in request.META:
            # Checks if the referer page is the topology selcetion
            if reverse("book_openflow", args=[slice_id]) in request.META['HTTP_REFERER']:
                # If no flowspace has been selected yet, show an extra form to allow user to choose at least one
                if not flowspace_form_contents:
                    flowspace_form_number = 1 # Show an extra (1) form besides the already selected one
                # Otherwise, when there is some already requested flowspace, show only the requested ones (no extra forms)
                else:
                    flowspace_form_number = 0 # No extra forms apart from the one(s) being shown
        
        # Redefine formset to handle all flowspaces
        # Extra: field that determines how many extra flowspaces there are
        FSFormSet = forms.models.modelformset_factory(
            model=FlowSpaceRule,
            formfield_callback=formfield_callback,
            can_delete=True,
            extra=flowspace_form_number, # Show numbe of forms according to origin path request and so on
        )
        formset = FSFormSet(
            queryset=flowspace_form_contents,
        )

    else:
        return HttpResponseNotAllowed("GET", "POST")

    done = PlanetLabSliver.objects.filter(slice=slice).count() == 0

    return simple.direct_to_template(
        request,
        template="openflow_select_flowspace.html",
        extra_context={
            "slice": slice,
            "fsformset": formset,
            "alertMessage":alertMessage,
            "done": done,
            "breadcrumbs": (
                ("Home", reverse("home")),
                ("Project %s" % slice.project.name, reverse("project_detail", args=[slice.project.id])),
                ("Slice %s" % slice.name, reverse("slice_detail", args=[slice_id])),
                ("Choose Flowspace", reverse("flowspace", args=[slice_id])),
            ),
        },
    )

def save_flowspace(request, slice_id):
    """
    Saves flowspace and gets back to slice detail page.
    """
    if request.method == "POST":
        slice = get_object_or_404(Slice, id=slice_id)
        
        class SliverMultipleChoiceField(forms.ModelMultipleChoiceField):
            def label_from_instance(self, obj):
                return "%s" % obj.resource.as_leaf_class()
            
            def widget_attrs(self, widget):
                return {"class": "wide"}
            
        def formfield_callback(f):
            if f.name == "slivers":
                return SliverMultipleChoiceField(
                    queryset=OpenFlowInterfaceSliver.objects.filter(slice=slice))
            else:
                return f.formfield()
        
        # create a formset to handle all flowspaces
        FSFormSet = forms.models.modelformset_factory(
            model=FlowSpaceRule,
            formfield_callback=formfield_callback,
            can_delete=True,
            extra=0, # No extra forms apart from the one being shown
        )
        
        formset = FSFormSet(
            request.POST,
            queryset=FlowSpaceRule.objects.filter(
                slivers__slice=slice).distinct(),
        )
        if formset.is_valid():
            formset.save()
        
        return HttpResponseRedirect(reverse("slice_detail", args=[slice_id]))
    else:
        return HttpResponseNotAllowed("POST")


'''
Update resources
'''

def _update_openflow_resources(request, slice):
    """
    Process the request to add/remove openflow resources from slice.
    """
    iface_ids = map(int, request.POST.getlist("selected_ifaces"))
    ifaces = OpenFlowInterface.objects.filter(id__in=iface_ids)
    # TODO: Send message if id not found.
    # get or create slivers for the ifaces in the slice.
    for iface in ifaces:
        # make sure all the selected interfaces are added
        sliver, created = OpenFlowInterfaceSliver.objects.get_or_create(
            slice=slice, resource=iface)
        if created:
            DatedMessage.objects.post_message_to_user(
                "Successfully added interface %s to slice %s" % (
                    iface, slice.name),
                request.user, msg_type=DatedMessage.TYPE_SUCCESS)
    # Delete all unselected interfaces
    to_del = OpenFlowInterfaceSliver.objects.exclude(
        resource__id__in=iface_ids).filter(slice=slice)
    to_del.delete()

def _update_planetlab_resources(request, slice):
    """
    Process the request to add/remove planetlab resources from slice.
    """
    node_ids = map(int, request.POST.getlist("selected_nodes"))
    nodes = PlanetLabNode.objects.filter(id__in=node_ids)
    # TODO: Send message if id not found.
    # get or create slivers for the nodes in the slice.
    for node in nodes:
        # make sure all the selected interfaces are added
        sliver, created = PlanetLabSliver.objects.get_or_create(
            slice=slice, resource=node)
        if created:
            DatedMessage.objects.post_message_to_user(
                "Successfully added %s to slice %s" % (
                    node, slice.name),
                request.user, msg_type=DatedMessage.TYPE_SUCCESS)
    # Delete all unselected interfaces
    to_del = PlanetLabSliver.objects.exclude(
        resource__id__in=node_ids).filter(slice=slice)
    to_del.delete()

###
# Topology to show in the Expedient
#

def get_checked_ids(slice):
    checked_ids = []
    try:
        checked_ids = list(OpenFlowInterface.objects.filter(
            slice_set=slice).values_list("id", flat=True))
        checked_ids.extend(PlanetLabNode.objects.filter(
            slice_set=slice).values_list("id", flat=True))
    except:
        pass
    return checked_ids

def get_controller_url(slice):
    try:
        controller_url = OpenFlowSliceInfo.objects.get(slice=slice).controller_url
    except:
        controller_url= "Not set"
    return controller_url

def get_openflow_aggregates(slice):
    aggs_filter = (Q(leaf_name=OpenFlowAggregate.__name__.lower()) |
                       Q(leaf_name=GCFOpenFlowAggregate.__name__.lower()))
    # Avoid non-available OF AMs
#    aggs_filter_available = ((Q(leaf_name=OpenFlowAggregate.__name__.lower()) & Q(available = True)) |
#                    (Q(leaf_name=GCFOpenFlowAggregate.__name__.lower()) & Q(available = True)))
    return slice.aggregates.filter(aggs_filter)

def get_planetlab_aggregates(slice):
    return slice.aggregates.filter(leaf_name=PlanetLabAggregate.__name__.lower())

def get_gfs(slice):
    gfs_list=[]
    try:
        of_aggs = get_openflow_aggregates(slice)
        for of_agg in of_aggs:
            # Checks that each OF AM is available prior to ask for granted flowspaces
            if of_agg.available:
                gfs = of_agg.as_leaf_class().get_granted_flowspace(of_agg.as_leaf_class()._get_slice_id(slice))
                gfs_list.append([of_agg.id,gfs])
    except:
        pass
    return gfs_list

def get_node_description(node):
    description = "<strong>Switch Datapath ID: " + node.name + "</strong><br/><br/>"
    if len(node.connection):
        description += "<strong>Connections:</strong><br/>"
        for connection in node.connection:
            description += "<strong>&#149; Port " + connection['src_port'] + "</strong> to Switch " + connection['target_datapath'] + " at port " + connection['target_port']+"<br/>";
    return description

def get_nodes_links(slice):
    nodes = []
    links = []

    id_to_idx = {}
    agg_ids = []

    of_aggs = get_openflow_aggregates(slice)
    pl_aggs = get_planetlab_aggregates(slice)

    # Getting image for the nodes
    try:
        image_url = reverse('img_media_openflow', args=("switch-tiny.png",))
    except:
        image_url = 'switch-tiny.png'

    #Openflow devices
    for i, agg in enumerate(of_aggs):
        agg_ids.append(agg.pk)
        switches = OpenFlowSwitch.objects.filter(
            aggregate__pk=agg.pk,
            available=True,
        )
        for s in switches:
            id_to_idx[s.id] = len(nodes)
            nodes.append(Node(name = s.name, value = s.id, description = "", type = "OpenFlow switch",
                              image = image_url, aggregate = agg,
                              # Extra paramaters for OpenFlow nodes
                              connection = []
                              )
                        )

    # Getting image for the nodes
    try:
        image_url = reverse('img_media_vt_plugin', args=("host-tiny.png",))
    except:
        image_url = 'host-tiny.png'

    #Planelab nodes 
    for i, agg in enumerate(pl_aggs):
        agg_ids.append(agg.pk)
        pl_nodes = PlanetLabNode.objects.filter(
            aggregate__pk=agg.pk,
            available=True,
        )
        for n in pl_nodes:
            id_to_idx[n.id] = len(nodes)
            nodes.append(Node(name = s.name, value = s.id, description = "", type = "PlanetLab node",
                              image = image_url, aggregate = agg
                             )
                        )

    # get all connections with both interfaces in wanted aggregates
    of_cnxn_qs = OpenFlowConnection.objects.filter(
        src_iface__aggregate__id__in=agg_ids,
        src_iface__available=True,
        dst_iface__aggregate__id__in=agg_ids,
        dst_iface__available=True,
    )

    non_of_cnxn_qs = NonOpenFlowConnection.objects.filter(
        of_iface__aggregate__id__in=agg_ids,
        resource__id__in=id_to_idx.keys(),
        of_iface__available=True,
        resource__available=True,
    )

    sliceUUID = Slice.objects.get(id=slice.id).uuid
    for node in nodes:
        try:
           for cnxn in of_cnxn_qs:
               cnx_exists=False
               if node.value == cnxn.src_iface.switch.id:
                   for old_cnx in node.connection:
                       if (old_cnx["target_datapath"] == str(cnxn.dst_iface.switch.datapath_id) and old_cnx["target_port"] == str(cnxn.dst_iface.port_num)) :
                           cnx_exists=True
                           break
                   if not cnx_exists:
                       node.connection.append(dict(
                       src_port = str(cnxn.src_iface.port_num),
                       target_port =  str(cnxn.dst_iface.port_num),
                       target_datapath = str(cnxn.dst_iface.switch.datapath_id)))
               elif node.value == cnxn.dst_iface.switch.id:
                   for old_cnx in node.connection:
                       if (old_cnx["target_datapath"] == str(cnxn.src_iface.switch.datapath_id) and old_cnx["target_port"] == str(cnxn.src_iface.port_num)):
                          cnx_exists=True
                          break
                   if not cnx_exists :
                       node.connection.append(dict(
                       target_port = str(cnxn.src_iface.port_num),
                       src_port = str(cnxn.dst_iface.port_num),
                       target_datapath = str(cnxn.src_iface.switch.datapath_id)))
           # Add description for every node
           node.description = get_node_description(node)
        except Exception as e:
            print "[WARNING] Could not set description for nodes within plugin 'openflow'. Details: %s" % str(e)

    for cnxn in of_cnxn_qs:
        try:
            links.append(Link(source = str(cnxn.src_iface.switch.id), target = str(cnxn.dst_iface.switch.id),
                             value = "rsc_id_%s-rsc_id_%s" % (cnxn.src_iface.id, cnxn.dst_iface.id)
                             )
                        )
        except:
            pass
    for cnxn in non_of_cnxn_qs:
        # Two-way link
        links.append(Link(source = str(cnxn.of_iface.switch.id), target = str(cnxn.resource.id),
                         value = "rsc_id_%s-rsc_id_%s" % (cnxn.of_iface.id, cnxn.resource.id)
                         )
                    )
        links.append(Link(source = str(cnxn.resource.id), target = str(cnxn.of_iface.switch.id),
                         value = "rsc_id_%s-rsc_id_%s" % (cnxn.resource.id, cnxn.of_iface.id)
                         )
                    )
    return [nodes, links]

def get_tree_ports(of_aggs, pl_aggs):
    """Implements Kruskal's algorihm to find a min spanning tree"""

    # Set of interfaces in the tree
    tree = set()

    # Clusters is a mapping from a node id to the cluster
    # of ids it is connected to given the connections found
    # so far in the tree.
    clusters = {}

    # aggregate ids
    of_agg_ids = of_aggs.values_list("id", flat=True)
    pl_agg_ids = pl_aggs.values_list("id", flat=True)

    # Get the set of all openflow connections in network
    of_cnxn_qs = OpenFlowConnection.objects.filter(
        src_iface__aggregate__id__in=of_agg_ids,
        src_iface__available=True,
        dst_iface__aggregate__id__in=of_agg_ids,
        dst_iface__available=True,
    )

    # For each connection in the network
    for cnxn in of_cnxn_qs:
        # check if the endpoints' switches are in the same cluster
        a = cnxn.src_iface.switch.id
        b = cnxn.dst_iface.switch.id
        if a in clusters and b in clusters and clusters[a] == clusters[b]:
            continue
        # if not, then add the connection to the tree
        tree.add(cnxn.src_iface.id)
        tree.add(cnxn.dst_iface.id)
        if a not in clusters:
            clusters[a] = set([a])
        if b not in clusters:
            clusters[b] = set([b])

        # merge the two clusters together
        merged_cluster = clusters[a] | clusters[b]

        for x in merged_cluster:
            clusters[x] = merged_cluster

    # get the set of non openflow connections in the aggregates
    non_of_cnxn_qs = NonOpenFlowConnection.objects.filter(
        of_iface__aggregate__id__in=of_agg_ids,
        of_iface__available=True,
        resource__aggregate__id__in=pl_agg_ids,
        resource__available=True,
    )

    # add the ports that are connected to the planetlab nodes
    iface_ids = list(non_of_cnxn_qs.values_list("of_iface__id", flat=True))
    tree.update(iface_ids)
    tree.update(
        PlanetLabNode.objects.filter(
            aggregate__id__in=pl_agg_ids,
            available=True,
        ).values_list("id", flat=True),
    )

    # return the list of interface ids
    return list(tree)

def get_ui_data(slice):
    """
    Hook method. Use this very same name so Expedient can get the resources for every plugin.
    """
    ui_context = dict()
    try:
        ui_context['checked_ids'] = get_checked_ids(slice)
        ui_context['controller_url'] = get_controller_url(slice)
        ui_context['allfs'] = FlowSpaceRule.objects.filter(slivers__slice=slice).distinct().order_by('id')
        ui_context['planetlab_aggs'] = get_planetlab_aggregates(slice)
        ui_context['openflow_aggs'] = get_openflow_aggregates(slice)
        ui_context['gfs_list'] = get_gfs(slice)
        ui_context['ofswitch_class'] = OpenFlowSwitch
        ui_context['planetlab_node_class'] = PlanetLabNode
        ui_context['tree_rsc_ids'] = get_tree_ports(ui_context['openflow_aggs'], ui_context['planetlab_aggs'])
        ui_context['nodes'], ui_context['links'] = get_nodes_links(slice)
    except Exception as e:
        print "[ERROR] Problem loading UI data for plugin 'openflow'. Details: %s" % str(e)
    return ui_context

