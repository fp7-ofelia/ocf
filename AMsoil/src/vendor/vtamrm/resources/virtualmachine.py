from sqlalchemy import Column, Integer, String, desc
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.orm import validates, relationship, backref

import inspect

from utils.commonbase import Base, DB_SESSION
from utils import validators
from utils.choices import VirtTechClass, OSDistClass, OSVersionClass, OSTypeClass

from interfaces.networkinterface import NetworkInterface
from interfaces.vmnetworkinterfaces import VMNetworkInterfaces

#from resources.xenvm import XenVM


'''@author: SergioVidiella'''


class VirtualMachine(Base):
    """VirtualMachine Class."""

    __tablename__ = 'vt_manager_virtualmachine'

    __childClasses = (
    	'XenVM',
    )

 #   xenvm = relationship("XenVM", backref="vm")

    ''' General parameters '''
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(512), nullable=False, default="")
    uuid = Column(String(1024), nullable=False, default="")
    memory = Column(Integer)
    numberOfCPUs = Column(Integer)
    discSpaceGB = Column(DOUBLE)

    '''Property parameters'''
    projectId = Column(String(1024), nullable=False, default="")
    projectName = Column(String(1024), nullable=False, default="")
    sliceId = Column(String(1024), nullable=False, default="")
    sliceName = Column(String(1024), nullable=False, default="")
    guiUserName = Column(String(1024), nullable=False, default="")
    guiUserUUID = Column(String(1024), nullable=False, default="")
    expedientId = Column(Integer)

    '''OS parameters'''
    operatingSystemType = Column(String(512), nullable=False, default="")
    operatingSystemVersion = Column(String(512), nullable=False, default="")
    operatingSystemDistribution = Column(String(512), nullable=False, default="")

    '''Networking'''
    networkInterfaces = relationship("VMNetworkInterfaces")

    '''Other'''
    callBackURL = Column(String(200))
    state = Column(String(24))

    '''Possible states'''
    RUNNING_STATE = 'running'
    CREATED_STATE = 'created (stopped)'
    STOPPED_STATE = 'stopped'
    UNKNOWN_STATE = 'unknown'
    FAILED_STATE = 'failed'
    ONQUEUE_STATE = 'on queue'
    STARTING_STATE = 'starting...'
    STOPPING_STATE = 'stopping...'
    CREATING_STATE = 'creating...'
    DELETING_STATE = 'deleting...'
    REBOOTING_STATE = 'rebooting...'

    __possibleStates = (RUNNING_STATE,CREATED_STATE,STOPPED_STATE,UNKNOWN_STATE,FAILED_STATE,ONQUEUE_STATE,STARTING_STATE,STOPPING_STATE,CREATING_STATE,DELETING_STATE,REBOOTING_STATE)

    ''' Mutex over the instance '''
    mutex = None

    '''Validators'''
    @validates('name')
    def validate_name(self, key, name):
    	try:
            validators.vm_name_validator(name)
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

    ''' Getters and setters'''
    def getLockIdentifier(self):
  	#Uniquely identifies object by a key
        return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)

    def getChildObject(self):
    	for childClass in self.__childClasses:
            try:
            	return self.__getattribute__(childClass.lower())
            except eval(childClass).DoesNotExist:
            	return self

    def setName(self, name):
    	try:
       	     validators.vm_name_validator(name)
             self.name = name
        except Exception as e:
             raise e
        
    def getName(self):
        return self.name

    def setUUID(self, uuid):
        self.uuid = uuid
        
    def getUUID(self):
        return self.uuid

    def setProjectId(self,projectId):
    	if not isinstance(projectId,str):
            projectId = str(projectId)
        self.projectId = projectId
        
    def getProjectId(self):
        return self.projectId

    def setProjectName(self,projectName):
        if not isinstance(projectName,str):
            projectName = str(projectName)
        self.projectName = projectName
        
    def getProjectName(self):
        return self.projectName

    def setSliceId(self, value):
        self.sliceId = value
        
    def getSliceId(self):
        return self.sliceId

    def setSliceName(self, value):
        self.sliceName = value

    def getSliceName(self):
        return self.sliceName

    def setUIId(self,expedientId):
        if not isinstance(expedientId,int):
            expedientId = int(expedientId)
        self.expedientId = expedientId
        
    def getUIId(self):
        return self.expedientId

    def setState(self,state):
        if state not in self.__possibleStates:
            raise KeyError, "Unknown state"
        else:
            self.state = state
        
    def getState(self):
        return self.state

    def setMemory(self,memory):
                self.memory = memory

    def getMemory(self):
        return self.memory

    def setNumberOfCPUs(self,num):
        self.numberOfCPUs=num
        
    def getNumberOfCPUs(self):
        return self.numberOfCPUs

    def setDiscSpaceGB(self,num):
        self.discSpaceGB=num
        
    def getDiscSpaceGB(self):
        return self.discSpaceGB

    def setOSType(self, type):
        OSTypeClass.validateOSType(type)
        self.operatingSystemType = type
        
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

    def setCallBackURL(self, url):
        self.callBackURL = url
        
    def getCallBackURL(self):
        return self.callBackURL

    def getNetworkInterfaces(self):
	return DB_SESSION.query(NetworkInterface).join(NetworkInterface.vm_associations, aliased=True).filter(VMNetworkInterfaces.virtualmachine_id == self.id).order_by(NetworkInterface.isMgmt.desc(), NetworkInterface.id).all()


