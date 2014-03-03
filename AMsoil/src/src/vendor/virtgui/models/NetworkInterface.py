from django.db import models
from django.contrib import auth
from threading import Lock
import inspect 

from vt_manager.utils.MutexStore import MutexStore
from vt_manager.models.MacRange import MacRange
from vt_manager.models.MacSlot import MacSlot
from vt_manager.models.Ip4Slot import Ip4Slot
from vt_manager.models.Ip4Range import Ip4Range
from vt_manager.utils.EthernetUtils import EthernetUtils
from vt_manager.common.utils import validators

class NetworkInterface(models.Model):

	"""Network interface model"""

	class Meta:
		"""Meta Class for your model."""
		app_label = 'vt_manager'

	'''Generic parameters'''
	name = models.CharField(max_length = 128, default="", verbose_name = "Name", validators=[validators.resourceNameValidator]) #check if bank = True and null = True are required
	mac = models.ForeignKey('MacSlot', blank = True, null = False, editable = False, verbose_name = "Mac address", validators=[EthernetUtils.checkValidMac],related_name="interface")
	ip4s = models.ManyToManyField('Ip4Slot', blank = True, null = True, editable = False, verbose_name = "IP4 addresses", related_name = "Interface")
	isMgmt = models.BooleanField(verbose_name="Mgmt interface",default=0, editable = False)
	isBridge = models.BooleanField(verbose_name="bridge interface",default=0, editable = False)

	'''Interfaces connectivy'''
	connectedTo =  models.ManyToManyField('NetworkInterface', blank = True, null = False, editable = False, verbose_name = "Interfaces connected", related_name= "serverBridge")

	'''Physical connection details for bridged interfaces'''	
	#switchID = models.CharField(max_length = 128, default="", blank = True, null=True, verbose_name = "Switch ID",validators=[checkBlank])
	switchID = models.CharField(max_length = 23, default="", blank = True, null=True, verbose_name = "Switch ID", validators=[validators.datapathValidator])
	port = models.IntegerField( blank = True, null=True, verbose_name = "Switch Port", validators=[validators.numberValidator])
	idForm = models.IntegerField(blank = True, null=True, editable = False)

	'''Defines soft or hard state of the VM'''	
	doSave = True

	##Constructor
	'''Interface constructor '''
	@staticmethod
	def constructor(name,macStr,macObj,switchID,port,ip4Obj,isMgmt=False,isBridge=False,save=True):
		self = NetworkInterface()	
		try:
			self.name = name;

			if macObj == None:
				self.mac = MacSlot.macFactory(None,macStr)	
			else:
				if not isinstance(macObj,MacSlot):
					raise Exception("Cannot construct NetworkInterface with a non MacSlot object as parameter")
				self.mac = macObj
			self.isMgmt = isMgmt

			'''Connectivity'''
			if isBridge:
				self.isBridge = isBridge
				self.switchID = switchID 
				self.port = port
			if not ip4Obj == None:
				if not isinstance(ip4Obj,Ip4Slot):
						raise Exception("Cannot construct NetworkInterface with a non Ip4Slot object as parameter")
				else:		
					self.save()
					self.ip4s.add(ip4Obj)			

			self.doSave = save
			if save:
				self.save()
		except Exception as e:
			print e
#			self.delete()
			raise e

		return self

	def update(self,name,macStr,switchID,port,save=True):
		try:
			self.setName(name)
			self.setMacStr(macStr)
			self.setSwitchID(switchID)
			self.setPort(port)
			if save:
				self.save()
		except Exception as e:
			print e
			raise e

	##Private methods
	def autoSave(self):
		if self.doSave:
			self.save()
	##Public methods
	def getLockIdentifier(self):
		#Uniquely identifies object by a key
		return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)
 
	def getName(self):
		return self.name
	def setName(self,name):
		self.name=name
		self.autoSave()
	def getMacStr(self):
		return self.mac.mac
	def setMacStr(self,macStr):
		#oldMac =self.mac 
		#self.mac = MacSlot.macFactory(None,macStr)	
		#if not oldMac == None:
		#	self.mac.destroy()
		#self.autoSave()
		#return
		self.mac.setMac(macStr)
		self.autoSave()

	def setPort(self,port):
		self.port = port

	def getPort(self):
		return self.port

	def setSwitchID(self, switchID):
		self.switchID = switchID

	def getSwitchID(self):
		return self.switchID

	def getNumberOfConnections(self):
		return self.connectedTo.all().count()
	
	def attachInterfaceToBridge(self,interface):
		if not self.isBridge:
			raise Exception("Cannot attach interface to a non-bridged interface")
			
		if not isinstance(interface,NetworkInterface):
			raise Exception("Cannot attach interface; object type unknown -> Must be NetworkInterface instance")
		self.connectedTo.add(interface)	
		self.autoSave()


	def detachInterfaceToBridge(self,interface):
		if not self.isBridge:
			raise Exception("Cannot detach interface from a non-bridged interface")
			
		if not isinstance(interface,NetworkInterface):
			raise Exception("Cannot detach interface; object type unknown -> Must be NetworkInterface instance")
		self.connectedTo.remove(interface)	
		self.autoSave()

	def addIp4ToInterface(self,ip4):
		if not self.isMgmt:
			raise Exception("Cannot add IP4 to a non mgmt interface")
		if not isinstance(ip4,Ip4Slot):
			raise Exception("Cannot add IP4 to interface; object type unknown -> Must be IP4Slot instance")

		self.ip4s.add(ip4)	
		self.autoSave()


	def removeIp4FromInterface(self,ip4):
		if not isinstance(ip4,Ip4Slot):
			raise Exception("Cannot remove IP4 to interface; object type unknown -> Must be IP4Slot instance")
		if not self.isMgmt:
			raise Exception("Cannot add IP4 to a non mgmt interface")
		self.ip4s.remove(ip4)	
		self.autoSave()


	def destroy(self):
		with MutexStore.getObjectLock(self.getLockIdentifier()):
			if self.getNumberOfConnections():
				raise Exception("Cannot destroy a bridge which has enslaved interfaces")
			for ip in self.ip4s.all():
				ip.destroy()
			self.mac.destroy()	
			self.delete()


	'''Server interface factories'''
	@staticmethod
	def createServerDataBridge(name,macStr,switchID,port,save=True):
		return NetworkInterface.constructor(name,macStr,None,switchID,port,None,False,True,save) 

	@staticmethod
	def updateServerDataBridge(id,name,macStr,switchID,port,save=True):
		return NetworkInterface.objects.get(id=id).update(name,macStr,switchID,port,save) 

	@staticmethod
	def createServerMgmtBridge(name,macStr,save=True):
		return NetworkInterface.constructor(name,macStr,None,None,None,None,True,True,save) 
		 

	'''VM interface factories'''
	@staticmethod
	def createVMDataInterface(name,macObj,save=True):
		return NetworkInterface.constructor(name,None,macObj,None,None,None,False,False,save) 
	@staticmethod
	def createVMMgmtInterface(name,macObj,ip4,save=True):
		return NetworkInterface.constructor(name,None,macObj,None,None,ip4,True,False,save) 
	
