from datetime import datetime
from django.contrib import auth
from django.db import models
from threading import Lock
#from expedient.common.utils import validators
from vt_manager.models.faults import *
from vt_manager.models.utils.Choices import OSDistClass, OSVersionClass, OSTypeClass
from vt_manager.utils.MutexStore import MutexStore
import re
import inspect

class VirtualMachine(models.Model):
	"""VM data model class"""

	class Meta:
		"""Meta Class for your model."""
		app_label = 'vt_manager'
#		abstract = True

	__childClasses = (
		'XenVM',
	)

	
	''' General parameters '''
	name = models.CharField(max_length = 512, default="", verbose_name = "VM name")
	uuid = models.CharField(max_length = 1024, default="")
	memory = models.IntegerField(blank = True, null=True)
	numberOfCPUs = models.IntegerField(blank = True, null=True)
	discSpaceGB = models.FloatField(blank = True, null=True, editable = False)
	
	''' Properity parameters '''
	projectId = models.CharField(max_length = 1024, default="")
	projectName = models.CharField(max_length = 1024, default="")
	sliceId = models.CharField(max_length = 1024, default="")
	sliceName = models.CharField(max_length = 1024, default="")
	guiUserName = models.CharField(max_length = 1024, default="")
	guiUserUUID = models.CharField(max_length = 1024, default="")
	expedientId = models.IntegerField(blank = True, null=True)

	''' OS parameters '''	
	operatingSystemType = models.CharField(max_length = 512, default="",validators=[OSTypeClass.validateOSType])
	operatingSystemVersion = models.CharField(max_length = 512, default="",validators=[OSVersionClass.validateOSVersion])
	operatingSystemDistribution = models.CharField(max_length = 512, default="",validators=[OSDistClass.validateOSDist])

	''' Networking  '''
	networkInterfaces = models.ManyToManyField('NetworkInterface', blank = True, null = True, editable = False,related_name="vm")
	
	''' Other '''
	callBackURL = models.URLField()
	state = models.CharField(max_length = 24, default="")

	''' Possible states '''
	RUNNING_STATE = 'running'
	CREATED_STATE = 'created (stopped)'
	STOPPED_STATE = 'stopped'
	UNKNOWN_STATE = 'unknown'
	FAILED_STATE = 'failed'
	ONQUEUE_STATE = 'on queue'
	STARTING_STATE = 'starting...'
	STOPPING_STATE = 'stopping...'
	CREATING_STATE = 'creating...'
	DELETING_STATE = 'deleting...'
	REBOOTING_STATE = 'rebooting...'
	
	__possibleStates = (RUNNING_STATE,CREATED_STATE,STOPPED_STATE,UNKNOWN_STATE,FAILED_STATE,ONQUEUE_STATE,STARTING_STATE,STOPPING_STATE,CREATING_STATE,DELETING_STATE,REBOOTING_STATE)

  	''' Mutex over the instance '''
	#Mutex
	mutex = None 

	'''Defines soft or hard state of the VM'''	
	doSave = True

	#Stats of memory cpu and disk
	#TODO: Add here ManyToMany relation to statistics objects



	def autoSave(self):
		if self.doSave:
			self.save()

	def getLockIdentifier(self):
		#Uniquely identifies object by a key
		return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)
 
	##public methods

	def getChildObject(self):
		for childClass in self.__childClasses:
			try:
				return self.__getattribute__(childClass.lower())
			except eval(childClass).DoesNotExist:
				return self

	''' Getters and setters'''
	def setName(self, name):
		def validate_name(value):
			def error():
				raise ValidationError("Invalid input: VM name should not contain blank spaces", code="invalid",)
			cntrlr_name_re = re.compile("^[\S]*$")
			m = cntrlr_name_re.match(value)
			if not m:
				error()
		try:
			validate_name(name)
#                        validators.resourceNameValidator(name)
			self.name = name
			self.autoSave()
		except Exception as e:
			raise e
	def getName(self):
		return self.name

	def setUUID(self, uuid):
		self.uuid = uuid
		self.autoSave()
	def getUUID(self):
		return self.uuid

	def setProjectId(self,projectId):
		if not isinstance(projectId,str):
			projectId = str(projectId)
		self.projectId = projectId
		self.autoSave()
	def getProjectId(self):
		return self.projectId

	def setProjectName(self,projectName):
		if not isinstance(projectName,str):
			projectName = str(projectName)
		self.projectName = projectName
		self.autoSave()
	def getProjectName(self):
		return self.projectName
	
	def setSliceId(self, value):
		self.sliceId = value
		self.autoSave()
	def getSliceId(self):
		return self.sliceId 
	
	def setSliceName(self, value):
		self.sliceName = value
		self.autoSave()
	def getSliceName(self):
		return self.sliceName
	
	def setUIId(self,expedientId):
		if not isinstance(expedientId,int):
			expedientId = int(expedientId)
		self.expedientId = expedientId
		self.autoSave()
	def getUIId(self):
		return self.expedientId
	
	def setState(self,state):
        	if state not in self.__possibleStates:
			raise KeyError, "Unknown state"
		else:
			self.state = state
		self.autoSave()
	def getState(self):
		return self.state
	
	def setMemory(self,memory):
		self.memory = memory
		self.autoSave()
	def getMemory(self):
		return self.memory
	
	def setNumberOfCPUs(self,num):
		#XXX
		self.numberOfCPUs=num
		self.autoSave()
	def getNumberOfCPUs(self):
		return self.numberOfCPUs

	def setDiscSpaceGB(self,num):
		#XXX
		self.discSpaceGB=num
		self.autoSave()
	def getDiscSpaceGB(self):
		return self.discSpaceGB

	def setOSType(self, type):
		OSTypeClass.validateOSType(type)
		self.operatingSystemType = type
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
	
	def setCallBackURL(self, url):
		self.callBackURL = url
		self.autoSave()
	def getCallBackURL(self):
		return self.callBackURL

	def getNetworkInterfaces(self):
		return self.networkInterfaces.all().order_by('-isMgmt','id')

