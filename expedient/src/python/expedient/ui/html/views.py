'''
Created on Jun 19, 2010

@author: jnaous
'''
import logging
from pprint import pformat
from django.views.generic import simple
from django.shortcuts import get_object_or_404
from expedient.clearinghouse.slice.models import Slice
from expedient.clearinghouse.project.models import Project
from openflow.plugin.models import OpenFlowAggregate, OpenFlowSwitch,\
    OpenFlowInterface, OpenFlowInterfaceSliver, FlowSpaceRule,\
    OpenFlowConnection, NonOpenFlowConnection
from django.http import HttpResponseRedirect, HttpResponseNotAllowed,\
    HttpResponse
from expedient.common.messaging.models import DatedMessage
from django.forms.models import modelformset_factory
from django.core.urlresolvers import reverse
from expedient_geni.planetlab.models import PlanetLabNode, PlanetLabSliver,\
    PlanetLabAggregate
from django import forms
from django.db.models import Q
from expedient_geni.gopenflow.models import GCFOpenFlowAggregate
from vt_plugin.models import resourcesHash

#VT_PLUGIN
from vt_plugin.models import VtPlugin, VTServer, VM, Action
from vt_plugin.controller.vtAggregateController.vtAggregateController import askForAggregateResources
from vt_plugin.utils.Translator import Translator
import xmlrpclib, uuid, copy
from vt_plugin.utils.ServiceThread import *
from vt_plugin.controller.dispatchers.ProvisioningDispatcher import *
import json

logger = logging.getLogger("html_ui_views")

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



'''
Node and links functions 
'''

