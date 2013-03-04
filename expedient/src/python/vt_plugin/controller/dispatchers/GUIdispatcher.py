import logging
from pprint import pformat

from django.views.generic import simple
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseNotAllowed,\
    HttpResponse
from django.forms.models import modelformset_factory
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django import forms
from django.db.models import Q
from django.views.generic.create_update import get_model_and_form_class

import copy
from vt_plugin.models import VtPlugin, VTServer, VM, Action
from vt_plugin.forms.VM import VMModelForm
from vt_manager.communication.utils.XmlHelper import XmlHelper
from vt_plugin.utils.Translator import Translator
import xmlrpclib, uuid
from vt_plugin.utils.ServiceThread import *
from vt_plugin.controller.dispatchers.ProvisioningDispatcher import *
from vt_plugin.controller.VMcontroller.VMcontroller import *
from vt_plugin.utils.ServiceThread import *
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.common.messaging.context_processors import messaging
from expedient.common.messaging.models import DatedMessage

# XXX: MAY REMOVE. Remove OpenFlow dependency
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
from vt_plugin.models import VtPlugin, VTServer, VM, Action
from vt_plugin.controller.vtAggregateController.vtAggregateController import askForAggregateResources
from vt_plugin.utils.Translator import Translator
import xmlrpclib, uuid, copy
from vt_plugin.utils.ServiceThread import *
from vt_plugin.controller.dispatchers.ProvisioningDispatcher import *
import json
from openflow.plugin.vlans import *
# XXX: END OF MAY REMOVE SECTION

from expedient.clearinghouse.resources.models import Resource

def goto_create_vm(request, slice_id, agg_id):
    """Show a page that allows user to add SSH s to the aggregate."""

    if request.method == "POST":
        # Shows error message when Aggregate is unreachable, disable VM creation and get back to slice detail page
        agg = Aggregate.objects.get(id = agg_id)
        if agg.check_status() == False:
            DatedMessage.objects.post_message_to_user(
                "VM Aggregate '%s' is not available" % agg.name,
                request.user, msg_type=DatedMessage.TYPE_ERROR,)
            return HttpResponseRedirect(reverse("slice_detail",args=[slice_id]))

        if 'create_vms' in request.POST:
            server_id=request.POST['selected_server_'+agg_id]
            return HttpResponseRedirect(reverse("virtualmachine_crud",
                                                args=[slice_id,server_id]))
        else:
            return HttpResponseRedirect("/")

#TODO: put the plugin code in plugin package!!!
def virtualmachine_crud(request, slice_id, server_id):

    """Show a page that allows user to add VMs to the VT server."""
    error_crud = ""
    serv = get_object_or_404(VTServer, id = server_id)
    slice = get_object_or_404(Slice, id = slice_id)
    virtualmachines = VM.objects.filter(sliceId=slice.uuid)

    # Creates a model based on VM
    VMModelFormAux = modelformset_factory(
        VM, can_delete=False, form=VMModelForm,
        fields=["name", "memory","disc_image", "hdSetupType", "virtualizationSetupType"],
    )

    try:
        if request.method == "POST":
            if 'create_new_vms' in request.POST:
                # "Done" pressed ==> send xml to AM
                formset = VMModelFormAux(request.POST, queryset=virtualmachines)
                if formset.is_valid():
                    instances = formset.save(commit=False)
                    #create virtualmachines from received formulary
                    VMcontroller.processVMCreation(instances, serv.uuid, slice, request.user)
