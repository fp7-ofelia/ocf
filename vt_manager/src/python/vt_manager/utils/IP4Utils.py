from array import *
import re



IP4_MIN_VALUE=0
IP4_MAX_VALUE=255

class IP4Validator:

	@staticmethod
	def validateIp(ip):

		controlIp = re.compile(r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}(/\d?\d)?$')
		if not controlIp.match(ip):
			raise Exception("Invalid IP format")

	@staticmethod
	def validateNetmask(mask):
		splitted = mask.split(".")
		netmaskStarted=False
		i=3
		while True:
			j=0
			value = int(splitted[i])&255
			while True:
				if not value&0x01 == 0x01:
					if netmaskStarted:
						raise Exception("Invalid Netmask format")	
				else:
					netmaskStarted = True	
				if j<7:
					value=value>>1
					j+=1
				else: 	
					break
			if i>0:
				i-=1
			else:
				break

	@staticmethod
	def __convertToNumericValue(ip):
		value =  ip.split(".")
		return (int(value[0]) <<24) + (int(value[1]) <<16) +  (int(value[2]) <<8) + (int(value[3]))

	@staticmethod
	def compareIps(a,b):
		return IP4Validator.__convertToNumericValue(a) -  IP4Validator.__convertToNumericValue(b) 

	@staticmethod
	def isIpInRange(ip,start,end):
		IP4Validator.validateIp(ip)	
		IP4Validator.validateIp(start)	
		IP4Validator.validateIp(end)	
		
		return IP4Validator.__convertToNumericValue(ip)>=IP4Validator.__convertToNumericValue(start) and  IP4Validator.__convertToNumericValue(ip)<=IP4Validator.__convertToNumericValue(end)

	@staticmethod
	def getNumberOfSlotsInRange(start,end,netmask):
		IP4Utils.checkValidIp(start)
		IP4Utils.checkValidIp(end)
		IP4Utils.checkValidNetmask(netmask)
	
		endNumeric = IP4Validator.__convertToNumericValue(end)
		startNumeric = IP4Validator.__convertToNumericValue(start)
		netmaskNumeric = IP4Validator.__convertToNumericValue(netmask)

		import math

		value =  netmask.split(".")
		shift = 0
		for i in range(0,4):
			if not int(value[i]) == 0:
				shift += round(math.log(int(value[i]),2),0)
		shift = 32 - int(shift)
		#print "Shift value is: "+str(shift)
		#print "Numeric:"+str(endNumeric)+" shift:"+str(shift)+" startNumeric:"+str(startNumeric)
		#print "Numeric:"+str(endNumeric>>shift)+" startNumeric:"+str(startNumeric>>shift)
		#print str(int(endNumeric>>shift))+"-"+str(int(startNumeric>>shift))
		nsubnet = int(endNumeric>>shift)- int(startNumeric>>shift)
		#print "Number of subnets"+str(nsubnet)	
		slots = endNumeric - startNumeric - 2*(nsubnet+1) +1
		#Substract broadcast
		return slots
	
	
