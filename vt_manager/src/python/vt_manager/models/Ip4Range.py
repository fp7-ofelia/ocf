from django.db import models
from django.contrib import auth
from threading import Lock
import inspect 
from vt_manager.utils.IP4Utils import IP4Utils 
from vt_manager.utils.MutexStore import MutexStore
from vt_manager.models.Ip4Slot import Ip4Slot

'''
	
	@author: msune
'''

class Ip4Range(models.Model):
	"""Ip4Range"""
	
	class Meta:
		"""Meta Class for your model."""
		app_label = 'vt_manager'

	'''
	Private attributes 
	'''
	#Range name
	name = models.CharField(max_length = 255, default="", verbose_name = "Range name", unique=True)

	isGlobal = models.BooleanField(verbose_name="Global range",default=1, help_text="Global ranges will be used by servers which are not subscribed to any specific range")

	#Range parameters
	startIp = models.IPAddressField(verbose_name = "Range start IP", editable = True, validators = [IP4Utils.checkValidIp])
	endIp = models.IPAddressField(verbose_name = "Range end IP", editable = True, validators = [IP4Utils.checkValidIp])
	netMask = models.IPAddressField(verbose_name = "Network mask", editable = True, validators = [IP4Utils.checkValidNetmask])

	#Networking parameters associated to this range
	gw = models.IPAddressField(blank = True, null=True, validators = [IP4Utils.checkValidIp])
	dns1 = models.IPAddressField(blank = True, null=True, default="10.216.24.2", validators = [IP4Utils.checkValidIp], help_text="DNS1 must be the OFELIA internal 10.216.24.2. It will be used by the VMs to resolve the LDAP address and authenticate users.")
	dns2 = models.IPAddressField(blank = True, null=True, validators = [IP4Utils.checkValidIp])
    
	#Pool of ips both assigned and excluded (particular case of assignment)
	ips = models.ManyToManyField('Ip4Slot', blank = True, null = True, editable = False, related_name = "Ip4Range")
	nextAvailableIp = models.IPAddressField(blank = True, null=True, validators = [IP4Utils.checkValidIp],editable=False,verbose_name="Next available Ip4 slot")

	#Statistics
	numberOfSlots = models.BigIntegerField(blank = True, null=True, editable = False)

	#Mutex
	mutex = None 

	#Defines soft or hard state of the range 
	doSave = True

	
	'''
	Private methods	
	'''
	@staticmethod
	def constructor(name,startIp,endIp,netmask,gw,dns1,dns2,isGlobal=True,save=True):
		self = Ip4Range()
		try:
			#Default constructor
			IP4Utils.checkValidIp(startIp) 
			IP4Utils.checkValidIp(endIp) 
			IP4Utils.checkValidNetmask(netmask)
			IP4Utils.checkValidIp(gw)
			IP4Utils.checkValidIp(dns1)
			if not dns2 == "": 
				IP4Utils.checkValidIp(dns2)
		
			self.name = name
			self.isGlobal= isGlobal
			self.startIp = startIp
			self.endIp = endIp
			self.netMask = netmask
			self.gw = gw
			self.dns1 = dns1
			if not dns2 == "":
				self.dns2 = dns2


			#Create an iterator
			it= IP4Utils.getIpIterator(self.startIp,self.endIp,self.netMask)
			self.nextAvailableIp = it.getNextIp()

			#Number of Slots
			try:
				self.numberOfSlots = IP4Utils.getNumberOfSlotsInRange(startIp,endIp,netmask)
			except Exception as e:
				print "Exception doing slot calculation"+str(e)	
				self.numberOfSlots = -1		
	
			self.doSave = save
			if save:
				self.save()
		except Exception as e:
			#self.delete()
			raise e
		return self

	'''
	Private methods	
	'''
        def __setStartIp(self, value):
		IP4Utils.checkValidIp(value) 
                self.startIp = value
		self.autoSave()

        def __setEndIp(self, value):
		IP4Utils.checkValidIp(value) 
                self.endIp = value
		self.autoSave()


        def __setNetmask(self, value):
		IP4Utils.checkValidNetmask(value) 
                self.netMask = value
		self.autoSave()

	def __isIpAvailable(self,ip):
		return	self.ips.filter(ip=ip).count() == 0
		
	def autoSave(self):
		if self.doSave:
			self.save()
	
	'''
	Public methods	
	'''
	def getLockIdentifier(self):
		#Uniquely identifies object by a key
		return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)
        def getName(self):
                return self.name
        def getIsGlobal(self):
                return self.isGlobal
        def getStartIp(self):
                return self.startIp
        def getEndIp(self):
                return self.endIp
        def getNetmask(self):
                return self.netMask
        def getGatewayIp(self):
                return self.gw
        def getDNS1(self):
                return self.dns1
        def getDNS2(self):
                return self.dns2

	def getExcludedIps(self):
		return self.ips.filter(isExcluded=True).order_by('ip')

 	def getAllocatedIps(self):
		return self.ips.filter(isExcluded=False).order_by('ip')
 
	def getNumberOfSlots(self):
		return int(self.numberOfSlots)
	
	def getPercentageRangeUsage(self):
		if not self.numberOfSlots == -1:
			return float((self.ips.all().count()/self.numberOfSlots)*100)
		return -1

	def destroy(self):
		with MutexStore.getObjectLock(self.getLockIdentifier()):
			if  self.ips.filter(isExcluded=False).count() > 0:
				raise Exception("Cannot delete Ip4Range. Range still contains allocated IPs")
		
			for ip in self.ips.all():
				#Delete excluded ips
				ip.delete()
			self.delete()
			
	def allocateIp(self):
		'''
		Allocates an IP address of the range	
		'''
		with MutexStore.getObjectLock(self.getLockIdentifier()):
			#Implements first fit algorithm
				
			if self.nextAvailableIp == None:
				raise Exception("Could not allocate any IP")
		
			newIp = Ip4Slot.ipFactory(self,self.nextAvailableIp)
			self.ips.add(newIp)
			
			#Try to find new slot
			try:
                        	it= IP4Utils.getIpIterator(self.nextAvailableIp,self.endIp,self.netMask)
				while True:
					ip = it.getNextIp()
					if self.__isIpAvailable(ip):
						break
				self.nextAvailableIp = ip
			except Exception as e:
				self.nextAvailableIp = None
	
			self.autoSave()
			return newIp
		
	def releaseIp(self,ipObj):
		'''
		Releases an IP address of the range (but it does not destroy the object!!)	
		'''
		with MutexStore.getObjectLock(self.getLockIdentifier()):
			ipStr = ipObj.getIp()
			if not self.ips.filter(ip=ipStr,isExcluded=False).count() > 0:
				raise Exception("Cannot release Ip %s. Reason may be is unallocated or is an excluded Ip",ipStr)
					
			self.ips.remove(ipObj)
				
			#Determine new available Ip
			if not self.nextAvailableIp == None:
				if IP4Utils.compareIps(ipStr,self.nextAvailableIp) > 0:
					#Do nothing
					pass
				else:	
					self.nextAvailableIp = ipStr
			else:
				#No more gaps
				self.nextAvailableIp = ipStr

			self.autoSave()

	def addExcludedIp(self,ipStr,comment):
		'''
		Add an IP to the exclusion list	
		'''
		with MutexStore.getObjectLock(self.getLockIdentifier()):
			#Check is not already allocated
			if not  self.__isIpAvailable(ipStr):
				raise Exception("Ip already allocated or marked as excluded")

			#then forbidd
			if not IP4Utils.isIpInRange(ipStr,self.startIp,self.endIp):
				raise Exception("Ip is not in range")
			newIp = Ip4Slot.excludedIpFactory(self,ipStr,comment)
			self.ips.add(newIp)

			#if was nextSlot shift
			if self.nextAvailableIp == ipStr:
				try:
                        		it= IP4Utils.getIpIterator(self.nextAvailableIp,self.endIp,self.netMask)
					while True:
						ip = it.getNextIp()
						if self.__isIpAvailable(ip):
							break
					self.nextAvailableIp = ip
				except Exception as e:
					self.nextAvailableIp = None
			
			self.autoSave()
		
	def removeExcludedIp(self,ipObj):
		'''
		Deletes an IP from the exclusion list (but it does not destroy the object!!)
		'''	
		with MutexStore.getObjectLock(self.getLockIdentifier()):
			ipStr = ipObj.getIp()
			if not self.ips.get(ip=ipStr).isExcludedIp():
				raise Exception("Cannot release Ip. Reason may be is unallocated or is not excluded Ip")
	
			self.ips.remove(ipObj)

			#Determine new available Ip
			if not self.nextAvailableIp == None:
				if IP4Utils.compareIps(ipStr,self.nextAvailableIp) > 0:
					#Do nothing
					pass
				else:	
					self.nextAvailableIp = ipStr
			else:
				#No more gaps
				self.nextAvailableIp = ipStr

	
			self.autoSave()
	
	'''
	Static methods
	'''
	@staticmethod
	def getAllocatedGlobalNumberOfSlots():
		allocated = 0
		for range in Ip4Range.objects.filter(isGlobal=True):
			allocated += range.ips.all().count()
		return allocated
			
	@staticmethod
	def getGlobalNumberOfSlots():
		slots = 0
		for range in Ip4Range.objects.filter(isGlobal=True):
			slots += range.numberOfSlots
		return int(slots)
	
	
	def rebasePointer(self):
		'''Used when pointer has lost track mostly due to bug #'''
		with MutexStore.getObjectLock(self.getLockIdentifier()):
			print "Rebasing pointer of range: "+str(self.id)
			print "Current pointer point to: "+self.nextAvailableIp
			try:
                        	it= IP4Utils.getIpIterator(self.startIp,self.endIp,self.netMask)
				while True:
					ip = it.getNextIp()
					if self.__isIpAvailable(ip):
						break
				self.nextAvailableIp = ip
			except Exception as e:
					self.nextAvailableIp = None
			
			print "Pointer will be rebased to: "+self.nextAvailableIp
			self.save()
	
	@staticmethod
	def rebasePointers():
		'''Used when pointer has lost track mostly due to bug #'''
		for range in Ip4Range.objects.all():
			range.rebasePointer()	

#slot = RangeSlot("127.0.0.1","127.0.0.255","255.255.255.0")

#slot.allocateIp()
#try:
#	slot.releaseIp("d")
#except Exception:
#	pass
#slot.allocateIp()



