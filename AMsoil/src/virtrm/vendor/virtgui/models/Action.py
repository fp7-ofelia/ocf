from django.db import models
from datetime import datetime
from vt_manager.models.faults import *
import logging
import uuid

class Action(models.Model):
	"""Class to store actions"""

	class Meta:
		"""Machine exportable class"""
		app_label = 'vt_manager'

	'''
	Action status Types
	'''

	QUEUED_STATUS = "QUEUED"
	ONGOING_STATUS= "ONGOING"
	SUCCESS_STATUS  = "SUCCESS"
	FAILED_STATUS   = "FAILED"

	__possibleStatus = (QUEUED_STATUS,ONGOING_STATUS,SUCCESS_STATUS,FAILED_STATUS)

	'''
	Action type Types
	'''
	##Monitoring
	#Servers
	MONITORING_SERVER_VMS_TYPE="listActiveVMs"
	
	__monitoringTypes = (
		#Server
		MONITORING_SERVER_VMS_TYPE,	
	)
	
	#VMs
	##Provisioning 
	#VM provisioning actions	
	PROVISIONING_VM_CREATE_TYPE = "create"
	PROVISIONING_VM_START_TYPE = "start"
	PROVISIONING_VM_DELETE_TYPE = "delete"
	PROVISIONING_VM_STOP_TYPE = "hardStop"
	PROVISIONING_VM_REBOOT_TYPE = "reboot"

	__provisioningTypes = (
		#VM
		PROVISIONING_VM_CREATE_TYPE,
		PROVISIONING_VM_START_TYPE,
		PROVISIONING_VM_DELETE_TYPE, 
		PROVISIONING_VM_STOP_TYPE, 
		PROVISIONING_VM_REBOOT_TYPE,
	)

	'''All possible types '''
	__possibleTypes = (
		#Monitoring
		#Server
		MONITORING_SERVER_VMS_TYPE,	
		
		##Provisioning
		#VM
		PROVISIONING_VM_CREATE_TYPE,
		PROVISIONING_VM_START_TYPE,
		PROVISIONING_VM_DELETE_TYPE, 
		PROVISIONING_VM_STOP_TYPE, 
		PROVISIONING_VM_REBOOT_TYPE,
	)
    
	type = models.CharField(max_length = 16, default="")
	uuid = models.CharField(max_length = 512, default="")
	callBackUrl = models.URLField()
	status = models.CharField(max_length = 16, default="")
	description = models.CharField(max_length = 2048, default="", blank =True, null =True)
	objectUUID = models.CharField(max_length = 512, default="", blank =  True, null = True)


	def checkActionIsPresentAndUnique(self):
		if Action.objects.filter (uuid = self.uuid).count() != 0:
			logging.error("Action with the same uuid already exists")
			raise Exception("Action with the same uuid already exists")
	
	@staticmethod	
	def getAndCheckActionByUUID(uuid):
		actions = Action.objects.filter (uuid = uuid)
		if actions.count() ==  1:
			return actions[0]
		elif actions.count() == 0:
			logging.error("Action with uuid %s does not exist" % uuid)
			raise Exception("Action with uuid %s does not exist" % uuid)
		elif actions.count() > 1:
			logging.error("Action with uuid %s does not exist" % uuid)
			raise Exception("More than one Action with uuid %s" % uuid)

	def setStatus(self, status):
		if status not in self.__possibleStatus:
			raise Exception("Status not valid")
		self.status = status
		self.save()

	def getStatus(self):
		return self.status

	def setType(self, type):
		if type not in self.__possibleTypes:
			raise Exception("Action type not valid")
		self.type = type
		self.save()

	def getType(self):
		return self.type

	def isProvisioningType(self):
		return self.type in self.__provisioningTypes
	def isMonitoringType(self):
		return self.type in self.__monitoringTypes

	def setDescription(self, description):
		self.description = description 
		self.save()

	def getDescription(self):
		return self.descripion

	def setUUID(self, uuid):
		self.uuid = uuid 
		self.save()

	def getUUID(self):
		return self.uuid

	def setCallBackUrl(self, url):
		self.uuid = url 
		self.save()

	def getCallBackUrl(self):
		return self.url

	def setObjectUUID(self, objUUID):
		self.objectUUID = objUUID 
		self.save()

	def getObjectUUID(self):
		return self.objectUUID
	
	@staticmethod
	def constructor(aType,status,objectUUID=None,description=""):
		action = Action()
		action.setType(aType)
		action.setStatus(status)
		action.setUUID(uuid.uuid4())
		if not objectUUID == None:
			action.setObjectUUID(objectUUID)
		if not description == "":
			action.setDescription(description)	
		return action
	
	def destroy(self):
		self.delete()