class IP4Iterator:
	#TODO: this is not thread safe!
	_ip = array('l',[0,0,0,0]) 
	_startRangeIp = array('l',[0,0,0,0]) 
	_endRangeIp = array('l',[0,0,0,0]) 
	_netmask = array('l',[0,0,0,0]) 
	_isFirstIncrement=True
	'''
	Constructor
	'''	
	def __init__(self,startip,endip,netmask):
		
		#Check well formed IPs
		IP4Utils.checkValidIp(startip)
		IP4Utils.checkValidIp(endip)
		IP4Utils.checkValidNetmask(netmask)

		#Check Range
		if IP4Validator.compareIps(startip,endip) >= 0:
			raise Exception("Invalid Range")


		splitted = startip.split(".")
		
		#Translate IP
		self._ip[0] = int(splitted[0]) 
		self._ip[1] = int(splitted[1])
		self._ip[2] = int(splitted[2])
		self._ip[3] = int(splitted[3])
		#Put start
		self._startRangeIp[0] = int(splitted[0]) 
		self._startRangeIp[1] = int(splitted[1])
		self._startRangeIp[2] = int(splitted[2])
		self._startRangeIp[3] = int(splitted[3])


		splitted = netmask.split(".")

		#Translate Netmask
		self._netmask[0] = int(splitted[0]) 
		self._netmask[1] = int(splitted[1])
		self._netmask[2] = int(splitted[2])
		self._netmask[3] = int(splitted[3])
		
		splitted = endip.split(".")
		
		#Put end
		self._endRangeIp[0] = int(splitted[0]) 
		self._endRangeIp[1] = int(splitted[1])
		self._endRangeIp[2] = int(splitted[2])
		self._endRangeIp[3] = int(splitted[3])


	'''
	Private method that increments IP
	'''
	def __increment(self,i=3):
		self._ip[i]+=1
		if self._ip[i] > IP4_MAX_VALUE:
			self._ip[i] = IP4_MIN_VALUE
			if i != 0: 
				self.__increment(i-1)
			else:
				raise Exception("No more IPs")
	'''
	Private method that decrements IP
	'''
	def __decrement(self,i=3):
		self._ip[i]-=1
		if self._ip[i] < IP4_MIN_VALUE:
			self._ip[i] = IP4_MAX_VALUE
			if i != 0: 
				self.__decrement(i-1)
			else:
				raise Exception("No more IPs")


	'''Checkings'''
	def __getCurrentNetworkSegment(self):
		toreturn = array('l',[0,0,0,0]) 
		toreturn[0] = self._ip[0] & self._netmask[0]
		toreturn[1] = self._ip[1] & self._netmask[1]
		toreturn[2] = self._ip[2] & self._netmask[2]
		toreturn[3] = self._ip[3] & self._netmask[3]
		return toreturn 

	def __isBroadcastIp(self):
		self.__increment()
		toReturn = self.__isNetworkIp()
		self.__decrement()
		return toReturn
	
	def __isNetworkIp(self):
		net = self.__getCurrentNetworkSegment() 
		return net[0] == self._ip[0] and net[1] == self._ip[1] and net[2] == self._ip[2] and net[3] == self._ip[3]
		
	def __isBroadcastOrNetworkIp(self):
		return self.__isBroadcastIp() or self.__isNetworkIp()
	
	def __convertToNumericValue(self,value):
		return (value[0] <<24) + (value[1] <<16) +  (value[2] <<8) + (value[3])

	def __isIpNotInRange(self):
		return self.__convertToNumericValue(self._startRangeIp)>self.__convertToNumericValue(self._ip) or self.__convertToNumericValue(self._endRangeIp)<self.__convertToNumericValue(self._ip)

	'''
	Public method that gets current IP
	'''

	def getPointedIpAsString(self):
		return str(self._ip[0])+"."+str(self._ip[1])+"."+str(self._ip[2])+"."+str(self._ip[3])

	'''
	Public method that increments IP and returns the next non-broadcast non-network ip of the iteration
	'''

	def getNextIp(self):
		while True:
			if not self._isFirstIncrement:
				#increment
				self.__increment()
			else:
				self._isFirstIncrement = False
			
			#Check if we are in range
			if self.__isIpNotInRange():
				raise Exception("No More Ips")
	

			#Check if broadcast or network
			if not self.__isBroadcastOrNetworkIp():
				break

	
		#return stringified IP
		return self.getPointedIpAsString()
	
	'''
	Public method that decrements IP and returns the next non-broadcast non-network ip of the iteration
	'''

	def getPreviousIp(self):
		while True:
			if not self._isFirstIncrement:
				#increment
				self.__decrement()
			else:
				self._isFirstIncrement = False
			
			#Check if we are in range
			if self.__isIpNotInRange():
				raise Exception("No More Ips")
	
			#Check if broadcast or network
			if not self.__isBroadcastOrNetworkIp():
				break

		#return stringified IP
		return self.getPointedIpAsString()
	
class IP4Utils():

	@staticmethod
	def checkValidIp(ip):
		return IP4Validator.validateIp(ip)

	@staticmethod
	def isIpInRange(ip,start,end):
		return IP4Validator.isIpInRange(ip,start,end)
	@staticmethod
	def compareIps(a,b):
		return IP4Validator.compareIps(a,b)

	@staticmethod
	def checkValidNetmask(ip):
		return IP4Validator.validateNetmask(ip)
		
	
	@staticmethod
	def getIpIterator(ipStart,ipEnd,netmask):
		return IP4Iterator(ipStart,ipEnd,netmask)

	
	@staticmethod
	def getNumberOfSlotsInRange(start,end,netmask):
		return IP4Validator.getNumberOfSlotsInRange(start,end,netmask)
		



#it = IP4Utils.getIpIterator("192.168.0.0","192.168.1.255","255.255.255.0")
#print IP4Utils.getNumberOfSlotsInRange("192.168.0.0","192.168.10.255","255.255.255.0")

#print it.getPointedIpAsString()
#i=0
#while True:
#	print it.getNextIp()
#	i+=1
#	if i >512:
#		break
print 
#IP4Utils.checkValidNetmask("240.0.0.0")

