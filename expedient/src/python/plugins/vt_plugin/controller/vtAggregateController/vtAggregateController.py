from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import simple
from expedient.common.utils.views import generic_crud
from expedient.common.messaging.models import DatedMessage
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.clearinghouse.utils import post_message_to_current_user
from vt_plugin.controller.vtAggregateController.forms.forms import *
from expedient.common.permissions.shortcuts import give_permission_to,\
    must_have_permission
from vt_manager.communication.utils.XmlHelper import XmlHelper
import logging, xmlrpclib, os
from vt_plugin.utils.Translator import Translator
from vt_plugin.models import VTServer, VtPlugin, xmlrpcServerProxy, resourcesHash, VM, Action


def aggregate_crud(request, agg_id=None):
    '''
    Create/update an Virtualization Aggregate.
    '''
    if agg_id != None:
        aggregate = get_object_or_404(VtPlugin, pk=agg_id)
        client = aggregate.client
    else:
        aggregate = None
        client = None

    extra_context_dict = {}
    errors = ""

    if request.method == "GET":
        agg_form = VTAggregateForm(instance=aggregate)
        client_form = xmlrpcServerProxyForm(instance=client)
        
    elif request.method == "POST":
        agg_form = VTAggregateForm(
            data=request.POST, instance=aggregate)
        client_form = xmlrpcServerProxyForm(
            data=request.POST, instance=client)

        if client_form.is_valid() and agg_form.is_valid():
            # Ping is tried after every field check
            client = client_form.save(commit=False)
            s = xmlrpclib.Server('https://'+client.username+':'+client.password+'@'+client.url[8:])
            try:
                s.ping('ping')
            except:
                errors = "Could not connect to server: username, password or url are not correct"
                DatedMessage.objects.post_message_to_user(
                    errors, user=request.user, msg_type=DatedMessage.TYPE_ERROR,
                )
                extra_context_dict['errors'] = errors
#                return HttpResponseRedirect(request.path) 

            if not errors:
                client = client_form.save()
                aggregate = agg_form.save(commit=False)
                aggregate.client = client
                aggregate.save()
                agg_form.save_m2m()
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
                    "Successfully created/updated aggregate %s" % aggregate.name,
                    user=request.user, msg_type=DatedMessage.TYPE_SUCCESS,
                )
                return HttpResponseRedirect("/")
    else:
        return HttpResponseNotAllowed("GET", "POST")

    if not errors:
        extra_context_dict['available'] = aggregate.check_status() if agg_id else False

    # Updates the dictionary with the common fields
    extra_context_dict.update({
            "agg_form": agg_form,
            "client_form": client_form,
            "create": not agg_id,
            "aggregate": aggregate,
            # Previously commented
            # "available": available,
            "breadcrumbs": (
                ('Home', reverse("home")),
                ("%s Virtualization Aggregate" % ("Update" if agg_id else "Add"),
                 request.path),
            )
        })

    return simple.direct_to_template(
        request,
        template="vt_plugin_aggregate_crud.html",
        extra_context=extra_context_dict
    )
        

def askForAggregateResources(vtPlugin, projectUUID = 'None', sliceUUID = 'None'):
    "asks the VT AM for all the resources under it."
    serversInAggregate = []
    try:
        client = xmlrpclib.Server('https://'+vtPlugin.client.username+':'+vtPlugin.client.password+'@'+vtPlugin.client.url[8:])
    except Exception as e:
        print "Can't connect to server: %s" % str(e)
        return
    
    try:
        rHashObject =  resourcesHash.objects.get(vtamID = vtPlugin.id, projectUUID = projectUUID, sliceUUID = sliceUUID)
    except:
        rHashObject = resourcesHash(hashValue = '0', vtamID = vtPlugin.id, projectUUID= projectUUID, sliceUUID = sliceUUID)
        rHashObject.save()
    try:
        remoteHashValue ,resourcesString = client.listResources(rHashObject.hashValue, projectUUID, sliceUUID)
        print remoteHashValue
    except Exception as e:
        print "Can't retrieve resources: %s" % str(e)
        return

    if remoteHashValue == rHashObject.hashValue:
        print "Same HASH, no changes in resources"
        return
    else:
        print remoteHashValue
        oldHashValue = rHashObject.hashValue
        rHashObject.hashValue = remoteHashValue
        rHashObject.save() 
        try:
            xmlClass = XmlHelper.parseXmlString(resourcesString)
        except Exception as e:
            print "Can't parse rspec: %s" % str(e)
            return
        try:
            for server in xmlClass.response.information.resources.server:
                vmsInAggregate = []
                for vm in server.virtual_machine:
                    #Translate and register VM present in the AM
                    VMmodel = Translator.VMtoModel(vm, vtPlugin.id, save="save")
                    Translator.PopulateNewVMifaces(vm, VMmodel)
                    vmsInAggregate.append(VMmodel.uuid)
                #Translate The whole server with the vms updated. There may be still VMs in the models
                #which are not in the AM
                serverModel = Translator.ServerClassToModel(server, vtPlugin.id)
                # Delete VMs in the model that are not in the linked to the server in the AM
                for vmuuid in serverModel.vms.filter(sliceId=sliceUUID, projectId=projectUUID).values_list('uuid', flat=True):                

                    try:
                        action_present = False
                        action_create =  Action.objects.get(vm__uuid=vmuuid)
                        if action_create.type=="create" and action_create.status=="SUCCESS":
                            action_present = True
                    except:
                        print "VM Manager returned a VM which has not provisioning create action associated"
                    if vmuuid not in vmsInAggregate and action_present:
                        vmToDelete = VM.objects.get(uuid=vmuuid)
                        serverModel.vms.remove(vmToDelete)
                        vmToDelete.completeDelete() 
                serversInAggregate.append(server.uuid)
                #Update VMs in the server model
                serverModel.setVMs()
            serversInExpedient  = VTServer.objects.filter(aggregate=vtPlugin.id).values_list('uuid', flat=True)
            #Delete servers in Expedient that are not any more in the AM. VMs in that server included
            for s in serversInExpedient:
                if s not in serversInAggregate:
                    delServer = VTServer.objects.get(uuid = s)
                    delServer.completeDelete()
                
            return xmlClass


        except Exception as e:
            print e
            rHashObject.hashValue = oldHashValue
            rHashObject.save()
   
