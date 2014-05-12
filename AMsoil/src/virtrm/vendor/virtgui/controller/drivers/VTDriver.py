from vt_manager.communication.utils.XmlHelper import XmlHelper
import os
import sys
from vt_manager.models import *
from vt_manager.controller import *
from vt_manager.communication.utils import *
from vt_manager.utils.ServiceThread import *
import xmlrpclib, threading, logging, copy
from django.conf import settings
from django import forms
#from vt_manager.settings.settingsLoader import settings.ROOT_USERNAME, settings.ROOT_PASSWORD, settings.VTAM_IP,settings.VTAM_PORT
from vt_manager.utils.HttpUtils import HttpUtils
from django.db.models.query import QuerySet
from vt_manager.models.VirtualMachine import VirtualMachine
from vt_manager.controller.actions.ActionController import ActionController
from vt_manager.utils.ServiceThread import *
from django.core.exceptions import ValidationError
from vt_manager.utils.HttpUtils import HttpUtils

class VTDriver():


	CONTROLLER_TYPE_XEN = "xen"
	__possibleVirtTechs = [CONTROLLER_TYPE_XEN]

#	ServerClass = None
#	VMclass = None


	@staticmethod
	def getDriver(virtType):
		from vt_manager.controller.drivers.XenDriver import XenDriver
		if virtType == VTDriver.CONTROLLER_TYPE_XEN:
			return XenDriver.getInstance()

	@staticmethod
	def getAllDrivers():
		from vt_manager.controller.drivers.XenDriver import XenDriver

		drivers = []	
		for vt in Driver.__possibleVirtTechs:
			drivers.append(Driver.getDriver(vt))
		return drivers

	@staticmethod
	def getAllServers():
		from vt_manager.models.VTServer import VTServer
		servers = VTServer.objects.all()
		serversChild = []
		for server in servers:
			server = server.getChildObject()
			serversChild.append(server)
		return serversChild

	
	@staticmethod
	def createServerFromPOST(request, instance):
		from vt_manager.models.VTServer import VTServer
		controller = VTDriver.getDriver(HttpUtils.getFieldInPost(request,VTServer,"virtTech"))
		return controller.createOrUpdateServerFromPOST(request, instance)		


	@staticmethod
	def crudServerFromInstance(instance):
                # Password check. Ping is directly checked in the VTServer model
                s = xmlrpclib.Server(instance.agentURL)
                try:
                    s.pingAuth("ping",instance.agentPassword)
                except:
                    raise forms.ValidationError("Could not connect to server: password mismatch")
		controller = VTDriver.getDriver(instance.getVirtTech())
		return controller.crudServerFromInstance(instance)

	@staticmethod
	def setMgmtBridge(request, server):
		name = HttpUtils.getFieldInPost(request, "mgmtBridge-name")
		mac = HttpUtils.getFieldInPost(request, "mgmtBridge-mac")
		server.setMgmtBridge(name, mac)

	@staticmethod
	def crudDataBridgeFromInstance(server,ifaces, ifacesToDelete):
		serverIfaces = server.getNetworkInterfaces().filter(isMgmt = False)
		for newIface in ifaces:
			if newIface.id == None:# or not serverIfaces.filter(id = newIface.id):
				server.addDataBridge(newIface.getName(),"",newIface.getSwitchID(),newIface.getPort())
			else:
				server.updateDataBridge(newIface)
		for id in ifacesToDelete:
			if id != '':
				try:
					server.deleteDataBridge(serverIfaces.get(id=id))
				except Exception as e:
					raise ValidationError(str(e))

	@staticmethod
	def getServerById(id):
		from vt_manager.models.VTServer import VTServer
		try:
			return VTServer.objects.get(id=id).getChildObject()
		except:
			raise Exception("Server does not exist or id not unique")
		
	@staticmethod
	def getServerByUUID(uuid):
		try:
			from vt_manager.models.VTServer import VTServer
			return VTServer.objects.get(uuid=uuid).getChildObject()
		except:
			raise Exception("Server does not exist or id not unique")

	@staticmethod
	def getVMsInServer(server):
		try:
			return server.vms.all()
		except:
			raise Exception("Could not recover server VMs")

	@staticmethod
	def getInstance():
		raise Exception("Driver Class cannot be instantiated")
	
	@staticmethod	
	def getVMbyUUID(uuid):
		try:
			return VirtualMachine.objects.get(uuid = uuid).getChildObject()
		except:
			raise

	@staticmethod
	def getVMbyId(id):
		try:
			return VirtualMachine.objects.get(id = id).getChildObject()
		except:
			raise

	def deleteVM():
		raise Exception("Method not callable for Driver Class")

	def getServerAndCreateVM(): 
		raise Exception("Method not callable for Driver Class")
	

	def getServers(self):
		return self.ServerClass.objects.all()

	@staticmethod
	def deleteServer(server):	
		server.destroy()

#	@staticmethod
#	def propagateAction(vmId, serverUUID, action):
#		try:
#			from vt_manager.controller.dispatchers.ProvisioningDispatcher import ProvisioningDispatcher
#			rspec = XmlHelper.getSimpleActionSpecificQuery(action, serverUUID)
#			#MARC XXX
#			#Translator.PopulateNewAction(rspec.query.provisioning.action[0], VTDriver.getVMbyId(vmId))
#			ProvisioningDispatcher.processProvisioning(rspec.query.provisioning)
#		except Exception as e:
#			logging.error(e)
			
	@staticmethod
	def manageEthernetRanges(request, server, totalMacRanges):

		justUnsubscribed = []
		for macRange in server.getSubscribedMacRangesNoGlobal():
			try:
				request.POST['subscribe_'+str(macRange.id)]
			except:
				server.unsubscribeToMacRange(macRange)
				justUnsubscribed.append(macRange)

		for macRange in totalMacRanges:
			if macRange not in (server.getSubscribedMacRangesNoGlobal() or justUnsubscribed):
				try:
					request.POST['subscribe_'+str(macRange.id)]
					server.subscribeToMacRange(macRange)
				except:
					pass

	@staticmethod
	def manageIp4Ranges(request, server, totalIpRanges):

		justUnsubscribed = []
		for ipRange in server.getSubscribedIp4RangesNoGlobal():
			#if not ipRange.getIsGlobal():
			try:
				request.POST['subscribe_'+str(ipRange.id)]
			except:
				server.unsubscribeToIp4Range(ipRange)
				justUnsubscribed.append(ipRange)

		for ipRange in totalIpRanges:
			if ipRange not in (server.getSubscribedIp4RangesNoGlobal() or justUnsubscribed):
				try:
					request.POST['subscribe_'+str(ipRange.id)]
					server.subscribeToIp4Range(ipRange)
				except Exception as e:
					pass

	@staticmethod
	def PropagateActionToProvisioningDispatcher(vm_id, serverUUID, action):
		from vt_manager.communication.utils.XmlHelper import XmlHelper
		from vt_manager.controller.dispatchers.xmlrpc.DispatcherLauncher import DispatcherLauncher
		vm = VirtualMachine.objects.get(id=vm_id).getChildObject()
		rspec = XmlHelper.getSimpleActionSpecificQuery(action, serverUUID)
		ActionController.PopulateNewActionWithVM(rspec.query.provisioning.action[0], vm)
		ServiceThread.startMethodInNewThread(DispatcherLauncher.processXmlQuery, rspec)