#                    return HttpResponseRedirect(reverse("slice_home",
                    return HttpResponseRedirect(reverse("slice_detail",
                                                args=[slice_id]))
                # Form not valid => raise error
                else:
                    raise ValidationError("Invalid input: either VM name contains non-ASCII characters, underscores, whitespaces or the memory is not a number or less than 128Mb.", code="invalid",)

        else:
            formset = VMModelFormAux(queryset=VM.objects.none())

    except ValidationError as e:
        # Django exception message handling is different to Python's...
        error_crud = ";".join(e.messages)
    except Exception as e:
        print "normal exception here: %s" % str(e)
        DatedMessage.objects.post_message_to_user(
            "VM might have been created, but some problem ocurred: %s" % str(e),
            request.user, msg_type=DatedMessage.TYPE_ERROR)
        return HttpResponseRedirect(reverse("home"))

    return simple.direct_to_template(
        request, template="aggregate_add_virtualmachines.html",
        extra_context={"virtual_machines": virtualmachines, "exception": error_crud,
                        "server_name": serv.name, "formset": formset,"slice":slice,
                        "breadcrumbs": (
                    ("Home", reverse("home")),
                    ("Project %s" % slice.project.name, reverse("project_detail", args=[slice.project.id])),
                    ("Slice %s" % slice.name, reverse("slice_detail", args=[slice_id])),
#                   #("Resource visualization panel ", reverse("slice_home", args=[slice_id])),
                    ("Create VM in server %s" %serv.name, reverse("virtualmachine_crud", args=[slice_id, server_id])),
                )
        })

def manage_vm(request, slice_id, vm_id, action_type):

    "Manages the actions executed over VMs at url manage resources."

    vm = VM.objects.get(id = vm_id)
    #if action_type == 'stop' : action_type = 'hardStop'
    rspec = XmlHelper.getSimpleActionSpecificQuery(action_type, vm.serverID)
    Translator.PopulateNewAction(rspec.query.provisioning.action[0], vm)

    ServiceThread.startMethodInNewThread(ProvisioningDispatcher.processProvisioning,rspec.query.provisioning, request.user)

    #set temporally status
    #vm.state = "on queue"
    if action_type == 'start':
        vm.state = 'starting...'
    elif action_type == 'stop':
        vm.state = 'stopping...'
    elif action_type == 'reboot':
        vm.state = 'rebooting...'
    elif action_type == 'delete':
        vm.state = 'deleting...'
    elif action_type == 'create':
        vm.state = 'creating...'
    vm.save()
    #go to manage resources again
    #return HttpResponseRedirect(reverse("slice_home",args=[slice_id]))
    response = HttpResponse("")
    return response


def check_vms_status(request, slice_id):
    from django.utils import simplejson
    vmsStatus = {}
    vmsActionsHtmlCodes = {}
    vmsIP = {}
    slice = get_object_or_404(Slice, id=slice_id)
    vt_aggs = \
            slice.aggregates.filter(
                leaf_name=VtPlugin.__name__.lower())
    for agg in vt_aggs:
        for server in agg.resource_set.all():
            if server.leaf_name == 'VTServer':
                for vm in server.as_leaf_class().vms.all():
                    vmsStatus[str(vm.id)]= vm.state
                    if vm.state == "running":
                        actionsHtmlCode =\
                        "<div>\
                        <a href=\"#/\" onclick=\"handleVMaction("+str(slice.id)+","+str(vm.id)+",\'stop\')\">Stop</a> |\
                        <a href=\"#/\" onclick=\"handleVMaction("+str(slice.id)+","+str(vm.id)+",\'reboot\')\">Reboot</a>\
                        </div>"
                    elif  vm.state == "created (stopped)" :
                        actionsHtmlCode =\
						"<div>\
                        <a href=\"#/\" onclick=\"handleVMaction("+str(slice.id)+","+str(vm.id)+",\'start\')\">Start</a> |\
                        <a href=\"#/\" onclick=\"handleVMaction("+str(slice.id)+","+str(vm.id)+",\'delete\',\'"+str(vm.name)+"\')\">Delete</a>\
                        </div>"
                    elif vm.state == "stopped" :
                        actionsHtmlCode =\
                        "<div>\
                        <a href=\"#/\" onclick=\"handleVMaction("+str(slice.id)+","+str(vm.id)+",\'start\')\">Start</a> |\
                        <a href=\"#/\" onclick=\"handleVMaction("+str(slice.id)+","+str(vm.id)+",\'delete\',\'"+str(vm.name)+"\')\">Delete</a>\
                        </div>"
                    else:
                        actionsHtmlCode = "<div><img src=\"/static/media/default/img/loading.gif\" align=\"absmiddle\"></div>"
                    vmsActionsHtmlCodes[str(vm.id)] = actionsHtmlCode
                    try:
                        vmsIP[str(vm.id)]= vm.ifaces.get(isMgmt = True).ip
                    except:
                        pass
        
    data = simplejson.dumps({'status': vmsStatus, 'actions': vmsActionsHtmlCodes, 'ips': vmsIP,})
    response = HttpResponse(data)
    return response


