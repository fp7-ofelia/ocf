from django.db import models
from django.contrib import auth
from threading import Lock
import inspect 
from vt_manager.models.VTServer import VTServer
from vt_manager.models.VirtualMachine import VirtualMachine
from vt_manager.models.XenVM import XenVM
from vt_manager.utils.MutexStore import MutexStore
from vt_manager.models.utils.Choices import VirtTechClass

def validateAgentURLwrapper():
	VTServer.validateAgentURL()

class XenServer(VTServer):
	"""Virtualization Server class"""

	class Meta:
		"""Meta Class for your model."""
		app_label = 'vt_manager'

	''' VMs array '''
	vms = models.ManyToManyField(XenVM, blank = True, null = False, editable = False, related_name = "Server")
	
	#Stats of memory cpu and disk
	#TODO: Add here ManyToMany relation to statistics objects


	##Private methods
	def __tupleContainsKey(tu,key):
		for val in tu:
			if val[0] == key:
				return True
		return False

	def __addInterface(self,interface):
		
		if not isinstance(interface,NetworkInterface):
			raise Exception("Cannot add an interface if is not a NetworkInterface object instance")	
		
	'''Constructor'''
	@staticmethod
	def constructor(name,osType,osDistribution,osVersion,nCPUs,CPUfreq,memory,size,agentUrl,agentPassword,save=True):
		self = XenServer()
		return self.updateServer(name,osType,osDistribution,osVersion,nCPUs,CPUfreq,memory,size,agentUrl,agentPassword,save=True)

	'''Updater'''
	def updateServer(self,name,osType,osDistribution,osVersion,nCPUs,CPUfreq,memory,size,agentUrl,agentPassword,save=True):
		try:
			self.setName(name)
			self.setVirtTech(VirtTechClass.VIRT_TECH_TYPE_XEN)
			self.setOSType(osType)
			self.setOSDistribution(osDistribution)
			self.setOSVersion(osVersion)
			self.setNumberOfCPUs(nCPUs)
			self.setCPUFrequency(CPUfreq)
			self.setMemory(memory)
			self.setDiscSpaceGB(size)
			self.setAgentURL(agentUrl)
			self.setAgentPassword(agentPassword)
			self.doSave = save
			if save:
				self.save()
			return self
		except Exception as e:
			print e
			self.destroy()
			raise e

	'''Destructor'''
	def destroy(self):	
		with MutexStore.getObjectLock(self.getLockIdentifier()):
			#destroy interfaces
			for inter in self.networkInterfaces.all():
				inter.destroy()
			self.delete()
	
	''' Public interface methods '''

	def getVMs(self,**kwargs):
		return self.vms.filter(**kwargs)
	def getVM(self,**kwargs):
		return self.vms.get(kwargs)
	
	def createVM(self,name,uuid,projectId,projectName,sliceId,sliceName,osType,osVersion,osDist,memory,discSpaceGB,numberOfCPUs,callBackUrl,hdSetupType,hdOriginPath,virtSetupType,save=True):
		with MutexStore.getObjectLock(self.getLockIdentifier()):
			
			if XenVM.objects.filter(uuid=uuid).count() > 0:
				raise Exception("Cannot create a Virtual Machine with the same UUID as an existing one")

			#Allocate interfaces for the VM
			interfaces = self.createEnslavedVMInterfaces()
			
			#Call factory
			vm = XenVM.create(name,uuid,projectId,projectName,sliceId,sliceName,osType,osVersion,osDist,memory,discSpaceGB,numberOfCPUs,callBackUrl,interfaces,hdSetupType,hdOriginPath,virtSetupType,save)
			self.vms.add(vm)	
			self.autoSave()
			return vm

	def deleteVM(self,vm):
		with MutexStore.getObjectLock(self.getLockIdentifier()):	
			if vm not in self.vms.all():
				raise Exception("Cannot delete a VM from pool if it is not already in") 
			self.vms.remove(vm)
			vm.destroy()	
			self.autoSave()

