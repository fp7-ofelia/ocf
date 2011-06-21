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
    print "UI/HTML/views.py --> goto_create_vm"

    if request.method == "POST":
        if 'create_vms' in request.POST:
            server_id=request.POST['server_id']
            return HttpResponseRedirect(reverse("virtualmachine_crud",
                                                args=[slice_id,server_id]))
        else:
            return HttpResponseRedirect("/")

#TODO: put the plugin code in plugin package!!!
def virtualmachine_crud(request, slice_id, server_id):

    """Show a page that allows user to add VMs to the VT server."""

    print "VIRTUALMACHINE_CRUD"
    serv = get_object_or_404(VTServer, id = server_id)
    #server_name = serv.name
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

    #set VM state to on queue
    vm.state = "on queue"
    vm.save()

    #go to manage resources again
    return HttpResponseRedirect(reverse("html_plugin_home",args=[slice_id]))


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
                        <a href=\"/vt_plugin/manage_vm/"+str(slice.id)+"/"+str(vm.id)+"/reboot/\">Reboot</a> |\
                        <a href=\"/vt_plugin/manage_vm/"+str(slice.id)+"/"+str(vm.id)+"/stop/\">Stop</a>\
                        </div>"
                    elif  vm.state == "created (stopped)" :
                        actionsHtmlCode =\
                        "<div>\
                        <a href=\"/vt_plugin/manage_vm/"+str(slice.id)+"/"+str(vm.id)+"/start/\">Start</a> |\
                        <a href=\"/vt_plugin/manage_vm/"+str(slice.id)+"/"+str(vm.id)+"/delete/\">Delete</a>\
                        </div>"
                    elif vm.state == "stopped" :
                        actionsHtmlCode =\
                        "<div>\
                        <a href=\"/vt_plugin/manage_vm/"+str(slice.id)+"/"+str(vm.id)+"/start/\">Start</a> |\
                        <a href=\"/vt_plugin/manage_vm/"+str(slice.id)+"/"+str(vm.id)+"/delete/\">Delete</a>\
                        </div>"
                    else:
                        actionsHtmlCode = "<div></div>"
                    vmsActionsHtmlCodes[str(vm.id)] = actionsHtmlCode
                    try:
                        vmsIP[str(vm.id)]= vm.ifaces.get(isMgmt = True).ip
                    except:
                        pass
        
    data = simplejson.dumps({'status': vmsStatus, 'actions': vmsActionsHtmlCodes, 'ips': vmsIP,})
    response = HttpResponse(data)
    return response
