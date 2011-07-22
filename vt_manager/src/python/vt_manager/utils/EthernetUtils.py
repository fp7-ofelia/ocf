from array import *
import re
from django.core.exceptions import ValidationError

ETH_MIN_VALUE=0
ETH_MAX_VALUE=255


class EthernetMacValidator:

	@staticmethod
	def validateMac(mac):
		Mac_RE = r'^([0-9a-fA-F]{2}([:-]?|$)){6}$'
		mac_re = re.compile(Mac_RE)			
		
		if not mac_re.match(mac):
			raise ValidationError("Invalid Ethernet Mac format")

	@staticmethod
        def _dec2hex(n):
                """return the hexadecimal string representation of integer n"""
                return "%02X" % n
	@staticmethod
        def _hex2dec(s):
                """return the integer value of a hexadecimal string s"""
                return int(s, 16)
	
	
	@staticmethod
	def __convertToNumericValue(mac):
		value =  mac.split(":")
		return (EthernetMacValidator._hex2dec(value[0]) <<40) +(EthernetMacValidator._hex2dec(value[1]) <<32) +(EthernetMacValidator._hex2dec(value[2]) <<24) + (EthernetMacValidator._hex2dec(value[3]) <<16) +  (EthernetMacValidator._hex2dec(value[4]) <<8) + (EthernetMacValidator._hex2dec(value[5]))
	
	@staticmethod
	def compareMacs(a,b):
		return EthernetMacValidator.__convertToNumericValue(a) -  EthernetMacValidator.__convertToNumericValue(b) 

	@staticmethod
	def isMacInRange(mac,start,end):
		EthernetMacValidator.validateMac(mac)	
		EthernetMacValidator.validateMac(start)	
		EthernetMacValidator.validateMac(end)	
		
		return EthernetMacValidator.__convertToNumericValue(mac)>=EthernetMacValidator.__convertToNumericValue(start) and  EthernetMacValidator.__convertToNumericValue(mac)<=EthernetMacValidator.__convertToNumericValue(end)

	
