from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import TINYINT, DOUBLE, VARCHAR
from sqlalchemy.orm import validates, relationship, backref

import uuid
import inspect

from utils.commonbase import Base, DB_SESSION
from utils import validators
from utils.choices import VirtTechClass, OSDistClass, OSVersionClass, OSTypeClass
from utils.mutexstore import MutexStore

from interfaces.networkinterface import NetworkInterface
from interfaces.servernetworkinterfaces import VTServerNetworkInterfaces

from ranges.servermacrange import VTServerMacRange
from ranges.serveriprange import VTServerIpRange
from ranges.macrange import MacRange
from ranges.ip4range import Ip4Range 

import amsoil.core.log

logging=amsoil.core.log.getLogger('VTServer')



'''@author: SergioVidiella'''



def validateAgentURLwrapper(url):
        VTServer.validateAgentURL(url)

class VTServer(Base):
    """Virtualization Server Class."""

    __tablename__ = 'vt_manager_vtserver'

    __childClasses = (
    'XenServer',
       )
    
#    xenserver = relationship("XenServer", backref="vtserver", cascade="all, delete-orphan", lazy='dynamic', passive_deletes=True)

    '''General attributes'''
    id = Column(Integer, autoincrement=True, primary_key=True)
    available = Column(TINYINT(1), nullable=False, default=1)
    enabled = Column(TINYINT(1), nullable=False, default=1)
    name = Column(VARCHAR(length=511), nullable=False, default="")
    uuid = Column(String(1024), nullable=False, default=uuid.uuid4())

    '''OS'''
    operatingSystemType = Column(String(512), nullable=False)
    operatingSystemDistribution = Column(String(512), nullable=False)
    operatingSystemVersion = Column(String(512), nullable=False)

    '''Virtualization Technology'''
    virtTech = Column(String(512), nullable=False)

    ''' Hardware '''
    numberOfCPUs = Column(Integer)
    CPUFrequency = Column(Integer)
    memory = Column(Integer)
    discSpaceGB = Column(DOUBLE)

    '''Agent Fields'''
    agentURL = Column(String(200))
    agentPassword = Column(String(128))
    url = Column(String(200))

    '''Network interfaces'''
    networkInterfaces = relationship("VTServerNetworkInterfaces", backref="vtserver")

    '''Other networking parameters'''
    subscribedMacRanges = relationship("VTServerMacRange", backref="vtserver", lazy='dynamic')
    subscribedIp4Ranges = relationship("VTServerIpRange", backref="vtserver", lazy='dynamic')

    ''' Mutex over the instance '''
    mutex = None

    '''Validators'''
    @validates('name')
    def validate_name(self, key, name):
        try:
	    validators.resource_name_validator(name)
            return name
        except Exception as e:
            raise e

    @validates('operatingSystemType')
    def validate_operatingsystemtype(self, key, os_type):
        try:
	    OSTypeClass.validateOSType(os_type)
            return os_type
        except Exception as e:
            raise e

    @validates('operatingSystemDistribution')
    def validate_operatingsystemdistribution(self, key, os_distribution):
        try:
            OSDistClass.validateOSDist(os_distribution)
            return os_distribution
        except Exception as e:
            raise e

    @validates('operatingSystemVersion')
    def validate_operatingsystemversion(self, key, os_version):
        try:
	    OSVersionClass.validateOSVersion(os_version)
            return os_version
        except Exception as e:
            raise e

    @validates('virtTech')
    def validate_virttech(self, key, virt_tech):
        try:
            VirtTechClass.validateVirtTech(virt_tech)
            return virt_tech
        except Exception as e:
            raise e

    @validates('agentURL')
    def validate_agenturl(self, key, agent_url):
        try:
            validateAgentURLwrapper(agent_url)
            return agent_url
        except Exception as e:
            raise e

    @validates('agentPassword')
    def validate_agentpassword(self, key, agent_password):
        try:
            validators.resource_name_validator(agent_password)
            return agent_password
        except Exception as e:
            raise e

    '''Private methods'''
    def getChildObject(self):
   	for childClass in self.__childClasses:
            try:
            	return self.__getattribute__(childClass.lower())[0]
            except Exception:
                pass
            
    def __tupleContainsKey(tu,key):
   	for val in tu:
            if val[0] == key:
             	return True
            return False

    def getLockIdentifier(self):
    	#Uniquely identifies object by a key
        return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)

    def destroy(self):
    	with MutexStore.getObjectLock(self.getLockIdentifier()):
	    if self.vms.all().count()>0:
            	raise Exception("Cannot destroy a server which hosts VMs. Delete VMs first")
	    #Delete associated interfaces
            for interface in self.networkInterfaces.all():
            	interface.destroy()
		#Delete instance
                self.delete()

    '''Getters and Setters'''
    def setName(self, name):
	validators.resource_name_validator(name)
        self.name = name

    def getName(self):
    	return self.name
        
    def setUUID(self, uuid):
    	self.uuid = uuid
        
    def getUUID(self):
        return self.uuid
    
    def setMemory(self,memory):
        self.memory = memory

    def getMemory(self):
        return self.memory

    def setAgentURL(self, url):
        with MutexStore.getObjectLock(self.getLockIdentifier()):
   	    VTServer.validateAgentURL(url)
            self.agentURL = url
        
    def getAgentURL(self):
        return self.agentURL
       
    def setURL(self, url):
        self.url = url
      
    def getURL(self):
   	return self.url
        
    def setVirtTech(self, virtTech):
        VirtTechClass.validateVirtTech(virtTech)
        self.virtTech = virtTech
        
    def getVirtTech(self):
        return self.virtTech
    
    def setOSType(self, osType):
        OSTypeClass.validateOSType(osType)
        self.operatingSystemType = osType
        
    def getOSType(self):
        return self.operatingSystemType

    def setOSVersion(self, version):
        OSVersionClass.validateOSVersion(version)
        self.operatingSystemVersion = version
        
    def getOSVersion(self):
        return self.operatingSystemVersion
       
    def setOSDistribution(self, dist):
        OSDistClass.validateOSDist(dist)
        self.operatingSystemDistribution = dist
        
    def getOSDistribution(self):
        return self.operatingSystemDistribution
    
    def setAvailable(self,av):
        self.available = av
        
    def getAvailable(self):
        return self.available
    
    def setEnabled(self,en):
        self.enabled = en
        
    def getEnabled(self):
        return self.enabled
    
    def getAgentPassword(self):
        return self.agentPassword
 
    def setAgentPassword(self, password):
        self.agentPassword = password

    ''' Ranges '''
    def subscribeToMacRange(self,newRange):
	if not isinstance(newRange,MacRange):
            raise Exception("Invalid instance type on subscribeToMacRange; must be MacRange")
        if newRange in self.subscribedMacRanges.all():
            raise Exception("Server is already subscribed to this range")
        self.subscribedMacRanges.add(newRange)

    def unsubscribeToMacRange(self,oRange):
        if not isinstance(oRange,MacRange):
            raise Exception("Invalid instance type on unsubscribeToMacRange; must be MacRange")
        self.subscribedMacRanges.remove(oRange)

    def getSubscribedMacRangesNoGlobal(self):
        return DB_SESSION.query(MacRange).join(MacRange.vtserver_association, aliased=True).filter(VTServerMacRange.vtserver_id == self.id).all()

    def getSubscribedMacRanges(self):
        if self.subscribedMacRanges.count() > 0:
            return DB_SESSION.query(MacRange).join(MacRange.vtserver_association, aliased=True).filter(VTServerMacRange.vtserver_id == self.id).all()
        else:
            #Return global (all) ranges
            return DB_SESSION.query(MacRange).filter(MacRange.isGlobal == True).all()

    def subscribeToIp4Range(self,newRange):
        if not isinstance(newRange,Ip4Range):
            raise Exception("Invalid instance type on subscribeToIpRange; must be Ip4Range")
        if newRange in self.subscribedIp4Ranges.all():
            raise Exception("Server is already subscribed to this range")
	self.subscribedIp4Ranges.add(newRange)

    def unsubscribeToIp4Range(self,oRange):
        if not isinstance(oRange,Ip4Range):
            raise Exception("Invalid instance type on unsubscribeToIpRange; must be Ip4Range")
	self.subscribedIp4Ranges.remove(oRange)

    def getSubscribedIp4RangesNoGlobal(self):
        return DB_SESSION.query(Ip4Range).join(Ip4Range.vtserver_association, aliased=True).filter(VTServerIpRange.vtserver_id == self.id).all()

    def getSubscribedIp4Ranges(self):
        if self.subscribedIp4Ranges.count() > 0:
            return DB_SESSION.query(Ip4Range).join(Ip4Range.vtserver_association, aliased=True).filter(VTServerIpRange.vtserver_id == self.id).all()
        else:
            #Return global (all) ranges
            return DB_SESSION.query(Ip4Range).filter(Ip4Range.isGlobal == True).all()

    def __allocateMacFromSubscribedRanges(self):
	logging.debug("************************* MAC 1")
        macObj = None
        #Allocate Mac
        for macRange in self.getSubscribedMacRanges():
	    logging.debug("*********************** MAC 2")
            try:
        	macObj = macRange.allocateMac()
            except Exception as e:
		logging.debug("******************** MAC ERROR 1 " + str(e))
                continue
            break
	if macObj == None:
	    logging.debug("********************* MAC ERROR 2 " + str(e))
            raise Exception("Could not allocate Mac address for the VM over subscribed ranges")
	logging.debug("*************************** MAC 3")
	return macObj

    def __allocateIpFromSubscribedRanges(self):
	logging.debug("*********************** IP 1")
    	ipObj = None
        #Allocate Ip
        for ipRange in self.getSubscribedIp4Ranges():
	    logging.debug("*********************** IP 2 " + str(ipRange))
            try:
		logging.debug("*********************** IP 3")
    	        ipObj = ipRange.allocateIp()
            except Exception as e:
		logging.debug("*********************** IP ERROR " + str(e))
           	continue
            break
	logging.debug("*********************** IP 4")
     	if ipObj == None:
	    logging.debug("*********************** IP ERROR 2")
            raise Exception("Could not allocate Ip4 address for the VM over subscribed ranges")
	logging.debug("*********************** IP 5")
	return ipObj

    ''' VM interfaces and VM creation methods '''
    def __createEnslavedDataVMNetworkInterface(self,serverInterface):
    	#Obtain
	logging.debug("******************** A1") 
        macObj = self.__allocateMacFromSubscribedRanges()
	logging.debug("******************** A2")
        interface = NetworkInterface.createVMDataInterface(serverInterface.getName()+"-slave",macObj)
        #Enslave it     
	logging.debug("******************* A3")
        serverInterface.attachInterfaceToBridge(interface)
	logging.debug("********************* A4")
        return interface

    def __createEnslavedMgmtVMNetworkInterface(self,serverInterface):
        #Obtain 
	logging.debug("*********************** A1")
        macObj = self.__allocateMacFromSubscribedRanges()
	logging.debug("*********************** A2")
        ipObj = self.__allocateIpFromSubscribedRanges()
	logging.debug("*********************** A3")
        interface = NetworkInterface.createVMMgmtInterface(serverInterface.getName()+"-slave",macObj,ipObj)
        #Enslave it     
	logging.debug("*********************** A4")
        serverInterface.attachInterfaceToBridge(interface)
	logging.debug("*********************** A5")
        return interface

    def createEnslavedVMInterfaces(self):
	self = DB_SESSION.query(VTServer).filter(VTServer.id == self.id).first()
	logging.debug("********************** A")
	vmInterfaces = set()
	logging.debug("********************** B")
        try:
             #Allocate one interface for each Server's interface
	     #Bound self to the session
             for serverInterface in self.networkInterfaces:
	        logging.debug("********************** C " + str(serverInterface))
             	if serverInterface.networkinterface.isMgmt:
		    logging.debug("*********************** D1 - 1")
		    try:
		    	created_interface = self.__createEnslavedMgmtVMNetworkInterface(serverInterface.networkinterface)
			logging.debug("********************* D1 - 2")
		    	vmInterfaces.add(created_interface)
			logging.debug("********************* D1 - 3 " + str(created_interface) + ' ' + str(vmInterfaces))
