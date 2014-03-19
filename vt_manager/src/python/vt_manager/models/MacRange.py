from django.db import models
from django.contrib import auth
from threading import Lock 
import inspect 
from vt_manager.utils.EthernetUtils import EthernetUtils
from vt_manager.utils.MutexStore import MutexStore
from vt_manager.models.MacSlot import MacSlot
'''
	
	@author: msune
'''

class MacRange(models.Model):
	
	from vt_manager.models.MacSlot import MacSlot
	"""MacRange"""
	
	class Meta:
		"""Meta Class for your model."""
		app_label = 'vt_manager'

	'''
	Private attributes 
	'''
	#Range name
	name = models.CharField(max_length = 255, default="", verbose_name = "Range name",unique=True)
	isGlobal = models.BooleanField(verbose_name="Global range",default=1,help_text="Globa ranges will be used by servers which are not subscribed to any specific range")


	#Range parameters
    	startMac = models.CharField(verbose_name="Start Mac Address", max_length = 17, default="", validators=[EthernetUtils.checkValidMac])
    	endMac = models.CharField(verbose_name="End Mac Address", max_length = 17, default="", validators=[EthernetUtils.checkValidMac])
	
	#Pool of macs both assigned and excluded (particular case of assignment)
	macs = models.ManyToManyField('MacSlot', blank = True, null = True, editable = False)
    	nextAvailableMac = models.CharField(verbose_name="Next Available Mac Address",max_length = 17, default="",editable=False)

	#Statistics
	numberOfSlots = models.BigIntegerField(blank = True, null=True, editable = False)

	#Defines soft or hard state of the range 
	doSave = True


	'''
	Private methods	
	'''
	
	@staticmethod
	def constructor(name,startMac,endMac,isGlobal=True,save=True):
		self = MacRange()
		try:
			#Default constructor
			EthernetUtils.checkValidMac(startMac)
			EthernetUtils.checkValidMac(endMac)
			
			self.startMac = startMac.upper()
			self.endMac = endMac.upper()
			
			self.name = name
			self.isGlobal= isGlobal
			
			#Create an iterator
			it= EthernetUtils.getMacIterator(self.startMac,self.endMac)
			self.nextAvailableMac = it.getNextMac()
			
			#Number of Slots
			try:
				self.numberOfSlots = EthernetUtils.getNumberOfSlotsInRange(startMac,endMac)		
			except Exception as e:	
				print "Exception doing slot calculation"+str(e)	
				self.numberOfSlots = -1		
		
			self.doSave = save
			if save:
				self.save()
		except Exception as e:
			print e
			raise e
		return self
	
	def autoSave(self):
		if self.doSave:
			self.save()
	
        def __setStartMac(self, value):
		EthernetUtils.checkValidMac(value)
		MAC4Utils.checkValidMac(value) 
                self.startMac = value.upper()
		self.autoSave()


        def __setEndMac(self, value):
		EthernetUtils.checkValidMac(value)
                self.endMac = value.upper()
		self.autoSave()

	def __isMacAvailable(self,mac):
		return	self.macs.filter(mac=mac).count() == 0

	'''
	Public methods	
	'''
	def getLockIdentifier(self):
		#Uniquely identifies object by a key
		return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)
        
	def getName(self):
		return self.name 
        def getStartMac(self):
                return self.startMac
        def getEndMac(self):
                return self.endMac
	def getIsGlobal(self):
		return self.isGlobal 
 
	def getExcludedMacs(self):
		return self.macs.filter(isExcluded=True).order_by('mac')

 	def getAllocatedMacs(self):
		return self.macs.filter(isExcluded=False).order_by('mac')

	def getNumberOfSlots(self):
		return int(self.numberOfSlots)
	
	def getPercentageRangeUsage(self):
		if not self.numberOfSlots == -1:
			return round((float(self.macs.all().count())/float(self.numberOfSlots))*100,2)
		return -1
 
	def destroy(self):
		with MutexStore.getObjectLock(self.getLockIdentifier()):
			if self.macs.filter(isExcluded=False).count() > 0:
				raise Exception("Cannot delete MacRange. Range still contains allocated Macs")
		
			for mac in self.macs.all():
				#Delete excluded macs
				mac.delete()
			self.delete()
			

		
	def allocateMac(self):
		'''
		Allocates an MAC address of the range	
		'''
		with MutexStore.getObjectLock(self.getLockIdentifier()):
			#Implements first fit algorithm
				
			if self.nextAvailableMac == None:
				raise Exception("Could not allocate any Mac")
		
			newMac = MacSlot.macFactory(self,self.nextAvailableMac)
			self.macs.add(newMac)
			
			#Try to find new slot
			try:
                        	it= EthernetUtils.getMacIterator(self.nextAvailableMac,self.endMac)
				while True:
					mac = it.getNextMac()
					if self.__isMacAvailable(mac):
						break
				self.nextAvailableMac = mac
			except Exception as e:
				self.nextAvailableMac = None
	
			self.autoSave()

			return newMac
		

	def releaseMac(self,macObj):
		'''
		Releases an MAC address of the range (but it does not destroy the object!!)	
		'''
		with MutexStore.getObjectLock(self.getLockIdentifier()):
			macStr = macObj.getMac()
			if not self.macs.filter(mac=macStr).count() > 0:
				raise Exception("Cannot release Mac %s. Reason may be is unallocated or is an excluded Mac",macStr)
					
			self.macs.remove(macObj)
				
			#Determine new available Mac
			if not self.nextAvailableMac == None:
				if EthernetUtils.compareMacs(macStr,self.nextAvailableMac) > 0:
					#Do nothing
					pass
				else:	
					self.nextAvailableMac = macStr
			else:
				#No more gaps
				self.nextAvailableMac = macStr

			self.autoSave()

	def addExcludedMac(self,macStr,comment=""):
		'''
		Add an MAC to the exclusion list	
		'''
		with MutexStore.getObjectLock(self.getLockIdentifier()):
			#Check is not already allocated
			if not  self.__isMacAvailable(macStr):
				raise Exception("Mac already allocated or marked as excluded")

			#then forbidd
			if not EthernetUtils.isMacInRange(macStr,self.startMac,self.endMac):
				raise Exception("Mac is not in range")

			newMac = MacSlot.excludedMacFactory(self,macStr,comment)
			self.macs.add(newMac)

			#if was nextSlot shift
			if self.nextAvailableMac == macStr:
				try:
                        		it= EthernetUtils.getMacIterator(self.nextAvailableMac,self.endMac)
					while True:
						mac = it.getNextMac()
						if self.__isMacAvailable(mac):
							break
					self.nextAvailableMac= mac
				except Exception as e:
					self.nextAvailableMac = None
			
			self.autoSave()
	
	def removeExcludedMac(self,macObj):
		'''
		Deletes an Mac from the exclusion list	(but it does not destroy the object!!)
		'''	
		with MutexStore.getObjectLock(self.getLockIdentifier()):

			macStr = macObj.getMac()

			if (not self.macs.get(mac=macStr).isExcludedMac()):
				raise Exception("Cannot release Mac. Reason may be is unallocated or is not excluded Mac")
	
			self.macs.remove(macObj)

			#Determine new available Mac
			if not self.nextAvailableMac == None:
				if EthernetUtils.compareMacs(macStr,self.nextAvailableMac) > 0:
					#Do nothing
					pass
				else:	
					self.nextAvailableMac = macStr
			else:
				#No more gaps
				self.nextAvailableMac = macStr

	
			self.autoSave()
	
	
	'''
	Static methods
	'''
	@staticmethod
	def getAllocatedGlobalNumberOfSlots():
		allocated = 0
		for range in MacRange.objects.filter(isGlobal=True):
			allocated += range.macs.all().count()
		return allocated
			
	@staticmethod
	def getGlobalNumberOfSlots():
		slots = 0
		for range in MacRange.objects.filter(isGlobal=True):
			slots += range.numberOfSlots
		return int(slots)
		

	def rebasePointer(self):
		'''Used when pointer has lost track mostly due to bug #'''
		with MutexStore.getObjectLock(self.getLockIdentifier()):
			print "Rebasing pointer of range: "+str(self.id)
			print "Current pointer point to: "+self.nextAvailableMac
			try:
                    		it= EthernetUtils.getMacIterator(self.startMac,self.endMac)
				while True:
					mac = it.getNextMac()
					if self.__isMacAvailable(mac):
						break
				self.nextAvailableMac= mac
			except Exception as e:
				self.nextAvailableMac = None
			
			print "Pointer will be rebased to: "+self.nextAvailableMac
			self.save()
	
	@staticmethod
	def rebasePointers():
		for range in MacRange.objects.all():
			range.rebasePointer()
		
			
#slot = RangeSlot("127.0.0.1","127.0.0.255","255.255.255.0")

#slot.allocateMac()
#try:
#	slot.releaseMac("d")
#except Exception:
#	pass
#slot.allocateMac()



