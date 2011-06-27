from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import simple
from vt_manager.common.utils.views import generic_crud
from vt_manager.common.messaging.models import DatedMessage
from vt_manager.models import VTServer
from django.views.generic import list_detail, create_update, simple
from vt_manager.models import *
from vt_manager.communication.utils.XmlUtils import XmlHelper
from vt_manager.controller.dispatchers.ProvisioningDispatcher import *
from vt_manager.controller.utils.Translator import *
import uuid
import time
import logging

def userIsIslandManager(request):

    if (not request.user.is_superuser):
        
        return simple.direct_to_template(request,
                            template = 'not_admin.html',
                            extra_context = {'user':request.user},
                        )

def servers_crud(request, server_id=None):
    """Show a page for the user to add/edit an  VTServer """

    if (not request.user.is_superuser):
        
        return simple.direct_to_template(request,
                            template = 'not_admin.html',
                            extra_context = {'user':request.user},
                        )

    return generic_crud(
        request,
        obj_id=server_id,
        model=VTServer,
        template_object_name="server",
        template="servers/servers_crud.html",
        redirect = lambda inst: '/dashboard'
    )


    
def admin_servers(request):
    
    if (not request.user.is_superuser):
        
        return simple.direct_to_template(request,
                            template = 'not_admin.html',
                            extra_context = {'user':request.user},
                        ) 

    servers_ids = VTServer.objects.all()

    return simple.direct_to_template(
        request, template="servers/admin_servers.html",
        extra_context={"servers_ids": servers_ids})

def delete_server(request, server_id):
    """
    Display a confirmation page (NOT IMLPEMENTED YET: then stop all slices) and delete the aggregate.
    """
    if (not request.user.is_superuser):
        
        return simple.direct_to_template(request,
                            template = 'not_admin.html',
                            extra_context = {'user':request.user},
                        )
 
    next = reverse("admin_servers")
    server = get_object_or_404(VTServer, id=server_id)
    req = create_update.delete_object(
        request,
        model=VTServer,
        post_delete_redirect=next,
        object_id=server_id,
        extra_context={"next": next},
        template_name="servers/delete_server.html",
    )
    return req

def action_vm(request, server_id, vm_id, action):

    if (not request.user.is_superuser):
        
        return simple.direct_to_template(request,
                            template = 'not_admin.html',
                            extra_context = {'user':request.user},
                        )

    if(action == 'list'):
          
        return simple.direct_to_template(
        request, template="servers/list_vm.html",
        extra_context={"vm": VM.objects.get(id = vm_id)})

    elif(action == 'check_status'):
        #check_state
        return simple.direct_to_template(
        request, template="servers/list_vm.html",
        extra_context={"vm": VM.objects.get(id = vm_id)})

    else:
        vm = VM.objects.get(id = vm_id)
        rspec = XmlHelper.getSimpleActionSpecificQuery(action)
        Translator.PopulateNewAction(rspec.query.provisioning.action[0], vm)
        ProvisioningDispatcher.processProvisioning(rspec.query.provisioning)
    
        #TODO: Very ugly way to wait until the responses arrived and the state of teh VM is refreshed without having to reload the page
        time.sleep(3)
        return HttpResponseRedirect(reverse('edit_server', args = [server_id]))
