from vt_manager.communication.utils.XmlUtils import XmlHelper
import os
import sys
from vt_manager.models import *
from vt_manager.controller import *
from vt_manager.controller.policy.PolicyManager import PolicyManager
from vt_manager.communication.utils import *
from vt_manager.utils.ServiceThread import *
from vt_manager.controller.utils.Translator import Translator
import xmlrpclib, threading, logging, copy
from vt_manager.settings import ROOT_USERNAME, ROOT_PASSWORD, VTAM_URL
from vt_manager.utils.HttpUtils import HttpUtils
from django.db.models.query import QuerySet

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
		print serversChild
		return serversChild

	
	@staticmethod
	def createServerFromPOST(request, instance):
		from vt_manager.models.VTServer import VTServer
		controller = VTDriver.getDriver(HttpUtils.getFieldInPost(request,VTServer,"virtTech"))
		return controller.createOrUpdateServerFromPOST(request, instance)		


	@staticmethod
	def crudServerFromInstance(instance):
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
			print "[LEODEBUG] CRUDING IFACES"
			print "Name: "+str(newIface.name)+" id: "+str(newIface.id)
			print serverIfaces.filter(id = newIface.id)
			if serverIfaces.filter(id = newIface.id):
				for merda in serverIfaces.filter(id = newIface.id):
					print merda.id
			if not newIface.id==None and not serverIfaces.filter(id = newIface.id):
				print "add"
				server.addDataBridge(newIface.getName(),"",newIface.getSwitchID(),newIface.getPort())
			else:
				print "update"
				server.updateDataBridge(newIface)
		for id in ifacesToDelete:
			if id != '':
				server.deleteDataBridge(serverIfaces.get(id=id))

	@staticmethod
	def getServerById(id):
		from vt_manager.models.VTServer import VTServer
		try:
			return VTServer.objects.get(id=id).getChildObject()
		except:
			raise Exception("Server does not exist or id not unique")
		
	@staticmethod
	def getServerById(id):
		try:
			from vt_manager.models.VTServer import VTServer
			return VTServer.objects.get(id=id).getChildObject()
		except:
			raise Exception("Server does not exist or id not unique")

	def getVMsInServer(server):
		try:
			return server.vms.all()
		except:
			raise Exception("Could not recover server VMs")

	@staticmethod
	def getInstance():
		raise Exception("Driver Class cannot be instantiated")
	
	def getVMbyUUID(self,uuid):
		try:
			self.VMclass.objects.get(uuid = uuid)
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
		print "EN DRIVER"
		server.destroy()

	@staticmethod
	def propagateAction(vmId, action):
		try:
			from vt_manager.controller.dispatchers.ProvisioningDispatcher import ProvisioningDispatcher
			rspec = XmlHelper.getSimpleActionSpecificQuery(action)
			Translator.PopulateNewAction(rspec.query.provisioning.action[0], VTDriver.getVMbyId(vmId))
			ProvisioningDispatcher.processProvisioning(rspec.query.provisioning)
		except Exception as e:
			logging.error(e)
			
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