def startStopSlice(action,uuid):

    "Manages the actions executed over VMs at url manage resources."
    try: 
        vmsToStart = VM.objects.filter(sliceId = uuid)
    
        #if action_type == 'stop' : action_type = 'hardStop'
        globalRspec = XmlHelper.getSimpleActionSpecificQuery(action, "dummy")
    	globalRspec.query.provisioning.action.pop()
        for vm in vmsToStart:
            rspec = XmlHelper.getSimpleActionSpecificQuery(action, vm.serverID)
            Translator.PopulateNewAction(rspec.query.provisioning.action[0], vm)
            globalRspec.query.provisioning.action.append(copy.deepcopy(rspec.query.provisioning.action[0]))
    
        ServiceThread.startMethodInNewThread(ProvisioningDispatcher.processProvisioning,globalRspec.query.provisioning, None)
    
        for vm in vmsToStart:
            if action == 'start':
            	vm.state = 'starting...'
            elif action == 'stop':
                vm.state = 'stopping'
            vm.save()
    except Exception as e:
        print e
        raise e


def update_messages(request):
    return simple.direct_to_template(
        request,
        template="messages_panel.html",
        extra_context=messaging(request),
    )

###
# Topology to show in the Expedient
#

def get_vms_list(slice):
    return VM.objects.filter(sliceId = slice.uuid)

def get_vm_aggregates(slice):
    vt_aggs = slice.aggregates.filter(leaf_name=VtPlugin.__name__.lower())
    try:
        from vt_plugin.controller.vtAggregateController.vtAggregateController import askForAggregateResources
        for agg in vt_aggs:
            vtPlugin = agg.as_leaf_class()
            project_uuid = Project.objects.filter(id = slice.project_id)[0].uuid
            askForAggregateResources(vtPlugin, projectUUID = project_uuid, sliceUUID = slice.uuid)
    except:
        pass
    return vt_aggs

def get_node_description(node, vms, vms_interfaces):
    description = "<strong>Server: " + node.name + "</strong><br/><br/>"
    number_vms = len(vms)
    if number_vms:
        description += "<strong>VMs (" + str(number_vms) + "):</strong><br clear=left />";
        for i, v in enumerate(vms):
            description += str(v)
            if i < number_vms-1:
                description += ", "
            else:
                description += "<br clear = left /><br clear=left />"
    else:
        description += "<strong>No VMs in this Server </strong><br/><br clear=left />"
    description += "<strong>VMs Interfaces:</strong><br clear=left />"
    for interface in vms_interfaces:
        description += "&#149; "+"<strong>" + interface['name'] + "</strong> to Switch: " + interface['switch']+ " at port: " + interface['port'] + "<br clear=left />";
    return description

def get_nodes_links(slice, chosen_group=None):
    nodes = []
    links = []

    agg_ids = []
    n_islands = 0

