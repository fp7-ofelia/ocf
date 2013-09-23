from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import TINYINT, BIGINT
from sqlalchemy.orm import validates, relationship

import inspect

from utils.commonbase import Base
from utils.ethernetutils import EthernetUtils
from resources.macslot import MacSlot
from ranges.macrangemacs import MacRangeMacs


'''@author: SergioVidiella'''


class MacRange(Base):
    """MacRange."""

    __tablename__ = 'vt_manager_macrange'

    id = Column(Integer, autoincrement=True, nullable=False,primary_key=True)

    #Range name
    name = Column(String(255), nullable=False, unique=True)
    isGlobal = Column(TINYINT(1), nullable=False)

    #Range parameters
    startMac = Column(String(17), nullable=False)
    endMac = Column(String(17), nullable=False)

    #Pool of ips both assigned and excluded (particular case of assignment)
    macs = relationship("MacRangeMacs")
    nextAvailableMac = Column(String(17))

    #Statistics
    numberOfSlots = BIGINT(20)
    

    @staticmethod
    def constructor(name, startMac, endMac, isGlobal=True):
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
	except Exception as e:
            print e
            raise e
        return self

    '''Validators'''
    @validates('startMac')
    def validate_startmac(self, key, mac):
        try:
            EthernetUtils.checkValidMac(mac)
            return mac
        except Exception as e:
            raise e

    @validates('endMac')
    def validate_endip(self, key, mac):
        try:
            IP4Utils.checkValidMac(mac)
            return mac
        except Exception as e:
            raise e

    '''Private methods'''
    def __setStartMac(self, value):
    	EthernetUtils.checkValidMac(value)
        self.starMac = value.upper()

    def __setEndMac(self, value):
        EthernetUtils.checkValidMac(value)
        self.endMac = value.upper()

    def __isMacAvailable(self,ip):
        return  self.macs.filter(mac=mac).count() == 0

    '''Public methods'''
    def getLockIdentifier(self):
   	#Uniquely identifies object by a key
        return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)

    def getName(self):
        return self.name

    def getIsGlobal(self):
        return self.isGlobal
   
    def getStartMac(self):
   	return self.startMac
        
    def getEndMac(self):
        return self.endMac
        
    def getExcludedMacs(self):
        return self.macs.filter(isExcluded=True).order_by('mac')

    def getAllocatedMacs(self):
        return self.macs.filter(isExcluded=False).order_by('mac')

    def getNumberOfSlots(self):
        return int(self.numberOfSlots)

    def getPercentageRangeUsage(self):
        if not self.numberOfSlots == -1:
            return float((self.macs.all().count()/self.numberOfSlots)*100)
        return -1

    def allocateMac(self):
        '''
        Allocates a MAC address of the range    
        '''
        with MutexStore.getObjectLock(self.getLockIdentifier()):                        
	#Implements first fit algorithm
            if self.nextAvailableIp == None:                                
		raise Exception("Could not allocate any MAC")
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
	    return newMac                                                                             

    def addExcludedMac(self,macStr,comment=""):
    	'''
        Add a MAC to the exclusion list 
        '''
        with MutexStore.getObjectLock(self.getLockIdentifier()):
            #Check is not already allocated
            if not  self.__isMacAvailable(ipStr):
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
		except Exception as e:
                    self.nextAvailableMac = None


