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
from vt_manager.controller.dispatchers.ProvisioningDispatcher import ProvisioningDispatcher
from vt_manager.utils.HttpUtils import HttpUtils


class VTDriver():


	CONTROLLER_TYPE_XEN = "xen"
	__possibleVirtTechs = [CONTROLLER_TYPE_XEN]

	ServerClass = None
	VMclass = None


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
			rspec = XmlHelper.getSimpleActionSpecificQuery(action)
			Translator.PopulateNewAction(rspec.query.provisioning.action[0], VTDriver.getVMbyId(vmId))
			ProvisioningDispatcher.processProvisioning(rspec.query.provisioning)
		except Exception as e:
			logging.error(e)
			
