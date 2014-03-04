from django.db import models
from django.contrib import auth
import inspect 
from vt_manager.utils.EthernetUtils import EthernetUtils
from vt_manager.utils.MutexStore import MutexStore


class MacSlot(models.Model):

	##from vt_manager.models.MacRange import MacRange

	"""MacSlot Class"""

	class Meta:
		"""Meta Class for your model."""
		app_label = 'vt_manager'

	#should be private; Django doesn't like underscores in attribute names 
    	mac = models.CharField(verbose_name="Mac Address",max_length = 17, default="",validators=[EthernetUtils.checkValidMac])
	macRange = models.ForeignKey('MacRange', blank = True, null = True, editable = False)
	isExcluded = models.BooleanField(verbose_name="Is and Excluded MAC",default=0)
	comment = models.CharField(max_length = 1024, verbose_name="Comment",default="")

	'''Defines soft or hard state of the interface'''	
	doSave = True

	##Private methods
	def autoSave(self):
		if self.doSave:
			self.save()

	def getLockIdentifier(self):
		#Uniquely identifies object by a key
		return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)
 
	@staticmethod
	def constructor(macRange,mac,excluded,comment="",save=True):
		self = MacSlot()

		#Check MAC
		if not mac == "":
			EthernetUtils.checkValidMac(mac)

		self.mac = mac
		self.isExcluded = excluded 
		self.macRange = macRange
		self.comment = comment
		self.doSave = save

		if save:
			self.save()
		
		return self
	
	def destroy(self):
			
		if self.macRange != None:
			
			if self.isExcluded:
				self.macRange.removeExcludedMac(self)	
			else:
				self.macRange.releaseMac(self)	

		self.delete()	

	def getMac(self):
		return self.mac

	def isExcludedMac(self):
		return self.isExcluded

	def getAssociatedVM(self):
		return self.interface.vm.name

	def setMac(self, mac):
		self.mac = mac
		self.autoSave()	
	'''
	Factories
	'''

	@staticmethod
	def macFactory(macRange,mac,save=True):
		return MacSlot.constructor(macRange,mac,False,"",save)

	@staticmethod
	def excludedMacFactory(macRange,mac,comment,save=True):
		return MacSlot.constructor(macRange,mac,True,comment,save)



#ip = Ip.ipFactory("127.0.0.1")
#excluded = Ip.excludedIpFactory("127.0.0.2")

#print ip.ip	
#print excluded.ip+str(excluded.isExcluded)	
