import logging
from pprint import pformat

from django.views.generic import simple
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseNotAllowed,\
    HttpResponse
from django.forms.models import modelformset_factory
from django.core.urlresolvers import reverse
from django import forms
from django.db.models import Q
from django.views.generic.create_update import get_model_and_form_class

import copy
from vt_plugin.models import VtPlugin, VTServer, VM, Action
from vt_manager.communication.utils.XmlHelper import XmlHelper
from vt_plugin.utils.Translator import Translator
import xmlrpclib, uuid
from vt_plugin.utils.ServiceThread import *
from vt_plugin.controller.dispatchers.ProvisioningDispatcher import *
from vt_plugin.controller.VMcontroller.VMcontroller import *
from vt_plugin.utils.ServiceThread import *

def goto_create_vm(request, slice_id):
    """Show a page that allows user to add SSH s to the aggregate."""

    if request.method == "POST":
        if 'create_vms' in request.POST:
            server_id=request.POST['selected_server']
            return HttpResponseRedirect(reverse("virtualmachine_crud",
                                                args=[slice_id,server_id]))
        else:
            return HttpResponseRedirect("/")

#TODO: put the plugin code in plugin package!!!
def virtualmachine_crud(request, slice_id, server_id):

    """Show a page that allows user to add VMs to the VT server."""

    serv = get_object_or_404(VTServer, id = server_id)
    slice = get_object_or_404(Slice, id = slice_id)
    virtualmachines = VM.objects.filter(sliceId=slice.uuid)

    VMFormSet = modelformset_factory(
        VM, can_delete=False, 
        fields=["name", "memory","disc_image", "hdSetupType", "virtualizationSetupType"],
    )

    if request.method == "POST":
        if 'create_new_vms' in request.POST:
            # "Done" pressed ==> send xml to AM
            formset = VMFormSet(
                request.POST, queryset=virtualmachines)
            if formset.is_valid():
                instances = formset.save(commit=False)
                #create virtualmachines from received formulary
                VMcontroller.processVMCreation(instances, serv.uuid, slice, request.user)

                return HttpResponseRedirect(reverse("html_plugin_home",
                                                args=[slice_id]))
    else:
        formset = VMFormSet(queryset=VM.objects.none())

    return simple.direct_to_template(
        request, template="aggregate_add_virtualmachines.html",
        extra_context={"virtual_machines": virtualmachines,
                        "server_name":serv.name, "formset": formset,"slice":slice,
                        "breadcrumbs": (
                    ("Home", reverse("home")),
                    ("Project %s" % slice.project.name, reverse("project_detail", args=[slice.project.id])),
                    ("Slice %s" % slice.name, reverse("slice_detail", args=[slice_id])),
                    ("Resource visualization panel ", reverse("html_plugin_home", args=[slice_id])),
                    ("Create VM in Server %s" %serv.name, reverse("virtualmachine_crud", args=[slice_id, server_id])), 
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
    #return HttpResponseRedirect(reverse("html_plugin_home",args=[slice_id]))
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
                        <a href=\"JavaScript:void()\" onclick=\"handleVMaction("+str(slice.id)+","+str(vm.id)+",\'stop\')\">Stop</a> |\
                        <a href=\"JavaScript:void()\" onclick=\"handleVMaction("+str(slice.id)+","+str(vm.id)+",\'reboot\')\">Reboot</a>\
                        </div>"
                    elif  vm.state == "created (stopped)" :
                        actionsHtmlCode =\
						"<div>\
                        <a href=\"JavaScript:void()\" onclick=\"handleVMaction("+str(slice.id)+","+str(vm.id)+",\'start\')\">Start</a> |\
                        <a href=\"JavaScript:void()\" onclick=\"handleVMaction("+str(slice.id)+","+str(vm.id)+",\'delete\')\">Delete</a>\
                        </div>"
                    elif vm.state == "stopped" :
                        actionsHtmlCode =\
                        "<div>\
                        <a href=\"JavaScript:void()\" onclick=\"handleVMaction("+str(slice.id)+","+str(vm.id)+",\'start\')\">Start</a> |\
                        <a href=\"JavaScript:void()\" onclick=\"handleVMaction("+str(slice.id)+","+str(vm.id)+",\'delete\')\">Delete</a>\
                        </div>"
                    else:
                        actionsHtmlCode = "<div><img src=\"/static/media/img/loading.gif\" align=\"absmiddle\"></div>"
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