#    ### PROBLEMATIC CODE!
#    id_to_idx = {}
#    #FIXME: dependency against OpenFlow plugin!!!!!! MAYBE HANDLE THE #GROUP INSIDE JAVASCRIPT?
#    from openflow.plugin.views import get_openflow_aggregates
#    of_aggs = get_openflow_aggregates(slice)
##    chosen_group = len(of_aggs)
#
#    #Openflow devices
#    #XXX: botch
#    openflowSwitches = dict() 
#    for i, agg in enumerate(of_aggs):
#        agg_ids.append(agg.pk)
#        switches = OpenFlowSwitch.objects.filter(
#            aggregate__pk=agg.pk,
#            available=True,
#        )
#        for s in switches:
#            id_to_idx[s.id] = len(nodes)
#            nodes.append(dict( 
#                name=s.name, value=s.id, aggregate=agg.pk, type="OpenFlow Aggregate",
#                available=agg.available, description="", connection=[], loc=agg.location)
#            )
#            openflowSwitches[s.datapath_id] = len(nodes)-1
#    print "************************** openflowSwitches: %s" % str(openflowSwitches)
#    nodes = []
#    ### END OF PROBLEMATIC CODE!

    vt_aggs = get_vm_aggregates(slice)

    # Getting image for the nodes
    # FIXME: avoid to ask the user for the complete name of the method here! he should NOT know it
    try:
        image_url = reverse('img_media_vt_plugin', args=("server-tiny.png",))
    except:
        image_url = 'server-tiny.png'

    # For every Virtualization AM
    for i, agg in enumerate(vt_aggs):
        agg_ids.append(agg.pk)
        vt_servers = VTServer.objects.filter(
            aggregate__pk=agg.pk,
            available=True,
        )

        serverInSameIsland = False

        # For every server of the Virtualization AM
        for n in vt_servers:
            vmNames = []
            for name in  n.vms.all().filter(sliceId = slice.uuid).values_list('name', flat=True):
                vmNames.append(str(name))
            vmInterfaces = []
            j=1 #FIXME XXX: eth0 is mgmt 
            for inter in n.getNetworkInterfaces():
                inter = inter[1] #WTF: why QuerySet is not iterable straight away, and have to wrap it via enumerate
                if not inter.isMgmt:
                    vmInterfaces.append(dict(name="eth"+str(j), switch=str(inter.switchID), port=str(inter.port)))
                    j+=1
            nodes.append(dict(
                    #XXX: lbergesio: Removed len(pl_aggs) to match vt_aggs with of_aggs in the 
                    #same group. Will planetlab be supported at the end?
                    # ORIGINAL
                    #name = n.name, value=n.id, group = i+chosen_group, aggregate = agg.pk,
                    # Carolina: users shall not be left the choice to choose group/island; otherwise collision may arise
                    name = n.name, value=n.id, aggregate = agg.pk, type = "Virtualized server",
                    description = get_node_description(n, vmNames, vmInterfaces), image = image_url,
                    available = agg.available, vmNames = vmNames, vmInterfaces = vmInterfaces, loc = agg.location)
                    #name=n.name, value=n.id, group=i+len(of_aggs), type="vt_agg", available=agg.available, vmNames=vmNames, vmInterfaces=vmInterfaces, loc=agg.location)
                    # Older
                    #name=n.name, value=n.uuid, group=i+len(of_aggs)+len(pl_aggs), type="vt_agg", vmNames=vmNames, vmInterfaces=vmInterfaces)
            )
            serverGroupSet=False

            # FIXME: Cuando entra en los links, todo peta...
            # For every interface of the server
            for j,inter in enumerate(n.ifaces.all()):
                #first check datapathId exists.
                try:
                    print "************************************** doing some link search... switch.id = %s" % str(inter.switchID)
                    # XXX: REMOVE -- OLD
#                    sId = openflowSwitches[inter.switchID]
#                    print "************************************** source ID (OLD!): %s" % str(sId)
#                    pId = OpenFlowSwitch.objects.get(name = inter.switchID).openflowinterface_set.get(port_num=inter.port).id
#                    print "************************************** target ID (OLD!): %s" % str(pId)


#                    openFlowSwitch = OpenFlowSwitch.objects.get(name = inter.switchID)
                    openFlowSwitch = Resource.objects.get(name = inter.switchID)
                    print "************************************** openflowswitch: %s" % str(openFlowSwitch)
#                    sId = openFlowSwitch.id
                    # FIXME -> HACER QUE SE PUEDA ENLAZAR DE UNO A OTRO CON LAS IDs REALES
                    sId = j
                    print "************************************** source ID: %s" % str(sId)
                    pId = openFlowSwitch.openflowinterface_set.get(port_num=inter.port).id
                    print "************************************** target ID: %s" % str(pId)
                except:
                    continue
                print "************************************** CHECKPOINT #0"
                links.append(
                        dict(
                            target = sId,
                            source = len(nodes)-1,
                            value = "rsc_id_" + str(pId) + "-" + str(inter.ifaceName) + ":" + str(inter.port)
                            #value="rsc_id_"+str(sId)+"-"+str(inter.ifaceName)+":"+str(inter.port)
                            #value=inter.ifaceName+":"+str(inter.port)
                            ),
                     )
                # When the server has >= 1 interfaces, set 'serverGroupSet' to True
                print "************************************** CHECKPOINT #1"
                if (not serverGroupSet):
                    # ORIGINAL