class EthernetMacIterator:

	#TODO: this is not thread safe!
	_mac = array('l',[0,0,0,0,0,0]) 
	_startRangeMac = array('l',[0,0,0,0,0,0]) 
	_endRangeMac = array('l',[0,0,0,0,0,0]) 
	
	_network = array('l',[0,0,0,0,0,0])
	_broadcast = array('l',[255,255,255,255,255,255])
	_isFirstIncrement=True
	'''
	Constructor
	'''	
	def __init__(self,startmac,endmac):
	
		#Check well formed MAC
		EthernetUtils.checkValidMac(startmac)
		EthernetUtils.checkValidMac(endmac)

		#Check Range
		if EthernetMacValidator.compareMacs(startmac,endmac) >= 0:
			raise Exception("Invalid Range")

		splitted = startmac.split(":")
		
		#Translate MAC
		self._mac[0] = self._hex2dec(splitted[0]) 
		self._mac[1] = self._hex2dec(splitted[1])
		self._mac[2] = self._hex2dec(splitted[2])
		self._mac[3] = self._hex2dec(splitted[3])
		self._mac[4] = self._hex2dec(splitted[4])
		self._mac[5] = self._hex2dec(splitted[5])

		#Put start
		self._startRangeMac[0] = self._hex2dec(splitted[0]) 
		self._startRangeMac[1] = self._hex2dec(splitted[1])
		self._startRangeMac[2] = self._hex2dec(splitted[2])
		self._startRangeMac[3] = self._hex2dec(splitted[3])
		self._startRangeMac[4] = self._hex2dec(splitted[4])
		self._startRangeMac[5] = self._hex2dec(splitted[5])

		splitted = endmac.split(":")
	
		#Put end
		self._endRangeMac[0] = self._hex2dec(splitted[0]) 
		self._endRangeMac[1] = self._hex2dec(splitted[1])
		self._endRangeMac[2] = self._hex2dec(splitted[2])
		self._endRangeMac[3] = self._hex2dec(splitted[3])
		self._endRangeMac[4] = self._hex2dec(splitted[4])
		self._endRangeMac[5] = self._hex2dec(splitted[5])
		
	
	'''
	Hexadecimal aids
	'''
	def _dec2hex(self,n):
		"""return the hexadecimal string representation of integer n"""
		return "%02X" % n
	def _hex2dec(self,s):
		"""return the integer value of a hexadecimal string s"""
		return int(s, 16)

	'''
	Private method that increments Mac
	'''
	def __increment(self,i=5):
		self._mac[i]+=1
		if self._mac[i] > ETH_MAX_VALUE:
			self._mac[i] = ETH_MIN_VALUE
			if i != 0: 
				self.__increment(i-1)
			else:
				raise Exception("No more MACs")
	'''
	Private method that decrements Mac
	'''
	def __decrement(self,i=5):
		self._mac[i]-=1
		if self._mac[i] < ETH_MIN_VALUE:
			self._mac[i] = ETH_MAX_VALUE
			if i != 0: 
				self.__decrement(i-1)
			else:
				raise Exception("No more MACs")


	'''Checkings'''
	def __isBroadcastMac(self):
		return self._mac[0] == ETH_MAX_VALUE and self._mac[1] == ETH_MAX_VALUE and self._mac[2] == ETH_MAX_VALUE and self._mac[3] == ETH_MAX_VALUE and self._mac[4] == ETH_MAX_VALUE and self._mac[5] == ETH_MAX_VALUE
	
	def __isNetworkMac(self):
		return self._mac[0] == ETH_MIN_VALUE and self._mac[1] == ETH_MIN_VALUE and self._mac[2] == ETH_MIN_VALUE and self._mac[3] == ETH_MIN_VALUE and self._mac[4] == ETH_MIN_VALUE and self._mac[5] == ETH_MIN_VALUE
		
	def __isBroadcastOrNetworkMac(self):
		return self.__isBroadcastMac() or self.__isNetworkMac()
	
	def __convertToNumericValue(self,value):
		return (value[0] <<40) + (value[1] <<32) +  (value[2] <<24) + (value[3]<<16)+(value[4]<<8)+(value[5])

	def __isMacNotInRange(self):
		return self.__convertToNumericValue(self._startRangeMac)>self.__convertToNumericValue(self._mac) or self.__convertToNumericValue(self._endRangeMac)<self.__convertToNumericValue(self._mac)

	'''
	Public method that gets current Mac
	'''
	def getPointedMacAsString(self):
		return self._dec2hex(self._mac[0])+":"+self._dec2hex(self._mac[1])+":"+self._dec2hex(self._mac[2])+":"+self._dec2hex(self._mac[3])+":"+self._dec2hex(self._mac[4])+":"+self._dec2hex(self._mac[5])

	'''
	Public method that increments IP and returns the next non-broadcast non-network ip of the iteration
	'''

	def getNextMac(self):
		while True:
			if not self._isFirstIncrement:
				#increment
				self.__increment()
			else:
				self._isFirstIncrement = False
			
			#Check if we are in range
			if self.__isMacNotInRange():
				raise Exception("No More MACs")
	

			#Check if broadcast or network
			if not self.__isBroadcastOrNetworkMac():
				break

		#return stringified IP
		return self.getPointedMacAsString()
	
	'''
	Public method that decrements IP and returns the next non-broadcast non-network ip of the iteration
	'''

	def getPreviousMac(self):
		while True:
			if not self._isFirstIncrement:
				#increment
				self.__decrement()
			else:
				self._isFirstIncrement = False
	
			#Check if we are in range
			if self.__isMacNotInRange():
				raise Exception("No More MACs")
	
			#Check if broadcast or network
			if not self.__isBroadcastOrNetworkMac():
				break

		#return stringified IP
		return self.getPointedMacAsString()
	
class EthernetUtils():

	@staticmethod
	def checkValidMac(mac):
		return EthernetMacValidator.validateMac(mac)

	@staticmethod
	def getMacIterator(macStart,macEnd):
		return EthernetMacIterator(macStart,macEnd)

	@staticmethod
	def isMacInRange(mac,start,end):
		return EthernetMacValidator.isMacInRange(mac,start,end)
	@staticmethod
	def compareMacs(a,b):
		return EthernetMacValidator.compareMacs(a,b)

	@staticmethod
	def getNumberOfSlotsInRange(start,end):
		EthernetUtils.checkValidMac(start)	
		EthernetUtils.checkValidMac(end)	
		
		slots = abs(EthernetMacValidator.compareMacs(end,start))

		#Substract broadcast
		if EthernetUtils.isMacInRange("00:00:00:00:00:00",start,end):
			slots -=1	
		return slots


#it = EthernetUtils.getMacIterator("FF:FF:FF:FF:FE:00","FF:FF:FF:FF:FF:FF")

#print it.getPointedMacAsString()
#i=0
#while True:
#	print it.getNextMac()
#	i+=1
#	if i >1024:
#		break
#print EthernetUtils.getNumberOfSlotsInRange("00:00:00:00:00:00","FF:FF:FF:FU:FF:FF")
#EthernetUtils.checkValidMac("00:11:22:11f:aa:bb")

