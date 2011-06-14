from django.db import models
#from django.db.models import SET_NULL
from datetime import datetime
from vt_manager.models.faults import *
#from vt_manager.models.VirtualMachine import VirtualMachine
from vt_manager.models.XenVM import XenVM
import logging

class Action(models.Model):
	"""Class to store actions"""

	class Meta:
		"""Machine exportable class"""
		app_label = 'vt_manager'

	'''
	Action status Types
	'''

	ACTION_STATUS_QUEUED_TYPE  	= "QUEUED"
	ACTION_STATUS_ONGOING_TYPE  = "ONGOING"
	ACTION_STATUS_SUCCESS_TYPE  = "SUCCESS"
	ACTION_STATUS_FAILED_TYPE   = "FAILED"

	__possibleStatus = (ACTION_STATUS_QUEUED_TYPE, ACTION_STATUS_ONGOING_TYPE, ACTION_STATUS_SUCCESS_TYPE, ACTION_STATUS_FAILED_TYPE)	

	'''
	Action type Types
	'''
	ACTION_TYPE_CREATE_TYPE = "create"
	ACTION_TYPE_START_TYPE = "start"
	ACTION_TYPE_DELETE_TYPE = "delete"
	ACTION_TYPE_STOP_TYPE = "hardStop"
	ACTION_TYPE_REBOOT_TYPE = "reboot"

	__possibleTypes = (ACTION_TYPE_CREATE_TYPE, ACTION_TYPE_START_TYPE, ACTION_TYPE_DELETE_TYPE, ACTION_TYPE_STOP_TYPE, ACTION_TYPE_REBOOT_TYPE)
    
	hyperaction = models.CharField(max_length = 16, default="")
	type = models.CharField(max_length = 16, default="")
	uuid = models.CharField(max_length = 512, default="")
	callBackUrl = models.URLField()
	status = models.CharField(max_length = 16, default="")
	description = models.CharField(max_length = 2048, default="", blank =True, null =True)
	vmUUID = models.CharField(max_length = 512, default="", blank =  True, null = True)

	def checkActionIsPresentAndUnique(self):
		if Action.objects.filter (uuid = self.uuid).count() != 0:
			logging.error("Action with the same uuid already exists")
			raise Exception("Action with the same uuid already exists")
	
	def getAndCheckActionByUUID(self, uuid):
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

	def setVMuuid(self, vmUUID):
		self.vmUUID = vmUUID 
		self.save()

	def getVMuuid(self):
		return self.vmUUID
