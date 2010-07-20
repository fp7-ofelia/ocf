'''
Created on Jun 19, 2010

@author: jnaous
'''
from django.views.generic import simple
from django.shortcuts import get_object_or_404
from expedient.clearinghouse.slice.models import Slice
from openflow.plugin.models import OpenFlowAggregate, OpenFlowSwitch,\
    OpenFlowInterface, OpenFlowInterfaceSliver, FlowSpaceRule,\
    OpenFlowConnection, NonOpenFlowConnection
from django.http import HttpResponseRedirect, HttpResponseNotAllowed,\
    HttpResponse
from expedient.common.messaging.models import DatedMessage
from django.forms.models import inlineformset_factory
from django.core.urlresolvers import reverse
from models import SliceFlowSpace
from geni.planetlab.models import PlanetLabNode, PlanetLabSliver,\
    PlanetLabAggregate

import logging
logger = logging.getLogger("html_ui_views")

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

def _get_nodes_links(of_aggs, pl_aggs):
    """
    Get nodes and links usable by protovis.
    """
    nodes = []
    links = []
    
    id_to_idx = {}
    agg_ids = []
    
    for i, agg in enumerate(of_aggs):
        agg_ids.append(agg.pk)
        switches = OpenFlowSwitch.objects.filter(aggregate__pk=agg.pk)
        for s in switches:
            id_to_idx[s.id] = len(nodes)
            nodes.append(dict(
                name=s.name, group=i)
            )
    
    for i, agg in enumerate(pl_aggs):
        agg_ids.append(agg.pk)
        pl_nodes = PlanetLabNode.objects.filter(aggregate__pk=agg.pk)
        for n in pl_nodes:
            id_to_idx[n.id] = len(nodes)
            nodes.append(dict(
                name=n.name, group=i+len(of_aggs))
            )
            
    # get all connections with both interfaces in wanted aggregates
    of_cnxn_qs = OpenFlowConnection.objects.filter(
        src_iface__aggregate__id__in=agg_ids,
        dst_iface__aggregate__id__in=agg_ids,
    )
    non_of_cnxn_qs = NonOpenFlowConnection.objects.filter(
        of_iface__aggregate__id__in=agg_ids,
        resource__id__in=id_to_idx.keys(),
    )
    
    for cnxn in of_cnxn_qs:
        links.append(
            dict(
                src=id_to_idx[cnxn.src_iface.switch.id],
                target=id_to_idx[cnxn.dst_iface.switch.id],
                value=1,
            )
        )
    
    for cnxn in non_of_cnxn_qs:
        links.append(
            dict(
                src=id_to_idx[cnxn.of_iface.switch.id],
                target=id_to_idx[cnxn.resource.id],
                value=1,
            )
        )
        links.append(
            dict(
                target=id_to_idx[cnxn.of_iface.switch.id],
                src=id_to_idx[cnxn.resource.id],
                value=1,
            )
        )
        
    return (nodes, links)

def home(request, slice_id):
    """
    Display the list of planetlab and openflow aggregates and their resources.
    On submit, create slivers and make reservation.
    """
    
    slice = get_object_or_404(Slice, id=slice_id)
    if request.method == "POST":
        
        _update_openflow_resources(request, slice)
        _update_planetlab_resources(request, slice)
        
        slice.modified = True
        slice.save()
        
        logger.debug("Done adding resources")
        return HttpResponseRedirect(reverse("html_plugin_flowspace",
                                            args=[slice_id]))
    else:
        checked_ids = list(slice.resource_set.filter_for_objects(
            OpenFlowInterface, slice_set=slice).values_list("id", flat=True))
        checked_ids.extend(slice.resource_set.filter_for_objects(
            PlanetLabNode, slice_set=slice).values_list("id", flat=True))
        logger.debug("Interfaces in slice: %s" % checked_ids)
        of_aggs = OpenFlowAggregate.objects.filter(slice=slice)
        pl_aggs = PlanetLabAggregate.objects.filter(slice=slice)
        protovis_nodes, protovis_links = _get_nodes_links(of_aggs, pl_aggs)
        return simple.direct_to_template(
            request,
            template="html/select_resources.html",
            extra_context={
                "protovis_nodes": protovis_nodes,
                "protovis_links": protovis_links,
                "openflow_aggs": of_aggs,
                "planetlab_aggs": pl_aggs,
                "slice": slice,
                "checked_ids": checked_ids,
                "ofswitch_class": OpenFlowSwitch,
                "planetlab_node_class": PlanetLabNode,
                "breadcrumbs": (
                    ("Home", reverse("home")),
                    ("Project %s" % slice.project.name, reverse("project_detail", args=[slice.project.id])),
                    ("Slice %s" % slice.name, reverse("slice_detail", args=[slice_id])),
                    ("HTML UI - Choose Resources", reverse("html_plugin_home", args=[slice_id])),
                )
            },
        )
        
