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
from vt_plugin.models import VTServer, VtPlugin, xmlrpcServerProxy, resourcesHash


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
        
    if request.method == "GET":
        agg_form = VTAggregateForm(instance=aggregate)
        client_form = xmlrpcServerProxyForm(instance=client)
        
    elif request.method == "POST":
        agg_form = VTAggregateForm(
            data=request.POST, instance=aggregate)
        client_form = xmlrpcServerProxyForm(
            data=request.POST, instance=client)
        if client_form.is_valid() and agg_form.is_valid():
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
    
    available = aggregate.check_status() if agg_id else False
    return simple.direct_to_template(
        request,
        template="aggregate_crud.html",
        extra_context={
            "agg_form": agg_form,
            "client_form": client_form,
            "create": not agg_id,
            "aggregate": aggregate,
            #"available": available,
            "breadcrumbs": (
                ('Home', reverse("home")),
                ("%s Virtualization Aggregate" % ("Update" if agg_id else "Add"),
                 request.path),
            )
        },
    )
        

def askForAggregateResources(vtPlugin, projectUUID = 'None', sliceUUID = 'None'):
    "asks the VT AM for all the resources under it."
    serversInAggregate = []
    try:
        client = xmlrpclib.Server('https://'+vtPlugin.client.username+':'+vtPlugin.client.password+'@'+vtPlugin.client.url[8:])
    except Exception as e:
        print "Can't connect to server"
        print e
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
        print "Can't retrieve resources"
        print e
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
            print "Can't parse rspec"
            print e
            return
#        try:
#            for server in xmlClass.response.information.resources.server:
#                for vm in server.virtual_machine:
#                    VMmodel = Translator.VMtoModel(vm, vtPlugin.id, save="save")
#                    Translator.PopulateNewVMifaces(vm, VMmodel)
#                Translator.ServerClassToModel(server, vtPlugin.id)
#                serversInAggregate.append(server.uuid)
#            serversInExpedient  = VTServer.objects.filter(aggregate=vtPlugin.id).values_list('uuid', flat=True)
#            for s in serversInExpedient:
#                if s not in serversInAggregate:
#                    delServer = VTServer.objects.get(uuid = s)
#                    delServer.completeDelete()
#            return xmlClass
        try:
            for s in VTServer.objects.all():
                s.completeDelete()
            for server in xmlClass.response.information.resources.server:
                Translator.ServerClassToModel(server, vtPlugin.id)
                for vm in server.virtual_machine:
                    VMmodel = Translator.VMtoModel(vm, vtPlugin.id, save="save")
                    Translator.PopulateNewVMifaces(vm, VMmodel)
                VTServer.objects.get(uuid=server.uuid).setVMs()
            return xmlClass


        except Exception as e:
            print e
            rHashObject.hashValue = oldHashValue
            rHashObject.save()
    
