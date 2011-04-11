from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import simple
from vt_manager.common.messaging.models import DatedMessage
from vt_manager.models import VTServer
from django.views.generic import list_detail, simple
from django.views.generic.create_update import apply_extra_context
from vt_manager.models import *
from vt_manager.communication.utils.XmlUtils import XmlHelper
from vt_manager.controller.dispatchers.ProvisioningDispatcher import *
from vt_manager.controller.utils.Translator import *
import uuid, time, logging
from django.template import loader, RequestContext
from django.core.xheaders import populate_xheaders
from django.contrib import messages
from django.utils.translation import ugettext

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
    vmProjects = {}
    vmSlices = {}
    try: 
        server = VTServer.objects.get(id = server_id)
        for vm in server.vms.all():
            if vm.projectName not in vmProjects:
                vmProjects[vm.projectName] = vm.projectId
            if vm.projectName not in vmProjects:
                vmSlices[vm.sliceName] = vm.sliceId
    except:
        pass

            
    return server_generic_crud(
        request,
        obj_id=server_id,
        model=VTServer,
        extra_context = {'vmProjects': vmProjects, 'vmSlices': vmSlices},
        template_object_name="server",
        template="servers/servers_crud.html",
        redirect = lambda inst: '/servers/admin/'
    )


from django.shortcuts import get_object_or_404
from django.views.generic.create_update import get_model_and_form_class
from django.views.generic import simple
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from vt_manager.common.messaging.models import DatedMessage

def server_generic_crud(request, obj_id, model, template, redirect,
                 extra_context={}, form_class=None,
                 template_object_name="object", pre_save=None,
                 post_save=None, success_msg=None):

    ifaceforms = []
    model, form_class = get_model_and_form_class(model, form_class)
    modelIface, form_classIface = get_model_and_form_class(VTServerIface, None)
    print modelIface
    print form_classIface
    if obj_id != None:
        instance = get_object_or_404(model, pk=obj_id)
    else:
        instance = None

    if request.method == "GET":
        form = form_class(instance=instance)
        if instance != None:
            for iface in instance.ifaces.all():
                ifaceforms.append(form_classIface(instance = iface))
        else:
            ifaceforms.append(form_classIface(instance = None)) 
    elif request.method == "POST":
        postData =  request.POST.copy()
        form = form_class(request.POST, instance=instance)
        if instance != None :
            #for iface in instance.ifaces.all():
            for i in range(0,len(request.POST.getlist('ifaceName'))):
                ifaceforms.append(form_classIface(
                                                    {
                                                    'ifaceName': request.POST.getlist('ifaceName')[i], 
                                                    'switchID': request.POST.getlist('switchID')[i], 
                                                    'port': request.POST.getlist('port')[i]
                                                    }, 
                                                    instance = None
                                                )
                                )
        else:
            ifaceforms.append(form_classIface(request.POST, instance = None))
        if form.is_valid():
            instance = form.save(commit=False)
            if pre_save: pre_save(instance, obj_id == None)
            instance.save()
            if post_save: post_save(instance, obj_id == None)
            for ifaceform in ifaceforms:
                if ifaceform.is_valid():
                    ifaceTemp = ifaceform.save(commit= False)
                    if instance.ifaces.filter(ifaceName = ifaceTemp.ifaceName):
                        ifaceTemp2 = instance.ifaces.get(ifaceName = ifaceTemp.ifaceName) 
                        ifaceTemp2.ifaceName = ifaceTemp.ifaceName
                        ifaceTemp2.port = ifaceTemp.port
                        ifaceTemp2.switchID = ifaceTemp.switchID
                        ifaceTemp2.save() 
                    else:
                        iface = ifaceform.save(commit=True)
                        instance.ifaces.add(iface)
            form.save_m2m()
            if success_msg:
                DatedMessage.objects.post_message_to_user(
                    success_msg(instance), request.user,
                    msg_type=DatedMessage.TYPE_SUCCESS)
            return HttpResponseRedirect(redirect(instance))
    else:
        return HttpResponseNotAllowed("GET", "POST")

    context = {"form": form, "ifaceforms": ifaceforms}
    context.update(extra_context)
    if obj_id != None: context[template_object_name] = instance

    return simple.direct_to_template(
        request,
        template=template,
        extra_context=context,
        form=form,
        ifaceforms = ifaceforms,
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
    Display a confirmation page and delete the server.
    """
    def delete_VTServer_object(request, model, post_delete_redirect, object_id=None,
        template_name=None,
        template_loader=loader, extra_context=None, login_required=False,
        context_processors=None, template_object_name='object'):

        if extra_context is None: extra_context = {}
        if login_required and not request.user.is_authenticated():
            return redirect_to_login(request.path)

        obj = get_object_or_404(model, id= object_id)
        if request.method == 'POST':
            for iface in obj.ifaces.all():
                iface.delete()
            obj.delete()
            msg = ugettext("The %(verbose_name)s was deleted.") %\
                                        {"verbose_name": model._meta.verbose_name}
            messages.success(request, msg, fail_silently=True)
            return HttpResponseRedirect(post_delete_redirect)
        else:
            if not template_name:
                template_name = "%s/%s_confirm_delete.html" % (model._meta.app_label, model._meta.object_name.lower())
            t = template_loader.get_template(template_name)
            c = RequestContext(request, {
                template_object_name: obj,
            }, context_processors)
            apply_extra_context(extra_context, c)
            response = HttpResponse(t.render(c))
            populate_xheaders(request, response, model, getattr(obj, obj._meta.pk.attname))
            return response

    if (not request.user.is_superuser):
        
        return simple.direct_to_template(request,
                            template = 'not_admin.html',
                            extra_context = {'user':request.user},
                        )
 
    next = reverse("admin_servers")
    req = delete_VTServer_object(
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