def _get_nodes_links(of_aggs, pl_aggs,vt_aggs):
    """
    Get nodes and links usable by protovis.
    """
    nodes = []
    links = []

    id_to_idx = {}
    agg_ids = []
   
    #Openflow devices
    #XXX: botch
    openflowSwitches = dict() 
    for i, agg in enumerate(of_aggs):
        agg_ids.append(agg.pk)
        switches = OpenFlowSwitch.objects.filter(
            aggregate__pk=agg.pk,
            available=True,
        )
        for s in switches:
            id_to_idx[s.id] = len(nodes)
            nodes.append(dict( 
                name=s.name, value=s.id, group=i, type="of_agg", connection=[])
            )
	    openflowSwitches[s.datapath_id] = len(nodes)-1
    
    #Planelab nodes 
    for i, agg in enumerate(pl_aggs):
        agg_ids.append(agg.pk)
        pl_nodes = PlanetLabNode.objects.filter(
            aggregate__pk=agg.pk,
            available=True,
        )
        for n in pl_nodes:
            id_to_idx[n.id] = len(nodes)
            nodes.append(dict(
                name=n.name, value=n.id, group=i+len(of_aggs), type="pl_agg" )
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
    
    for node in nodes:
        try:
           for cnxn in of_cnxn_qs:
               cnx_exists=False
               if node["value"] == cnxn.src_iface.switch.id:
                   for old_cnx in node["connection"]:
                       if (old_cnx["target_datapath"] == str(cnxn.dst_iface.switch.datapath_id) and old_cnx["target_port"] == str(cnxn.dst_iface.port_num)) :
                           cnx_exists=True
                           break
                   if not cnx_exists:
                       node["connection"].append(dict(
                       src_port = str(cnxn.src_iface.port_num),
                       target_port =  str(cnxn.dst_iface.port_num),
                       target_datapath = str(cnxn.dst_iface.switch.datapath_id)))
               elif node["value"] == cnxn.dst_iface.switch.id:
                   for old_cnx in node["connection"]:
                       if (old_cnx["target_datapath"] == str(cnxn.src_iface.switch.datapath_id) and old_cnx["target_port"] == str(cnxn.src_iface.port_num)):
                          cnx_exists=True
                          break
                   if not cnx_exists :
                       node["connection"].append(dict(
                       target_port = str(cnxn.src_iface.port_num),
                       src_port = str(cnxn.dst_iface.port_num),
                       target_datapath = str(cnxn.src_iface.switch.datapath_id)))
        except Exception as e:
            pass
    
    for cnxn in of_cnxn_qs:
        #XXX: change me
        try:
            links.append(
                dict(
                    src=id_to_idx[cnxn.src_iface.switch.id],
                    #src_datapath=cnxn.src_iface.switch.datapath_id,
                    #src_port=cnxn.src_iface.port_num,
                    target=id_to_idx[cnxn.dst_iface.switch.id],
                    #target_datapath=cnxn.dst_iface.switch.datapath_id,
                    #target_port=cnxn.dst_iface.port_num,
                   value="rsc_id_%s-rsc_id_%s" % (
                        cnxn.src_iface.id, cnxn.dst_iface.id
                    ),
                )
            )
        except:
            pass
    for cnxn in non_of_cnxn_qs:
        links.append(
            dict(
                src=id_to_idx[cnxn.of_iface.switch.id],
                target=id_to_idx[cnxn.resource.id],
                value="rsc_id_%s-rsc_id_%s" % (
                    cnxn.of_iface.id, cnxn.resource.id
                ),
            )
        )
        links.append(
            dict(
                target=id_to_idx[cnxn.of_iface.switch.id],
                src=id_to_idx[cnxn.resource.id],
                value="rsc_id_%s-rsc_id_%s" % (
                    cnxn.resource.id, cnxn.of_iface.id
                ),
            )
        )

    #VT-AM nodes 
    for i, agg in enumerate(vt_aggs):
        agg_ids.append(agg.pk)
#       vt_servers = [{'name':"prova",'id':99},{'name':"prova2",'id':100},{'name':"prova3",'id':101}]
        vt_servers = VTServer.objects.filter(
            aggregate__pk=agg.pk,
            available=True,
        )



        for n in vt_servers:
            #id_to_idx[n.id] = len(nodes)
#            nodes.append(dict(
#                    name=n.name, value=n.uuid, group=i+len(of_aggs)+len(pl_aggs))
#                    #name=n['name'], value=n['id'], group=i+len(of_aggs)+len(pl_aggs))
#            )
            vmNames = []
            for name in  n.vms.all().values_list('name', flat=True):
                vmNames.append(str(name))
            vmInterfaces = []
            for j,inter in enumerate(n.ifaces.all()):
                vmInterfaces.append(dict(name="eth"+str(j+1), switch=str(inter.switchID), port=str(inter.port)))
            nodes.append(dict(
                    name=n.name, value=n.uuid, group=i+len(of_aggs)+len(pl_aggs), type="vt_agg", vmNames=vmNames, vmInterfaces=vmInterfaces)
                    #name=n['name'], value=n['id'], group=i+len(of_aggs)+len(pl_aggs))
            ) 
            for j,inter in enumerate(n.ifaces.all()):
		#first check datapathId exists.
                try:
                    sId= openflowSwitches[inter.switchID]
                except:
                    continue
                links.append(
                        dict(
                            target=sId,
                            src=len(nodes)-1,
                            value=inter.ifaceName+":"+str(inter.port)
                            ),
                     )
    return (nodes, links)



def _get_tree_ports(of_aggs, pl_aggs):
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


'''
Home and allocation view functions
'''

def bookOpenflow(request, slice_id):
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
        
        return HttpResponseRedirect(reverse("html_plugin_flowspace",
                                            args=[slice_id]))
    else:
        checked_ids = list(OpenFlowInterface.objects.filter(
            slice_set=slice).values_list("id", flat=True))
        checked_ids.extend(PlanetLabNode.objects.filter(
            slice_set=slice).values_list("id", flat=True))

        aggs_filter = (Q(leaf_name=OpenFlowAggregate.__name__.lower()) |
                       Q(leaf_name=GCFOpenFlowAggregate.__name__.lower()))
        of_aggs = \
            slice.aggregates.filter(aggs_filter)
        pl_aggs = \
            slice.aggregates.filter(
                leaf_name=PlanetLabAggregate.__name__.lower())

        vt_aggs = \
            slice.aggregates.filter(
                leaf_name=VtPlugin.__name__.lower())

        for agg in vt_aggs:
            vtPlugin = agg.as_leaf_class()
            askForAggregateResources(vtPlugin, projectUUID = Project.objects.filter(id = slice.project_id)[0].uuid, sliceUUID = slice.uuid)
       
#        vm = VM.objects.filter(sliceId=slice.uuid)        
 
        protovis_nodes, protovis_links = _get_nodes_links(of_aggs, pl_aggs, vt_aggs)
        tree_rsc_ids = _get_tree_ports(of_aggs, pl_aggs)
        
        return simple.direct_to_template(
            request,
            template="html/select_resources.html",
            extra_context={
                "protovis_nodes": protovis_nodes,
                "protovis_links": protovis_links,
                "tree_rsc_ids": tree_rsc_ids,
                "openflow_aggs": of_aggs,
                "planetlab_aggs": pl_aggs,
                "vt_aggs": vt_aggs,
                "slice": slice,
                "checked_ids": checked_ids,
                "ofswitch_class": OpenFlowSwitch,
                "planetlab_node_class": PlanetLabNode,
#                "virtualmachines": vm,
                "breadcrumbs": (
                    ("Home", reverse("home")),
                    ("Project %s" % slice.project.name, reverse("project_detail", args=[slice.project.id])),
                    ("Slice %s" % slice.name, reverse("slice_detail", args=[slice_id])),
                    ("Resource visualization panel ", reverse("html_plugin_home", args=[slice_id])),
                    ("Allocate Openflow and PlanetLab resources", reverse("html_plugin_bookOpenflow", args=[slice_id])),
                )
            },
        )
 

def home(request, slice_id):
    """
    Display the list of all the resources  
    """
    
    slice = get_object_or_404(Slice, id=slice_id)
    if request.method == "POST":
        
        _update_openflow_resources(request, slice)
        _update_planetlab_resources(request, slice)
        
        slice.modified = True
        slice.save()
        
        return HttpResponseRedirect(reverse("html_plugin_flowspace",
                                            args=[slice_id]))
    else:
        checked_ids = list(OpenFlowInterface.objects.filter(
            slice_set=slice).values_list("id", flat=True))
        checked_ids.extend(PlanetLabNode.objects.filter(
            slice_set=slice).values_list("id", flat=True))

        aggs_filter = (Q(leaf_name=OpenFlowAggregate.__name__.lower()) |
                       Q(leaf_name=GCFOpenFlowAggregate.__name__.lower()))
        of_aggs = \
            slice.aggregates.filter(aggs_filter)
        pl_aggs = \
            slice.aggregates.filter(
                leaf_name=PlanetLabAggregate.__name__.lower())

        vt_aggs = \
            slice.aggregates.filter(
                leaf_name=VtPlugin.__name__.lower())
        for agg in vt_aggs:
            vtPlugin = agg.as_leaf_class()
            askForAggregateResources(vtPlugin, projectUUID = Project.objects.filter(id = slice.project_id)[0].uuid, sliceUUID = slice.uuid)
       
#        vm = VM.objects.filter(sliceId=slice.uuid)        
 
        protovis_nodes, protovis_links = _get_nodes_links(of_aggs, pl_aggs, vt_aggs)
        tree_rsc_ids = _get_tree_ports(of_aggs, pl_aggs)
        
        fsquery=FlowSpaceRule.objects.filter(slivers__slice=slice).distinct().order_by('id')
        allocated_of_resources=[]
        ports=[]
        for agg in of_aggs:
            for rsc in agg.resource_set.all():
                rsc = rsc.as_leaf_class()
                if isinstance(rsc,OpenFlowSwitch):
                   ports=[]
                   for iface in rsc.openflowinterface_set.all():
                       if iface.id in checked_ids:
                           ports.append(iface.port_num)
                   if ports:
                       allocated_of_resources.append(dict(switch=rsc,ports=ports))

        return simple.direct_to_template(
            request,
            template="html/show_resources.html",
            extra_context={
                "protovis_nodes": protovis_nodes,
                "protovis_links": protovis_links,
                "tree_rsc_ids": tree_rsc_ids,
                "openflow_aggs": of_aggs,
                "planetlab_aggs": pl_aggs,
                "vt_aggs": vt_aggs,
                "slice": slice,
                "checked_ids": checked_ids,
                "allfs": fsquery, 
                "ofswitch_class": OpenFlowSwitch,
                "planetlab_node_class": PlanetLabNode,
                "allocated_of_resources":allocated_of_resources,
                "breadcrumbs": (
                    ("Home", reverse("home")),
                    ("Project %s" % slice.project.name, reverse("project_detail", args=[slice.project.id])),
                    ("Slice %s" % slice.name, reverse("slice_detail", args=[slice_id])),
                    ("Resource visualization panel ", reverse("html_plugin_home", args=[slice_id])),
                )
            },
        )
        
def flowspace(request, slice_id):
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
    FSFormSet = modelformset_factory(
        model=FlowSpaceRule,
        formfield_callback=formfield_callback,
        can_delete=True,
        extra=2,
    )
    
    if request.method == "POST":
        formset = FSFormSet(
            request.POST,
            queryset=FlowSpaceRule.objects.filter(
                slivers__slice=slice).distinct(),
        )
        if formset.is_valid():
            formset.save()
            
            DatedMessage.objects.post_message_to_user(
                "Successfully set flowspace for slice %s" % slice.name,
                request.user, msg_type=DatedMessage.TYPE_SUCCESS,
            )
            
            slice.modified = True
            slice.save()
            return HttpResponseRedirect(request.path)
    
    elif request.method == "GET":
        formset = FSFormSet(
            queryset=FlowSpaceRule.objects.filter(
                slivers__slice=slice).distinct(),
        )
    
    else:
        return HttpResponseNotAllowed("GET", "POST")
        
    done = PlanetLabSliver.objects.filter(slice=slice).count() == 0
        
    return simple.direct_to_template(
        request,
        template="html/select_flowspace.html",
        extra_context={
            "slice": slice,
            "fsformset": formset,
            "done": done,
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

