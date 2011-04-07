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
from vt_manager.communication.utils.XmlUtils import XmlHelper
from vt_plugin.utils.Translator import Translator
import xmlrpclib, uuid
from vt_plugin.utils.ServiceThread import *
from vt_plugin.controller.dispatchers.ProvisioningDispatcher import *
from vt_plugin.controller.VMcontroller.VMcontroller import *

def goto_create_vm(request, slice_id):
    """Show a page that allows user to add SSH s to the aggregate."""
    print "UI/HTML/views.py --> goto_create_vm"

    if request.method == "POST":
        if 'create_vms' in request.POST:
            server_id=request.POST['server_id']
            return HttpResponseRedirect(reverse("virtualmachine_crud",
                                                args=[slice_id,server_id]))
        #TODO: implement "Delete VM" checkbutton


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
        fields=["name", "memory","disc_image", "hd_setup_type", "virtualization_setup_type"],
    )

    if request.method == "POST":
        if 'create_new_vms' in request.POST:
            # "Done" pressed ==> send xml to AM
            formset = VMFormSet(
                request.POST, queryset=virtualmachines)
            print "VIRTUALMACHINE_CRUD BEFORE IS_VALID"
            if formset.is_valid():
                print "VIRTUALMACHINE_CRUD AFTER IS_VALID"
                instances = formset.save(commit=False)
                #create virtualmachines from received formulary
                VMcontroller.processVMCreation(instances, serv.uuid, slice)

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
                                        ("HTML UI - Choose Resources", reverse("html_plugin_home", args=[slice_id])),
            ),
        })


def manage_vm(request, slice_id, vm_id, action_type):

    "Manages the actions executed over VMs at url manage resources."

#    #manage virtual machines
#    VM_Manager.manageVM(slice_id, vm_id, action_type)

    vm = VM.objects.get(id = vm_id)

    rspec = XmlHelper.getSimpleActionSpecificQuery(action_type)
     
    Translator.PopulateNewAction(rspec.query.provisioning.action[0], vm)

    ProvisioningDispatcher.processProvisioning(rspec.query.provisioning)

    #set VM state to on queue
    vm.state = "on queue"
    vm.save()

    #go to manage resources again
    return HttpResponseRedirect(reverse("html_plugin_home",
                                        args=[slice_id]))