#                    vmInterfaces.add(self.__createEnslavedMgmtVMNetworkInterface(serverInterface.networkinterface))
		    except Exception as e:
			logging.debug("********************* CREATION FAIL " + str(e))
                else:
		    logging.debug("*********************** D2")
                    vmInterfaces.add(self.__createEnslavedDataVMNetworkInterface(serverInterface.networkinterface))
     	except Exception as e:
	    logging.debug("**************************** VTServer FAIL " + str(e))
            for interface in vmInterfaces:
            	interface.destroy()
            raise e
	logging.debug("*************************** E")
     	return vmInterfaces

    ''' Server interfaces '''
    #Network mgmt bridges
    def setMgmtBridge(self,name,macStr):
    	with MutexStore.getObjectLock(self.getLockIdentifier()):
            nInter = self.networkInterfaces.filter(isMgmt=True,isBridge=True)
            if nInter.count() == 1:
            	mgmt = nInter.get()
                mgmt.setName(name)
                mgmt.setMacStr(macStr)
	    elif nInter.count() == 0:
                mgmt = NetworkInterface.createServerMgmtBridge(name,macStr)
                self.networkInterfaces.add(mgmt)
            else:
                raise Exception("Unexpected length of managment NetworkInterface query")

    #Network data bridges
    def addDataBridge(self,name,macStr,switchId,port):
   	with MutexStore.getObjectLock(self.getLockIdentifier()):
   	    if self.networkInterfaces.filter(name=name, isBridge=True).count()> 0:
             	raise Exception("Another data bridge with the same name already exists in this Server")
	    netInt = NetworkInterface.createServerDataBridge(name,macStr,switchId,port)
            self.networkInterfaces.add(netInt)

    def updateDataBridge(self,interface):
    	with MutexStore.getObjectLock(self.getLockIdentifier()):
            if self.networkInterfaces.filter(id = interface.id).count()!= 1:
            	raise Exception("Can not update bridge interface because it does not exist or id is duplicated")
	    NetworkInterface.updateServerDataBridge(interface.id,interface.getName(),interface.getMacStr(),interface.getSwitchID(),interface.getPort())

    def deleteDataBridge(self,netInt):
    	with MutexStore.getObjectLock(self.getLockIdentifier()):
            if not isinstance(netInt,NetworkInterface):
            	raise Exception("Can only delete Data Bridge that are instances of NetworkInterace")
	    #TODO: delete interfaces from VMs, for the moment forbid
            if netInt.getNumberOfConnections() > 0:
            	raise Exception("Cannot delete a Data bridge from a server if this bridge has VM's interfaces ensalved.")
	    self.networkInterfaces.remove(netInt)
            netInt.destroy()

    def getNetworkInterfaces(self):
    	return self.networkInterfaces.all().order_by('-isMgmt','id')

                                                                                