#                    nodes[len(nodes)-1]["group"] = nodes[sId]["group"]
                    serverGroupSet = True
                print "************************************** CHECKPOINT #2"

            # When the previous flag is set to True, add island
            if (not serverGroupSet and not serverInSameIsland):
                #Add n_islands since there is an Island with VM AM but no OF AM
                n_islands += 1
                # This groups servers of the same VT AM in the same island
                serverInSameIsland = True
            print "************************************** CHECKPOINT #3"
    return [nodes, links, n_islands]

# XXX: REMOVE... ONLY FOR TESTS
def _get_nodes_links(of_aggs, pl_aggs,vt_aggs, slice_id):
    """
    Get nodes and links usable by d3.
    """
    nodes = []
    links = []

    id_to_idx = {}
    agg_ids = []
   
    nIslands = 0

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
            agg_pk = agg.pk or 0
            nodes.append(dict( 
                name=s.name, value=s.id, aggregate=agg_pk, type="of_agg", description="", image="", available=agg.available, connection=[], loc=agg.location)
            )
	    openflowSwitches[s.datapath_id] = len(nodes)-1
   
    #One island per OF AM
    nIslands = len(of_aggs)

    #Planelab nodes 
    for i, agg in enumerate(pl_aggs):
        agg_ids.append(agg.pk)
        pl_nodes = PlanetLabNode.objects.filter(
            aggregate__pk=agg.pk,
            available=True,
        )
        for n in pl_nodes:
            id_to_idx[n.id] = len(nodes)
            agg_pk = agg.pk or 0
            nodes.append(dict(
                #XXX: lbergesio: pl_agg nodes set to group -1 to match vt_aggs con of_aggs in the 
                #same group. Will planetlab be supported at the end?
                name=n.name, value=n.id, aggregate=agg_pk or 0,type="pl_agg", description="", image="", available=agg.available, loc=agg.location)
                #name=n.name, value=n.id, group=i+len(of_aggs), type="pl_agg" )
            )


    print "\n\n\n\n CHECKPOINT #1 \n\n\n\n"

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

    print "\n\n\n\n CHECKPOINT #2 \n\n\n\n"

    sliceUUID = Slice.objects.get(id=slice_id).uuid
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
    
    print "\n\n\n\n CHECKPOINT #3 \n\n\n\n"

    for cnxn in of_cnxn_qs:
        #XXX: change me
        try:
            src_link = id_to_idx[cnxn.src_iface.switch.id] or 0
            links.append(
                dict(
                    src=src_link,
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

    print "\n\n\n\n CHECKPOINT #4 \n\n\n\n"

    for cnxn in non_of_cnxn_qs:
        src_link = id_to_idx[cnxn.of_iface.switch.id] or 0
        links.append(
            dict(
                src=src_link,
                target=id_to_idx[cnxn.resource.id],
                value="rsc_id_%s-rsc_id_%s" % (
                    cnxn.of_iface.id, cnxn.resource.id
                ),
            )
        )
        src_link = id_to_idx[cnxn.resource.id] or 0
        links.append(
            dict(
                target=id_to_idx[cnxn.of_iface.switch.id],
                src=src_link,
                value="rsc_id_%s-rsc_id_%s" % (
                    cnxn.resource.id, cnxn.of_iface.id
                ),
            )
        )

    print "\n\n\n\n CHECKPOINT #5 \n\n\n\n"

    # For every Virtualization AM
    for i, agg in enumerate(vt_aggs):
        agg_ids.append(agg.pk)
        vt_servers = VTServer.objects.filter(
            aggregate__pk=agg.pk,
            available=True,
        )

        serverInSameIsland = False

        # For every server of the Virtualization AM
        for n in vt_servers:
            vmNames = []
            for name in  n.vms.all().filter(sliceId = sliceUUID).values_list('name', flat=True):
                vmNames.append(str(name))
            vmInterfaces = []
            j=1 #FIXME XXX: eth0 is mgmt 
            for inter in n.getNetworkInterfaces():
		inter = inter[1] #WTF: why QuerySet is not iterable straight away, and have to wrap it via enumerate
                if not inter.isMgmt: 
                    vmInterfaces.append(dict(name="eth"+str(j), switch=str(inter.switchID), port=str(inter.port)))
                    j+=1
                    agg_pk = agg.pk or 0
            nodes.append(dict(
                    #XXX: lbergesio: Removed len(pl_aggs) to matche vt_aggs con of_aggs in the 
                    #same group. Will planetlab be supported at the end?
                    name=n.name, value=n.id, description="", image="", aggregate=agg_pk,type="vt_agg", available=agg.available, vmNames=vmNames, vmInterfaces=vmInterfaces, loc=agg.location)
                    #name=n.name, value=n.uuid, group=i+len(of_aggs), type="vt_agg", vmNames=vmNames, vmInterfaces=vmInterfaces, loc=agg.location)
                    #name=n.name, value=n.uuid, group=i+len(of_aggs)+len(pl_aggs), type="vt_agg", vmNames=vmNames, vmInterfaces=vmInterfaces)
            )
            serverGroupSet=False

            print "\n\n\n\n CHECKPOINT #6 \n\n\n\n"

            # For every interface of the server
            for j,inter in enumerate(n.ifaces.all()):
		#first check datapathId exists.
                try:
                    sId= openflowSwitches[inter.switchID]
                    pId = OpenFlowSwitch.objects.get(name = inter.switchID).openflowinterface_set.get(port_num=inter.port).id
                except:
                    continue
                src_link = len(nodes)-1 or 0
                links.append(
                        dict(
                            target=sId,
                            src=src_link,
                            value="rsc_id_"+str(pId)+"-"+str(inter.ifaceName)+":"+str(inter.port)
                            #value="rsc_id_"+str(sId)+"-"+str(inter.ifaceName)+":"+str(inter.port)
                            #value=inter.ifaceName+":"+str(inter.port)
                            ),
                     )

                print "\n\n\n\n CHECKPOINT #6 1/2 \n\n\n\n"

                # When the server has >= 1 interfaces, set 'serverGroupSet' to True
                if (not serverGroupSet):
                    # Gives an error, but thanks to this everything works...
                    nodes[len(nodes)-1]["group"]=nodes[sId]["group"]
                    serverGroupSet = True

            # When the previous flag is set to True, add island
            if(not serverGroupSet and not serverInSameIsland):
                #Add nIslands since there is an Island with VM AM but no OF AM
                nIslands += 1
                # This groups servers of the same VT AM in the same island
                serverInSameIsland = True

    print "\n\n\n\n CHECKPOINT #7 \n\n\n\n"

    return [nodes, links, nIslands]

def get_ui_data(slice):
    """
    Hook method. Use this very same name so Expedient can get the resources for every plugin.
    """
    ui_context = dict()
    try:
        ui_context['vms_list'] = get_vms_list(slice)
        ui_context['vt_aggs'] = get_vm_aggregates(slice)
        ui_context['nodes'], ui_context['links'], ui_context['n_islands'] = get_nodes_links(slice)

#        aggs_filter = (Q(leaf_name=OpenFlowAggregate.__name__.lower()) | Q(leaf_name=GCFOpenFlowAggregate.__name__.lower()))
#        of_aggs = slice.aggregates.filter(aggs_filter)
#        pl_aggs = slice.aggregates.filter(leaf_name=PlanetLabAggregate.__name__.lower())
#        vt_aggs = get_vm_aggregates(slice)
#        ui_context['nodes'], ui_context['links'], ui_context['n_islands'] = _get_nodes_links(of_aggs, pl_aggs, vt_aggs, slice.id)
#        print "\n\n\n\nui_context['nodes'] = %s" % str(ui_context['nodes'])
#        print "\n\n\n\nui_context['links'] = %s" % str(ui_context['links'])


    except Exception as e:
        print "[ERROR] Problem loading UI data for plugin 'vt_plugin'. Details: %s" % str(e)
    return ui_context

