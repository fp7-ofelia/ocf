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
from vt_manager.communication.utils.XmlUtils import XmlHelper
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
            
            #check if virtualization aggregate manager is available
            try:
                print 'DIRECCION: '+'https://'+aggregate.client.username+':'+aggregate.client.password+'@'+aggregate.client.url[8:]
                temp_client = xmlrpclib.Server('https://'+aggregate.client.username+':'+aggregate.client.password+'@'+aggregate.client.url[8:])                
                print 'aggregate_crud --> server instance OK'
            except Exception as e:
                print 'aggregate_crud --> server instance KO'
                print "Can't connect to server"
                print e
                return
                
            #TODO: finish check by calling the (yet not implemented) "ping" function in VT_AM
            #meanwhile we check connection through listResources service call
            try:
                rspec = temp_client.listResources()
                aggregate.available = True
                print "aggregate_crud --> connection OK ; aggregate.available = True"
            except Exception as e:
                aggregate.available = False
                print "aggregate_crud --> connection OK; aggregate.available = False"                                            

            
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
        

def askForAggregateResources(vtPlugin, serverUUID = 'None', projectUUID = 'None', sliceUUID = 'None'):

    "asks the VT AM for all the resources under it."

    try:
        client = xmlrpclib.Server('https://'+vtPlugin.client.username+':'+vtPlugin.client.password+'@'+vtPlugin.client.url[8:])
    except Exception as e:
        print "Can't connect to server"
        print e
        return
    
    try:
        rHashObject =  resourcesHash.objects.get(serverUUID = serverUUID, projectUUID = projectUUID, sliceUUID = sliceUUID)
    except:
        rHashObject = resourcesHash(hashValue = 0, serverUUID = serverUUID, projectUUID= projectUUID, sliceUUID = sliceUUID)
        rHashObject.save()

    try:
        hashV ,rspec = client.listResources(rHashObject.hashValue, 'None', projectUUID, sliceUUID)
    except Exception as e:
        print "Can't retrieve resources"
        print e
        return
    print rspec

    if hashV == rHashObject.hashValue:
        return
    else:
        rHashObject.hashValue = hashV
        rHashObject.save() 
        try:
            xmlClass = XmlHelper.parseXmlString(rspec)
        except Exception as e:
            print "Can't parse rspec"
            print e
            return
    
        for server in xmlClass.response.information.resources.server:
            for vm in server.virtual_machine:
                Translator.PopulateNewVMifaces(vm, Translator.VMtoModel(vm, save="save"))
            Translator.ServerClassToModel(server, vtPlugin.id)
    
        return xmlClass
    
