from django.db import models
from django.contrib import auth
from datetime import datetime
from vt_manager.models.faults import *
import re
import inspect 
from vt_manager.models.VirtualMachine import VirtualMachine
from vt_manager.utils.MutexStore import MutexStore


''' Choices  and constants '''
#HD setup type
HD_SETUP_TYPE_FILE_IMAGE = "file-image"
HD_SETUP_TYPE_LV = "logical-volume-image"
HD_SETUP_TYPE_CHOICES = (
       	(HD_SETUP_TYPE_FILE_IMAGE, 'File image'),
       	(HD_SETUP_TYPE_LV, 'Logical Volume Image'),
)

#Virtualization type
VIRTUALIZATION_SETUP_TYPE_PARAVIRTUALIZATION= "paravirtualization"
VIRTUALIZATION_SETUP_TYPE_HAV = "hardware-assisted-virtualization"
VIRTUALIZATION_SETUP_TYPE = (
       	(VIRTUALIZATION_SETUP_TYPE_PARAVIRTUALIZATION, 'Paravirtualization'),
       	(VIRTUALIZATION_SETUP_TYPE_HAV, 'Hardware-assisted virtualization'),
)


IMAGE_CONFIGURATORS = {
			'default/default.tar.gz':'',
			'irati/irati.img':'IratiDebianVMConfigurator',
			'spirent/spirentSTCVM.img':'SpirentCentOSVMConfigurator',
                        'debian7/debian7.img': 'DebianWheezyVMConfigurator',
			}
	

'''
Ugly wrappers due to Django limitation on the validators
'''
def validateHdSetupWrapper(param):
	return XenVM.validateHdSetupType(param)
def validateVirtualizationSetupType(param):
	return XenVM.validateHdSetupType(param)


	
class XenVM(VirtualMachine):

	class Meta:
		"""Meta Class for your model."""
		app_label = 'vt_manager'

	"""XEN VM data model class"""
	#server = models.OneToOneField('XenServer', blank = False, null = False, editable = False, verbose_name = "XEN server")

	hdSetupType = models.CharField(max_length = 1024, default="",validators=[validateHdSetupWrapper])
	hdOriginPath = models.CharField(max_length = 1024, default="")
	virtualizationSetupType = models.CharField(max_length = 1024, default="",validators=[validateVirtualizationSetupType])


	@staticmethod	
	def constructor(name,uuid,projectId,projectName,sliceId,sliceName,osType,osVersion,osDist,memory,discSpaceGB,numberOfCPUs,callBackUrl,interfaces,hdSetupType,hdOriginPath,virtSetupType,save=True):
		self =  XenVM()
		try:
			#Set common fields
			self.setName(name)
			self.setUUID(uuid)
			self.setProjectId(projectId)
			self.setProjectName(projectName)
			self.setSliceId(sliceId)
			self.setSliceName(sliceName)
			self.setOSType(osType)
			self.setOSVersion(osVersion)
			self.setOSDistribution(osDist)
			self.setMemory(memory)
			self.setDiscSpaceGB(discSpaceGB)
			self.setNumberOfCPUs(numberOfCPUs)
			self.setCallBackURL(callBackUrl)
			self.setState(self.UNKNOWN_STATE)
			for interface in interfaces:
				self.networkInterfaces.add(interface)
			#self.server = server
	
			#Xen parameters
			self.hdSetupType =hdSetupType
			self.hdOriginPath = hdOriginPath
			self.virtualizationSetupType = virtSetupType
	
			self.doSave = save
			if save:	
				self.save()
		except Exception as e:
			#self.delete()
			print e
			raise e

		return self	
	
	'''Destructor'''
	def destroy(self):	
		with MutexStore.getObjectLock(self.getLockIdentifier()):
			#destroy interfaces
			for inter in self.networkInterfaces.all():
				inter.destroy()
			self.delete()
	
	''' Getters and setters '''
	def getHdSetupType(self):
		return 	self.hdSetupType
	@staticmethod
	def validateHdSetupType(hdType):
		if value not in HD_SETUP_TYPE_CHOICES:
			raise Exception("Invalid HD Setup type")	
	def setHdSetupType(self,hdType):
		validateHdSetupType(hdType)
		self.hdSetupType
		self.autoSave()

	def getHdOriginPath(self):
		return 	self.hdSetupType
	def setHdOriginPath(self,path):
		self.hdOriginPath = path
		self.autoSave()
	def getVirtualizationSetupType(self):
		return 	self.virtualizationSetupType
	@staticmethod
	def validateVirtualizationSetupType(self,vType):
		if value not in VIRTUALIZATION_SETUP_TYPE_CHOICES:
			raise Exception("Invalid Virtualization Setup type")	
	def setVirtualizationSetupType(self,vType):
		self.validateVirtualizationSetupType(vType)
		self.virtualizationSetupType = vType
		self.autoSave()



	''' Factories '''
	@staticmethod
	def create(name,uuid,projectId,projectName,sliceId,sliceName,osType,osVersion,osDist,memory,discSpaceGB,numberOfCPUs,callBackUrl,interfaces,hdSetupType,hdOriginPath,virtSetupType,save=True):
		return XenVM.constructor(name,uuid,projectId,projectName,sliceId,sliceName,osType,osVersion,osDist,memory,discSpaceGB,numberOfCPUs,callBackUrl,interfaces,hdSetupType,hdOriginPath,virtSetupType,save)
