from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import simple
from vt_manager.common.messaging.models import DatedMessage
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

#News
from vt_manager.controller.drivers.VTDriver import VTDriver
from vt_manager.utils.HttpUtils import HttpUtils
from vt_manager.models.NetworkInterface import NetworkInterface
from vt_manager.controller.dispatchers.forms.NetworkInterfaceForm import MgmtBridgeForm


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
		for vm in VTDriver.getVMsInServer(VTDriver.getServerById(server_id)):
			if vm.projectName not in vmProjects:
				vmProjects[vm.projectName] = vm.projectId
			if vm.sliceName not in vmSlices:
				vmSlices[vm.sliceName] = vm.sliceId
	except Exception as e:
		pass


	modelServer, form_classServer = HttpUtils.getForm(VTServer)
	modelIface, form_classIface = HttpUtils.getForm(NetworkInterface)
	IfaceFormSet = modelformset_factory(NetworkInterface)

	if server_id != None:
		server= get_object_or_404(modelServer, pk=server_id)
	else:
		server = None


	if request.method == "GET":
		formServer = form_classServer(instance=server)

		if server  != None:
			mgmt = server.getNetworkInterfaces().filter(isMgmt = True)
			if mgmt:
				mgmt = mgmt.get()
				formMgmtIface = MgmtBridgeForm({'mgmtBridge-name':mgmt.getName(), 'mgmtBridge-mac':mgmt.getMacStr()}, prefix ="mgmtBridge")
			else:
				formMgmtIface = MgmtBridgeForm(prefix ="mgmtBridge")
			
			data = server.getNetworkInterfaces().filter(isMgmt = False)
			if data:
				IfaceFormSet = modelformset_factory(NetworkInterface,extra = 0)
			ifaceformset = IfaceFormSet(queryset= data)

		else:
			formMgmtIface = MgmtBridgeForm(prefix ="mgmtBridge")
			ifaceformset = IfaceFormSet()
			

	elif request.method == "POST":
		formServer = form_classServer(request.POST)	
		print "LA FORM"
		print formServer
		ifaceformset = IfaceFormSet(request.POST)
		formMgmtIface = MgmtBridgeForm(request.POST, prefix ="mgmtBridge")
		
		if formServer.is_valid() and ifaceformset.is_valid() and formMgmtIface.is_valid():
			serverTemp = formServer.save(commit = False)
			print "HOAL"
			print server.uuid
			ifaces = ifaceformset.save(commit = False)
			try:
				VTDriver.crudServerFromInstance(server,serverTemp)
				VTDriver.setMgmtBridge(request, server)
				#VTDriver.crudDataBridgeFromInstance(server, ifaces,request.POST.getlist("DELETE"))
			except Exception as e:
				print e
			#	print "TUPU"
			#	from django.forms.util import ErrorList
			#	print "hola"
			#	formMgmtIface.errors["Error"] = ErrorList([u""+str(e)])
			#	print "chau"
			#	context = {"formServer": formServer, 'vmProjects': vmProjects, 'vmSlices': vmSlices,'ifaceformset' : ifaceformset, 'formMgmtIface' : formMgmtIface}
			#	if server_id != None: context["server"] = server

			#	return simple.direct_to_template(
			#			request,
			#			template="servers/servers_crud.html",
			#			extra_context=context
			#		)

				#return a alguna pagina y volver atras las transacciones
				
			return HttpResponseRedirect('/servers/admin/')
	else:
		return HttpResponseNotAllowed("GET", "POST")

	context = {"formServer": formServer, 'vmProjects': vmProjects, 'vmSlices': vmSlices,'ifaceformset' : ifaceformset, 'formMgmtIface' : formMgmtIface}
	if server_id != None: context["server"] = server

	return simple.direct_to_template(
		request,
		template="servers/servers_crud.html",
		extra_context=context,
	)

def admin_servers(request):
    
	if (not request.user.is_superuser):
        
		return simple.direct_to_template(request,
				template = 'not_admin.html',
				extra_context = {'user':request.user},
			) 
	
	servers = VTDriver.getAllServers()

	return simple.direct_to_template(
		request, template="servers/admin_servers.html",
		extra_context={"servers_ids": servers})

def delete_server(request, server_id):

	if (not request.user.is_superuser):
        
		return simple.direct_to_template(request,
				template = 'not_admin.html',
				extra_context = {'user':request.user},
		)
	if request.method == 'POST':
		try:
			VTDriver.deleteServer(VTDriver.getServerById(server_id))
			print "IN POSTTTT"
			return HttpResponseRedirect(reverse('dashboard'))

		except Exception as e:
			logging.error(e)
	elif request.method == 'GET':
		print "IN GETTTT"
		return simple.direct_to_template(request,
				template = 'servers/delete_server.html',
				extra_context = {'user':request.user, 'next':reverse("admin_servers")},
		)
	
def action_vm(request, server_id, vm_id, action):

	if (not request.user.is_superuser):
        
		return simple.direct_to_template(request,
			template = 'not_admin.html',
			extra_context = {'user':request.user},
		)

	if(action == 'list'):
          
		return simple.direct_to_template(
				request, template="servers/list_vm.html",
				extra_context={"vm": VTDriver.getVMbyId(vm_id)}
		)

	elif(action == 'check_status'):
		#XXX: Do this function if needed
		return simple.direct_to_template(
				request, template="servers/list_vm.html",
				extra_context={"vm": VM.objects.get(id = vm_id)}
		)

	else:
		VTDriver.PropagateAction(vm_id, action)
		#vm = VM.objects.get(id = vm_id)
		#rspec = XmlHelper.getSimpleActionSpecificQuery(action)
		#Translator.PopulateNewAction(rspec.query.provisioning.action[0], vm)
		#ProvisioningDispatcher.processProvisioning(rspec.query.provisioning)
    
	return HttpResponseRedirect(reverse('edit_server', args = [server_id]))