def flowspace(request, slice_id):
    """
    Add flowspace.
    """
    slice = get_object_or_404(Slice, id=slice_id)
    
    slivers = OpenFlowInterfaceSliver.objects.filter(slice=slice)
    
    # create a formset to handle all flowspaces
    FSFormSet = inlineformset_factory(Slice, SliceFlowSpace)
    if request.method == "POST":
        logger.debug("Got post for flowspace")
        formset = FSFormSet(request.POST, instance=slice)
        if formset.is_valid():
            logger.debug("Flowspace valid")
            formset = formset.save()
            
            # Update the Flowspace for the slivers
            for fs in FlowSpaceRule.objects.filter(sliver__slice=slice):
                fs.delete()
                
            slivers = OpenFlowInterfaceSliver.objects.filter(slice=slice)
            for fs in SliceFlowSpace.objects.filter(slice=slice):
                # get the wanted attributes into a dict
                d = {}
                for f in SliceFlowSpace._meta.fields:
                    logger.debug("Doing field %s" % f.name)
                    if f.name != "slice" and f.name != "id":
                        val = getattr(fs, f.name)
                        if val == None or val == "": val = "*"
                        d[f.name+"_start"] = "%s" % val
                        d[f.name+"_end"] = "%s" % val
                        
                logger.debug("Saved flowspace %s" % d)
                # now create fs for all the slivers
                for s in slivers:
                    d["sliver"] = s
                    FlowSpaceRule.objects.create(**d)
            
            DatedMessage.objects.post_message_to_user(
                "Successfully set flowspace for slice %s" % slice.name,
                request.user, msg_type=DatedMessage.TYPE_SUCCESS,
            )
            
            slice.modified = True
            slice.save()
        
            return HttpResponseRedirect(request.path)
        else:
            logger.debug("Flowspace invalid: %s" % formset)
    
    elif request.method == "GET":
        formset = FSFormSet(instance=slice)
    
    else:
        return HttpResponseNotAllowed("GET", "POST")
        
    return simple.direct_to_template(
        request,
        template="html/select_flowspace.html",
        extra_context={
            "slice": slice,
            "fsformset": formset,
            "breadcrumbs": (
                ("Home", reverse("home")),
                ("Project %s" % slice.project.name, reverse("project_detail", args=[slice.project.id])),
                ("Slice %s" % slice.name, reverse("slice_detail", args=[slice_id])),
                ("HTML UI - Choose Resources", reverse("html_plugin_home", args=[slice_id])),
                ("HTML UI - Choose Flowspace", reverse("html_plugin_flowspace", args=[slice_id])),
            ),
        },
    )

def sshkeys(request, slice_id):
    """
    Show links to download ssh keys. Regenerate keys on submit.
    """
    slice = get_object_or_404(Slice, id=slice_id)
    
    if request.method == "POST":
        slice.geni_slice_info.generate_ssh_keys()
        slice.geni_slice_info.save()
        slice.modified = True
        slice.save()
        return HttpResponseRedirect(request.path)
    
    return simple.direct_to_template(
        request,
        template="html/sshkeys.html",
        extra_context={
            "slice":slice,
            "breadcrumbs": (
                ("Home", reverse("home")),
                ("Project %s" % slice.project.name, reverse("project_detail", args=[slice.project.id])),
                ("Slice %s" % slice.name, reverse("slice_detail", args=[slice_id])),
                ("HTML UI - Choose Resources", reverse("html_plugin_home", args=[slice_id])),
                ("HTML UI - Choose Flowspace", reverse("html_plugin_flowspace", args=[slice_id])),
                ("HTML UI - Download SSH Keys", reverse("html_plugin_sshkeys", args=[slice_id])),
            ),
        }
    )

def sshkey_file(request, slice_id, type):
    """
    Send a file.
    """
    slice = get_object_or_404(Slice, id=slice_id)
    if type != "ssh_public_key" and type != "ssh_private_key":
        raise Exception("Unknown request for file %s" % type)
    
    data = getattr(slice.geni_slice_info, type)
    
    filename = "id_rsa"
    if type == "ssh_public_key": filename = filename + ".pub"
    
    response = HttpResponse(data, mimetype="application/x-download")
    response["Content-Disposition"] = 'attachment;filename=%s' % filename
    return response
