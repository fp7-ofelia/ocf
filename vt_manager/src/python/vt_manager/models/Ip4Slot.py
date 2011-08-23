from django.db import models
from django.contrib import auth
import inspect 
from vt_manager.utils.IP4Utils import IP4Utils
from vt_manager.utils.MutexStore import MutexStore


class Ip4Slot(models.Model):
	
	"""Ip4Slot Class"""

	class Meta:
		"""Meta Class for your model."""
		app_label = 'vt_manager'

	#should be private; Django doesn't like underscores in attribute names 
	ip = models.IPAddressField(verbose_name = "Ip address", editable = True, validators = [IP4Utils.checkValidIp])
	
	isExcluded = models.BooleanField(verbose_name="Is and Excluded Ip",default=0)
	ipRange = models.ForeignKey('Ip4Range', blank = False, null = False, editable = False)
	comment = models.CharField(max_length = 1024, verbose_name="Comment",default="")

	'''Defines soft or hard state of the interface'''	
	doSave = True
	
	##Private methods
	def autoSave(self):
		if self.doSave:
			self.save()
	
	@staticmethod
	def constructor(ipRange,ip,excluded,comment="",save=True):
		self = Ip4Slot()
		try:
			#Check IP
			IP4Utils.checkValidIp(ip)

			self.ip = ip
			self.isExcluded = excluded 
			self.ipRange = ipRange
			self.comment = comment

			self.doSave = save
			if save:
				self.save()
		except Exception as e:
			#self.delete()
			raise e
		return self
	
	def isExcludedIp(self):
		return self.isExcluded

	def getLockIdentifier(self):
		#Uniquely identifies object by a key
		return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)
 
	def getIp(self):
		return self.ip
	def getNetmask(self):
		return self.ipRange.getNetmask()
	def getGatewayIp(self):
		return self.ipRange.getGatewayIp()
	def getDNS1(self):
		return self.ipRange.getDNS1()
	def getDNS2(self):
		return self.ipRange.getDNS2()
	
	def destroy(self):
	
		if self.ipRange != None:
			
			if self.isExcluded:
				self.ipRange.removeExcludedIp(self)	
			else:
				self.ipRange.releaseIp(self)	

		self.delete()	

	'''
	Factories
	'''

	@staticmethod
	def ipFactory(ipRange,ip,save=True):
		return Ip4Slot.constructor(ipRange,ip,False,"",save)

	@staticmethod
	def excludedIpFactory(ipRange,ip,comment,save=True):
		return Ip4Slot.constructor(ipRange,ip,True,comment,save)


#ip = Ip.ipFactory("127.0.0.1")
#excluded = Ip.excludedIpFactory("127.0.0.2")

#print ip.ip	
#print excluded.ip+str(excluded.isExcluded)	