def servers_net_settings(request):
	pass
#    """Show a page for the user to add/edit the Netoworking settings for a VTServer """
#
#    if (not request.user.is_superuser):
#
#        return simple.direct_to_template(request,
#                            template = 'not_admin.html',
#                            extra_context = {'user':request.user},
#                        )
#    settings = VTServerNetworkingSettings.objects.all()
#
#    if len(settings) == 0:
#        settings_id = None 
#    elif len(settings) == 1:
#        settings_id = settings[0].id
#    else:
#        for i,s in enumerate(settings):
#            if i != 0:
#                s.delete()
#        settings_id = settings[0].id
#
#    return generic_crud(
#        request,
#        obj_id=settings_id,
#        model=VTServerNetworkingSettings,
#        template_object_name="settings",
#        template="servers/servers_net.html",
#        redirect = lambda inst: '/servers/net/update/'
#    )

def servers_net_update(request):
	pass
#    if (not request.user.is_superuser): 
#
#        return simple.direct_to_template(request,
#               template = 'not_admin.html',
#               extra_context = {'user':request.user},
#               )
#
#    settings = VTServerNetworkingSettings.objects.all()
#    if len(settings) == 0:
#        try: 
#            raise Exception("No Settings to update")
#        except:
#            pass
#
#    elif len(settings) == 1:
#        settings = settings[0]
#    else:
#        for i,s in enumerate(settings):
#            if i != 0:
#                s.delete()
#        settings = settings[0]
#
#    for server in VTServer.objects.all():
#        server.ipRange = settings.ipRange
#        server.mask = settings.mask
#        server.gw = settings.gw
#        server.dns1  = settings.dns1
#        server.dns2  = settings.dns2   
#        server.save() 
#
#    return HttpResponseRedirect('/servers/admin/')




'''
Networking point of entry
'''
from vt_manager.controller.networking.EthernetController import EthernetController
from vt_manager.controller.networking.Ip4Controller import Ip4Controller

NETWORKING_ACTION_ADD="add"
NETWORKING_ACTION_EDIT="edit"
NETWORKING_ACTION_DELETE="delete"
NETWORKING_ACTION_SHOW="show"
NETWORKING_POSSIBLE_ACTIONS=(NETWORKING_ACTION_ADD,NETWORKING_ACTION_DELETE,NETWORKING_ACTION_EDIT,NETWORKING_ACTION_SHOW,None)

def networkingDashboard(request):#,rangeId):
	
	
	template = "networking/index.html"
	return simple.direct_to_template(
		request,
		extra_context = {"section": "networking","subsection":"None"},
		template=template,
	)



def manageIp4Range(request,rangeId=None,action=None):
	if not action in NETWORKING_POSSIBLE_ACTIONS:
		raise Exception("Unknown action") 
	
	extra_context = {"section": "networking","subsection":"ip4"+str(action),}	
	if(action == None ):
		extra_context["ranges"] = Ip4Controller.listRanges()	

	template = "networking/ip4/index.html"
	return simple.direct_to_template(
			request,
			extra_context = extra_context, 
			template=template,
		)

def manageEthernet(request,rangeId=None,action=None):

	if not action in NETWORKING_POSSIBLE_ACTIONS:
		raise Exception("Unknown action") 

	#Define context	
	extra_context = {"section": "networking","subsection":"ethernet",}	


	
	#Add process	
	if (action == NETWORKING_ACTION_ADD):
		print "JJJJJJJJJJJJJJJJJJJJJJJJJJJJ"
		if request.method == "GET":
			print "gggggggggggggggggggggggggggg"
			#Show form
			return generic_crud(
				request,
				obj_id=None,
				model=MacRange,
				extra_context = extra_context, 
				template_object_name="form",
				template="networking/ethernet/rangeCrud.html",
				redirect = lambda inst: '/networking/ethernet/'
			)
			pass	
		elif request.method == "POST":
			try:
				print "fffffffffffffgggggggggggggggggggggggggggg"
				EthernetController.createRange(request)
			except Exception as e:
				print "tttttttttttttgggggggggggggggggggggggggggg"
				rangeId = None
				#Process creation query
				return generic_crud(
					request,
					obj_id=rangeId,
					model=MacRange,
					extra_context = extra_context, 
					template_object_name="form",
					template="networking/ethernet/rangeCrud.html",
					redirect = lambda inst: '/networking/ethernet/'
				)	
			
			
	#Show
	if ((action == None) or (action==NETWORKING_ACTION_SHOW)) and (not rangeId==None):
		model, form_class = HttpUtils.getForm(VTServer)
		return generic_crud(
			request,
			obj_id=rangeId,
			model=MacRange,
			extra_context = extra_context, 
			template_object_name="form",
			template="networking/ethernet/rangeCrud.html",
			redirect = lambda inst: '/networking/ethernet/'
			)	
		
	#Edit

	#Add excluded Ip
	
	#Release excluded Ip

	#Delete
	


	#Listing ranges
	extra_context["ranges"] = EthernetController.listRanges()
	return simple.direct_to_template(
			request,
			extra_context = extra_context, 
			template = "networking/ethernet/index.html",
		)



