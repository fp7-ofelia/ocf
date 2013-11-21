import logging

from django.views.generic import simple
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseNotAllowed,\
    HttpResponse
from django.forms.models import modelformset_factory
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django import forms

import copy
from vt_plugin.models import VtPlugin, VTServer, VM, Action
from vt_plugin.forms.VM import VMModelForm
from vt_manager.communication.utils.XmlHelper import XmlHelper
from vt_plugin.utils.Translator import Translator
from vt_plugin.controller.dispatchers.ProvisioningDispatcher import ProvisioningDispatcher
from vt_plugin.controller.VMcontroller.VMcontroller import VMcontroller
from vt_plugin.utils.ServiceThread import ServiceThread
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.common.messaging.context_processors import messaging
from expedient.common.messaging.models import DatedMessage

from expedient.clearinghouse.slice.models import Slice
from expedient.clearinghouse.project.models import Project
from expedient.common.utils.plugins.plugincommunicator import PluginCommunicator
from expedient.common.utils.plugins.resources.node import Node
from expedient.common.utils.plugins.resources.link import Link

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

def virtualmachine_crud(request, slice_id, server_id):

    """Show a page that allows user to add VMs to the VT server."""
    error_crud = ""
    serv = get_object_or_404(VTServer, id = server_id)
    slice = get_object_or_404(Slice, id = slice_id)
    virtualmachines = VM.objects.filter(sliceId=slice.uuid)

    # Creates a model based on VM
#    VMModelFormAux = modelformset_factory(
#        VM, can_delete=False, form=VMModelForm,
#        fields=["name", "memory","disc_image", "hdSetupType", "virtualizationSetupType"],
#    )

    try:
        if request.method == "POST":
            import pprint
            pprint.pprint(request.POST)
            
            print "--------------------------------------1"
            if 'create_new_vms' in request.POST:
                print "----------------------------------2"
                # "Done" pressed ==> send xml to AM
#                formset = VMModelFormAux(request.POST, queryset=virtualmachines)
                form = VMModelForm(request.POST)
                print "----------------------------------3"
#               if formset.is_valid():
                print form.errors
                if form.is_valid():
                    print "------------------------------------4"
                    instance = form.save(commit=False)
                    print "------------------------------------5"
                    #create virtualmachines from received formulary
                    VMcontroller.processVMCreation(instance, serv.uuid, slice, request.user)
                    print "------------------------------------6" 
