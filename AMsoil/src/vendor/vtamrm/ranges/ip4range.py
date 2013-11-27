from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import TINYINT, BIGINT
from sqlalchemy.orm import validates, relationship

import inspect

from utils.commonbase import Base, DB_SESSION
from utils.ip4utils import IP4Utils
from resources.ip4slot import Ip4Slot
from ranges.ip4rangeips import Ip4RangeIps
from utils.mutexstore import MutexStore

import amsoil.core.log

logging=amsoil.core.log.getLogger('Ip4Range')



'''@author: SergioVidiella'''


class Ip4Range(Base):
    """Ip4Range."""

    __tablename__ = 'vt_manager_ip4range'

    id = Column(Integer, autoincrement=True, nullable=False,primary_key=True)

    #Range name
    name = Column(String(255), nullable=False, unique=True)
    isGlobal = Column(TINYINT(1), nullable=False)

    #Range parameters
    startIp = Column(String(15), nullable=False)
    endIp = Column(String(15), nullable=False)
    netMask = Column(String(15), nullable=False)

    #Networking parameters associated to this range
    gw = Column(String(15))
    dns1 = Column(String(15))
    dns2 = Column(String(15))

    #Statistics
    numberOfSlots = Column(BIGINT(20))
    
    #Pool of ips both assigned and excluded (particular case of assignment)
    nextAvailableIp = Column(String(15))
    ip4s = relationship("Ip4RangeIps")

    @staticmethod
    def constructor(name, startIp, endIp, netmask, gw, dns1, dns2, isGlobal=True):
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
	except Exception as e:
            raise e
        return self

    '''Validators'''
    @validates('startIp')
    def validate_startip(self, key, ip):
        try:
            IP4Utils.checkValidIp(ip)
            return ip
        except Exception as e:
            raise e

    @validates('endIp')
    def validate_endip(self, key, ip):
        try:
            IP4Utils.checkValidIp(ip)
            return ip
        except Exception as e:
            raise e

    @validates('netmask')
    def validate_netmask(self, key, netmask):
        try:
            IP4Utils.checkValidNetmask(netmask)
            return netmask
        except Exception as e:
            raise e

    @validates('gw')
    def validate_gw(self, key, gw):
        try:
            IP4Utils.checkValidIp(gw)
            return gw
        except Exception as e:
            raise e
 
    @validates('dns1')
    def validate_dns1(self, key, dns):
        try:
            IP4Utils.checkValidIp(dns)
            return dns
        except Exception as e:
            raise e

    @validates('dns2')
    def validate_dns2(self, key, dns):
        try:
            IP4Utils.checkValidIp(dns)
            return dns
        except Exception as e:
            raise e

    @validates('nextAvailableIp')
    def validate_next_available_ip(self, key, ip):
        try:
            IP4Utils.checkValidIp(ip)
            return ip
        except Exception as e:
            raise e

    '''Private methods'''
    def __setStartIp(self, value):
    	IP4Utils.checkValidIp(value)
        self.startIp = value

    def __setEndIp(self, value):
        IP4Utils.checkValidIp(value)
        self.endIp = value

    def __setNetmask(self, value):
        IP4Utils.checkValidNetmask(value)
        self.netMask = value

    def __isIpAvailable(self,ip):
        return  DB_SESSION.query(Ip4RangeIps).filter(Ip4RangeIps.ip4range_id == self.id).join(Ip4RangeIps.ip4slot, aliased=True).filter(Ip4Slot.ip == ip).count() == 0

    '''Public methods'''
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

    def allocateIp(self):
        '''
        Allocates an IP address of the range    
        '''
        with MutexStore.getObjectLock(self.getLockIdentifier()):                        
	    logging.debug("******************************************* RANGEIP 1")
	    #Implements first fit algorithm
            if self.nextAvailableIp == None:                                
		logging.debug("******************************************* RANGEIP ERROR 1")
		raise Exception("Could not allocate any IP")
	    logging.debug("******************************************* RANGEIP 2")
	    newIp = Ip4Slot.ipFactory(self,self.nextAvailableIp)
	    logging.debug("******************************************* RANGEIP 3")
	    DB_SESSION.add(newIp)
            DB_SESSION.commit()
            newIpRangeIp = Ip4RangeIps()
            newIpRangeIp.ip4range_id = self.id
            newIpRangeIp.ip4slot_id = newIp.id
            DB_SESSION.add(newIpRangeIp)
            DB_SESSION.commit()
	    logging.debug("******************************************* RANGEIP 4")
	    #Try to find new slot
            try:
		logging.debug("******************************************* RANGEIP 5")
            	it= IP4Utils.getIpIterator(self.nextAvailableIp,self.endIp,self.netMask)
		logging.debug("******************************************* RANGEIP 6")
                while True:
                    ip = it.getNextIp()
		    logging.debug("******************************************* RANGEIP 7 " + str(ip))
                    if self.__isIpAvailable(ip):
			logging.debug("******************************************* RANGEIP 9")
                    	break
                    self.nextAvailableIp = ip
		    logging.debug("******************************************* RANGEIP 8")
            except Exception as e:
		logging.debug("******************************************* RANGEIP ERROR 2 " + str(e))
            	self.nextAvailableIp = None
	    logging.debug("******************************************* RANGEIP 10")
	    return newIp                                                                             

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
	    DB_SESSION.add(newIp)
            DB_SESSION.commit()
            newIpRangeIp = Ip4RangeIps()
            newIpRangeIp.ip4range_id = self.id
            newIpRangeIp.ip4slot_id = newIp.id
            DB_SESSION.add(newIpRangeIp)
            DB_SESSION.commit()
	    #if was nextSlot shift
            if self.nextAvailableIp == ipStr:
            	try:
                    it= IP4Utils.getIpIterator(self.nextAvailableIp,self.endIp,self.netMask)
                    while True:
                    	ip = it.getNextIp()
                        if self.__isIpAvailable(ip):
                            break
		except Exception as e:
                    self.nextAvailableIp = None


