from django.db import models
from django.contrib import auth
from threading import Lock 
import re
import uuid
import inspect 
from django.core.exceptions import ValidationError
from vt_manager.models.NetworkInterface import NetworkInterface
from vt_manager.communication.XmlRpcClient import XmlRpcClient
from vt_manager.models.utils.Choices import VirtTechClass, OSDistClass, OSVersionClass, OSTypeClass
from vt_manager.utils.MutexStore import MutexStore
from vt_manager.models.MacRange import MacRange
from vt_manager.models.Ip4Range import Ip4Range
from vt_manager.common.utils import validators

def validateAgentURLwrapper(url):
	VTServer.validateAgentURL(url)

class VTServer(models.Model):
	"""Virtualization Server class"""

	class Meta:
		"""Meta Class for your model."""
		app_label = 'vt_manager'
#		abstract = True


	__childClasses = (
		'XenServer',
	  )


	''' General attributes '''
	available = models.BooleanField(default=1, verbose_name = "Available", editable = False)
	enabled = models.BooleanField(default=1, verbose_name = "Enabled", editable = True)
	name = models.CharField(max_length = 511, default="", verbose_name = "Name", validators=[validators.resourceNameValidator])
	uuid = models.CharField(max_length = 1024, default = uuid.uuid4(), editable = False)

	''' OS '''
	operatingSystemType = models.CharField(choices = OSTypeClass.OS_TYPE_CHOICES,max_length = 512, verbose_name = "OS Type",validators=[OSTypeClass.validateOSType])
	operatingSystemDistribution = models.CharField(choices = OSDistClass.OS_DIST_CHOICES,max_length = 512, verbose_name = "OS Distribution",validators=[OSDistClass.validateOSDist])
	operatingSystemVersion = models.CharField(choices = OSVersionClass.OS_VERSION_CHOICES,max_length = 512, verbose_name = "OS Version",validators=[OSVersionClass.validateOSVersion])
	
	''' Virtualization technology '''
	virtTech = models.CharField(choices = VirtTechClass.VIRT_TECH_CHOICES, max_length = 512, verbose_name = "Virtualization Technology",validators=[VirtTechClass.validateVirtTech])
	
	''' Hardware '''
	numberOfCPUs = models.IntegerField(blank = True, null=True, verbose_name = "Number of CPUs")
	CPUFrequency = models.IntegerField(blank = True, null=True, verbose_name = "CPU frequency (GB)")
	memory = models.IntegerField(blank = True, null=True, verbose_name = "Memory (GB)")
	discSpaceGB = models.FloatField(blank = True, null=True, verbose_name = "Size (GB)")

	''' Agent fields'''
	agentURL = models.URLField(verify_exists = False, verbose_name = "URL of the Server Agent", validators=[validateAgentURLwrapper], help_text="URL of the agent daemon running in the server. It should be https://DOMAIN_OR_IP:9229")
	agentPassword = models.CharField(blank=True,null=True,max_length=128, verbose_name="Agent password", validators=[validators.resourceNameValidator])

	url = models.URLField(verify_exists = False, verbose_name = "URL of the Server", editable = False, blank = True)
	
	''' Network interfaces'''
	networkInterfaces = models.ManyToManyField('NetworkInterface', blank = True, null = False, editable = False)
	
	''' Other networking parameters '''
	subscribedMacRanges = models.ManyToManyField('MacRange', blank = True, null = True, editable = False)
	subscribedIp4Ranges = models.ManyToManyField('Ip4Range', blank = True, null = True, editable = False)
	
	''' Mutex over the instance '''
	#Mutex
	mutex = None 

	'''Defines soft or hard state of the Server'''	
	doSave = True


	#Stats of memory cpu and disk
	#TODO: Add here ManyToMany relation to statistics objects


	##Private methods

	def getChildObject(self):
		for childClass in self.__childClasses:
	  		try:
				return self.__getattribute__(childClass.lower())
	  		except Exception:
	  		#except eval(childClass).DoesNotExist:
				pass
				#return self
	
	def __tupleContainsKey(tu,key):
		for val in tu:
			if val[0] == key:
				return True
		return False
	
	def autoSave(self):
		if self.doSave:
			self.save()
	
	def getLockIdentifier(self):
		#Uniquely identifies object by a key
		return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)
 
	##Public methods

	''' Getters and setters '''
	def setName(self, name):
		self.name = name
		self.autoSave()
	def getName(self):
		return self.name
	def setUUID(self, uuid):
		#XXX	
		self.uuid = uuid
		self.autoSave()
	def getUUID(self):
		return self.uuid
	def setNumberOfCPUs(self, cpus):
		self.numberOfCPUs = cpus
		self.autoSave()
	def getNumberOfCPUs(self):
		return self.numberOfCPUs
	def setMemory(self, memory):
		self.memory = memory
		self.autoSave()
	def getCPUFrequency(self):
		return self.CPUFrequency
	def setCPUFrequency(self, frequency):
		self.CPUFrequency = frequency
		self.autoSave()
	def getMemory(self):
		return self.memory
	def setDiscSpaceGB(self, space):
		self.discSpaceGB = space
		self.autoSave()
	def getDiscSpaceGB(self):
		return self.discSpaceGB

	@staticmethod
	def validateAgentURL(url):
			#Hard lookup; make sure that Agent is running and at the same time URL is correct:
			if url == "":
				return
			try:
				XmlRpcClient.callRPCMethod(url,"ping","testing")
			except Exception as e:
				raise ValidationError("Cannot communicate with Agent. Nested exception is: " + str(e))
		
	def setAgentURL(self, url):
		with MutexStore.getObjectLock(self.getLockIdentifier()):
			VTServer.validateAgentURL(url)
			self.agentURL = url
			self.autoSave()
	def getAgentURL(self):
		return self.agentURL
	def setURL(self, url):
		self.url = url
		self.autoSave()
	def getURL(self):
		return self.url
	def setVirtTech(self, virtTech):
		VirtTechClass.validateVirtTech(virtTech)
		self.virtTech = virtTech
		self.autoSave()
	def getVirtTech(self):
		return self.virtTech
	def setOSType(self, osType):
		OSTypeClass.validateOSType(osType)	
		self.operatingSystemType = osType
		self.autoSave()
	def getOSType(self):
		return self.operatingSystemType
	def setOSVersion(self, version):
		OSVersionClass.validateOSVersion(version)
		self.operatingSystemVersion = version
		self.autoSave()
	def getOSVersion(self):
		return self.operatingSystemVersion
	def setOSDistribution(self, dist):
		OSDistClass.validateOSDist(dist)
		self.operatingSystemDistribution = dist
		self.autoSave()
	def getOSDistribution(self):
		return self.operatingSystemDistribution
	def setAvailable(self,av):
		self.available = av
		self.autoSave()
	def getAvailable(self):
		return self.available
   	def setEnabled(self,en):
		self.enabled = en
		self.autoSave()
	def getEnabled(self):
		return self.enabled
	def getAgentPassword(self):
		return self.agentPassword
	def setAgentPassword(self, password):
		self.agentPassword = password
		self.autoSave()

	#Destroy
	def destroy(self):
		with MutexStore.getObjectLock(self.getLockIdentifier()):

			if self.vms.all().count()>0:
				raise Exception("Cannot destroy a server which hosts VMs. Delete VMs first")
			
			#Delete associated interfaces
			for interface in self.networkInterfaces.all():
				interface.destroy()

			#Delete instance
			self.delete()
	''' Ranges '''
	def subscribeToMacRange(self,newRange):
		if not isinstance(newRange,MacRange):
			raise Exception("Invalid instance type on subscribeToMacRange; must be MacRange")
		if newRange in self.subscribedMacRanges.all():
			raise Exception("Server is already subscribed to this range")
			
		self.subscribedMacRanges.add(newRange)
		self.autoSave()

	def unsubscribeToMacRange(self,oRange):
		if not isinstance(oRange,MacRange):
			raise Exception("Invalid instance type on unsubscribeToMacRange; must be MacRange")
	
		self.subscribedMacRanges.remove(oRange)
		self.autoSave()
		
	def getSubscribedMacRangesNoGlobal(self):
		return self.subscribedMacRanges.all()

	def getSubscribedMacRanges(self):
		if self.subscribedMacRanges.all().count() > 0:
			return self.subscribedMacRanges.all()
		else:
			#Return global (all) ranges
			return MacRange.objects.filter(isGlobal=True)

	def subscribeToIp4Range(self,newRange):
		if not isinstance(newRange,Ip4Range):
			raise Exception("Invalid instance type on subscribeToIpRange; must be Ip4Range")
		if newRange in self.subscribedIp4Ranges.all():
			raise Exception("Server is already subscribed to this range")
			
		self.subscribedIp4Ranges.add(newRange)
		self.autoSave()

	def unsubscribeToIp4Range(self,oRange):
		if not isinstance(oRange,Ip4Range):
			raise Exception("Invalid instance type on unsubscribeToIpRange; must be Ip4Range")
	
		self.subscribedIp4Ranges.remove(oRange)
		self.autoSave()
	
	def getSubscribedIp4RangesNoGlobal(self):
		return self.subscribedIp4Ranges.all()
	
	def getSubscribedIp4Ranges(self):
		if self.subscribedIp4Ranges.all().count() > 0:
			return self.subscribedIp4Ranges.all()
		else:
			#Return global (all) ranges
			return Ip4Range.objects.filter(isGlobal=True)
	
	def __allocateMacFromSubscribedRanges(self):
		macObj = None
		#Allocate Mac
		for macRange in self.getSubscribedMacRanges():
			try:
				macObj = macRange.allocateMac() 
			except Exception as e:
				continue
			break

		if macObj == None:
			raise Exception("Could not allocate Mac address for the VM over subscribed ranges")
	
		return macObj

	def __allocateIpFromSubscribedRanges(self):
		ipObj = None 
		
		#Allocate Ip
		for ipRange in self.getSubscribedIp4Ranges():
			try:
				ipObj = ipRange.allocateIp() 
			except Exception as e:
				continue
			break
		if ipObj == None:
			raise Exception("Could not allocate Ip4 address for the VM over subscribed ranges")
	
		return ipObj
	
	''' VM interfaces and VM creation methods '''
	def __createEnslavedDataVMNetworkInterface(self,serverInterface):
		#Obtain 
		macObj = self.__allocateMacFromSubscribedRanges() 
		
		interface = NetworkInterface.createVMDataInterface(serverInterface.getName()+"-slave",macObj) 
		
		#Enslave it	
		serverInterface.attachInterfaceToBridge(interface)	
		return interface
	
	def __createEnslavedMgmtVMNetworkInterface(self,serverInterface):
		#Obtain 
		macObj = self.__allocateMacFromSubscribedRanges() 
		ipObj = self.__allocateIpFromSubscribedRanges()
		
		interface = NetworkInterface.createVMMgmtInterface(serverInterface.getName()+"-slave",macObj,ipObj) 
		
		#Enslave it	
		serverInterface.attachInterfaceToBridge(interface)	
		return interface

	def createEnslavedVMInterfaces(self):
		vmInterfaces = set()	
		try:
			#Allocate one interface for each Server's interface 
			for serverInterface in self.networkInterfaces.all():
				if serverInterface.isMgmt:
					vmInterfaces.add(self.__createEnslavedMgmtVMNetworkInterface(serverInterface))
				else: 		
					vmInterfaces.add(self.__createEnslavedDataVMNetworkInterface(serverInterface))
		except Exception as e:
			for interface in vmInterfaces:
				interface.destroy()
			raise e
		return vmInterfaces 
			
	''' Server interfaces '''
	#Network mgmt bridges
	def setMgmtBridge(self,name,macStr):
		with MutexStore.getObjectLock(self.getLockIdentifier()):
			nInter = self.networkInterfaces.filter(isMgmt=True,isBridge=True)
			if nInter.count() == 1:
				mgmt = nInter.get()
				mgmt.setName(name)
				mgmt.setMacStr(macStr)

			elif nInter.count() == 0:
				mgmt = NetworkInterface.createServerMgmtBridge(name,macStr)
				self.networkInterfaces.add(mgmt)
			else:
				raise Exception("Unexpected length of managment NetworkInterface query")
			self.autoSave()
	
	#Network data bridges
	def addDataBridge(self,name,macStr,switchId,port):
		with MutexStore.getObjectLock(self.getLockIdentifier()):	
			if self.networkInterfaces.filter(name=name, isBridge=True).count()> 0:
				raise Exception("Another data bridge with the same name already exists in this Server") 
				
			netInt = NetworkInterface.createServerDataBridge(name,macStr,switchId,port)
			self.networkInterfaces.add(netInt)
			self.autoSave()

	def updateDataBridge(self,interface):
		with MutexStore.getObjectLock(self.getLockIdentifier()):
			if self.networkInterfaces.filter(id = interface.id).count()!= 1:
				raise Exception("Can not update bridge interface because it does not exist or id is duplicated") 
				
			NetworkInterface.updateServerDataBridge(interface.id,interface.getName(),interface.getMacStr(),interface.getSwitchID(),interface.getPort())

	def deleteDataBridge(self,netInt):
		with MutexStore.getObjectLock(self.getLockIdentifier()):
			if not isinstance(netInt,NetworkInterface):
				raise Exception("Can only delete Data Bridge that are instances of NetworkInterace")
			
			#TODO: delete interfaces from VMs, for the moment forbid
			if netInt.getNumberOfConnections() > 0:
				raise Exception("Cannot delete a Data bridge from a server if this bridge has VM's interfaces ensalved.")	

			self.networkInterfaces.remove(netInt)
			netInt.destroy()
			self.autoSave()


	def getNetworkInterfaces(self):
		return self.networkInterfaces.all().order_by('-isMgmt','id')