#                   VMcontroller.processVMCreation(instances, serv.uuid, slice, request.user)
                    return HttpResponseRedirect(reverse("slice_detail",
                                                args=[slice_id]))
                # Form not valid => raise error
                else:
                    print "-------------------------------------7" 
                    if "VM already exists" in form.errors[0]:
                        print "----------------------------------8"
                        raise ValidationError("It already exists a VM with the same name in the same slice. Please choose another name", code="invalid",)
                    print "-----------------------------------10" 
                    raise ValidationError("Invalid input: either VM name contains non-ASCII characters, underscores, whitespaces or the memory is not a number or less than 128Mb.", code="invalid",)

        else:
            print "----------------------------------------9"
            form = VMModelForm()

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
        request, template="vt_plugin_aggregate_add_virtualmachines.html",
        extra_context={"virtual_machines": virtualmachines, "exception": error_crud,
                        "server_name": serv.name, "form": form,"slice":slice,
                        "breadcrumbs": (
                    ("Home", reverse("home")),
                    ("Project %s" % slice.project.name, reverse("project_detail", args=[slice.project.id])),
                    ("Slice %s" % slice.name, reverse("slice_detail", args=[slice_id])),
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
    response = HttpResponse("")
    return response


def check_vms_status(request, slice_id):
    from django.utils import simplejson
    vmsStatus = {}
    vmsActionsHtmlCodes = {}
    vmsIP = {}
    slice = get_object_or_404(Slice, id=slice_id)
    vt_aggs = slice.aggregates.filter(leaf_name=VtPlugin.__name__.lower())
    for agg in vt_aggs:
        for server in agg.resource_set.all():
            if server.leaf_name == 'VTServer':
                for vm in server.as_leaf_class().vms.all().filter(sliceId = slice.uuid):
                    vmsStatus[str(vm.id)]= vm.state
                    if vm.state == "running":
                        actionsHtmlCode =\
                        "<div class=\"vm_actions\">\
                        <input type=\"button\" onclick=\"handleVMaction("+str(slice.id)+","+str(vm.id)+",\'stop\')\" value=\"Stop\" />\
                        <input type=\"button\" onclick=\"handleVMaction("+str(slice.id)+","+str(vm.id)+",\'reboot\')\" value=\"Reboot\" />\
                        </div>"
                    elif  vm.state == "created (stopped)" :
                        actionsHtmlCode =\
			"<div class=\"vm_actions\">\
                        <input type=\"button\" onclick=\"handleVMaction("+str(slice.id)+","+str(vm.id)+",\'start\')\" value=\"Start\" />\
                        <input type=\"button\" onclick=\"handleVMaction("+str(slice.id)+","+str(vm.id)+",\'delete\',\'"+str(vm.name)+"\')\" value=\"Delete\" />\
                        </div>"
                    elif vm.state == "stopped" :
                        actionsHtmlCode =\
			"<div class=\"vm_actions\">\
                        <input type=\"button\" onclick=\"handleVMaction("+str(slice.id)+","+str(vm.id)+",\'start\')\" value=\"Start\" />\
                        <input type=\"button\" onclick=\"handleVMaction("+str(slice.id)+","+str(vm.id)+",\'delete\',\'"+str(vm.name)+"\')\" value=\"Delete\" />\
                        </div>"
                    else:
                        actionsHtmlCode = "<div><img src='/static/media/default/img/loading.gif' align=\"absmiddle\"></div>"
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
        template="vt_plugin_messages_panel.html",
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
    id_to_idx = {}

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
            nodes.append(Node(name = n.name, value = n.id, description = get_node_description(n, vmNames, vmInterfaces),
                              type = "Virtualized server", image = image_url, aggregate = agg,
                              # Extra parameters for VM nodes (will be used to show connections to switches)
                              vmNames = vmNames, vmInterfaces = vmInterfaces
                             )
                        )

            # For every interface of the server
            for j,inter in enumerate(n.ifaces.filter(isMgmt = False)):
                #first check datapathId exists.
                try:
                    switch_id = PluginCommunicator.get_object_id(slice, "openflow", "OpenFlowSwitch", name=inter.switchID)
                    port_id = PluginCommunicator.get_object_id(slice,"openflow", "OpenFlowInterface", switch=switch_id, port_num=inter.port)
                except Exception as e:
#                    print "[WARNING] Problem retrieving links insde plugin 'vt_plugin'. Details: %s" % str(e)
                    continue
                links.append(Link(source = str(n.id), target = str(switch_id),
                                 value = "rsc_id_" + str(port_id) + "-" + str(inter.ifaceName) + ":" + str(inter.port)
                                 )
                            )
    return [nodes, links]

#from expedient.common.utils.plugins.plugininterface import PluginInterface

#class Plugin(PluginInterface):
#    @staticmethod
def get_ui_data(slice):
    """
    Hook method. Use this very same name so Expedient can get the resources for every plugin.
    """
    ui_context = dict()
    try:
        ui_context['vms_list'] = get_vms_list(slice)
        ui_context['vt_aggs'] = get_vm_aggregates(slice)
        ui_context['nodes'], ui_context['links'] = get_nodes_links(slice)
    except Exception as e:
        print "[ERROR] Problem loading UI data for plugin 'vt_plugin'. Details: %s" % str(e)
    return ui_context

def remove_vm(request, vm_id):
    """
    Communicates with vt_plugin in order to delete a VM, given its ID.

    @param request HTTP request
    @param int Expedient identifier for VM
    @raise exception if VM could not be removed
    @return redirect to administration home
    """
    message_center_notification = "VM could not be removed"
    try:
        p = subprocess.Popen(["python","%s/vt_plugin/tests/deleteVM.py" % str(settings.PLUGINS_PATH),str(vm_id)], 
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if err:
            message_center_notification = str(err.split("\n")[-2])
            raise Exception
        else:
            DatedMessage.objects.post_message_to_user(
                "Administration info for vt_plugin: VM with id %s removed successfully" % str(vm_id),
                request.user, msg_type=DatedMessage.TYPE_SUCCESS)
    except:
        DatedMessage.objects.post_message_to_user(
            "Administration error for vt_plugin: %s" % message_center_notification,
            request.user, msg_type=DatedMessage.TYPE_ERROR)
    return HttpResponseRedirect(reverse("administration_home"))

def remove_all_vms(request):
    """
    Communicates with vt_plugin in order to delete all the VMs.

    @param request HTTP request
    @return redirect to administration home
    """
    message_center_notification = "could not delete every VM"
    try:
        p = subprocess.Popen(["python","%s/vt_plugin/tests/deleteAllVMs.py" % str(settings.PLUGINS_PATH)], 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if err:
            message_center_notification = str(err.split("\n")[-2])
            raise Exception
        else:
            DatedMessage.objects.post_message_to_user(
                "Administration info for vt_plugin: all VMs have been successfully deleted",
                request.user, msg_type=DatedMessage.TYPE_SUCCESS)
    except:
        DatedMessage.objects.post_message_to_user(
            "Administration error for vt_plugin: %s" % message_center_notification,
            request.user, msg_type=DatedMessage.TYPE_ERROR)
    return HttpResponseRedirect(reverse("administration_home"))

def get_administration_data(request):
    """
    Shows the administration panel for the plugin.

    @param request HTTP request
    @return string template data to shows administration features for this plugin
    """
    from vt_plugin.forms.remove_vm import RemoveVM

    if request.method == "POST":
        form_vm = RemoveVM(request.POST)
        if form_vm.is_valid():
            vm_id = form_vm.cleaned_data["vm_id"]
            return HttpResponseRedirect(reverse("remove_vm", args=[vm_id]))
    else:
        form_vm = RemoveVM()

    return simple.direct_to_template(
        request,
        template="vt_plugin_administration.html",
        extra_context={
            "form_stalled_vms": form_vm,
        },
    )
