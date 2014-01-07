from sqlalchemy import desc
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

import inspect

from base import db
from utils import validators
from utils.choices import VirtTechClass, OSDistClass, OSVersionClass, OSTypeClass

from interfaces.networkinterface import NetworkInterface
from interfaces.vmnetworkinterfaces import VMNetworkInterfaces

#from resources.xenvm import XenVM


'''@author: SergioVidiella'''


class VirtualMachine(db.Model):
    """VirtualMachine Class."""

    __tablename__ = 'vt_manager_virtualmachine'

    __child_classes = (
    	'XenVM',
    )

    ''' General parameters '''
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(512), nullable=False, default="")
    uuid = db.Column(db.String(1024), nullable=False, default="")
    memory = db.Column(db.Integer)
    number_of_cpus = db.Column("numberOfCPUs", db.Integer)
    disc_space_gb = db.Column("discSpaceGB", DOUBLE)

    '''Property parameters'''
    project_id = db.Column("projectId", db.String(1024), nullable=False, default="")
    project_name = db.Column("projectName", db.String(1024), nullable=False, default="")
    slice_id = db.Column("sliceId", db.String(1024), nullable=False, default="")
    slice_name = db.Column("sliceName", db.String(1024), nullable=False, default="")
    gui_user_name = db.Column("guiUserName", db.String(1024), nullable=False, default="")
    gui_user_uuid = db.Column("guiUserUUID", db.String(1024), nullable=False, default="")
    expedient_id = db.Column("expedientId", db.Integer)

    '''OS parameters'''
    operating_system_type = db.Column("operatingSystemType", db.String(512), nullable=False, default="")
    operating_system_version = db.Column("operatingSystemVersion", db.String(512), nullable=False, default="")
    operating_system_distribution = Column("operatingSystemDistribution", db.String(512), nullable=False, default="")

    '''Networking'''
    network_interfaces = association_proxy("vm_networkinterfaces", "networkinterface")

    '''Other'''
    callback_url = db.Column("callBackURL", db.String(200))
    state = db.Column(db.String(24))

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

    __possible_states = (RUNNING_STATE,CREATED_STATE,STOPPED_STATE,UNKNOWN_STATE,FAILED_STATE,ONQUEUE_STATE,STARTING_STATE,STOPPING_STATE,CREATING_STATE,DELETING_STATE,REBOOTING_STATE)

    ''' Mutex over the instance '''
    mutex = None

    '''Defines soft or hard state of the VM'''
    do_save = True


    '''Validators'''
    @validates('name')
    def validate_name(self, key, name):
    	try:
            validators.vm_name_validator(name)
            return name
        except Exception as e:
            raise e

    @validates('operating_system_type')
    def validate_operatingsystemtype(self, key, os_type):
        try:
            OSTypeClass.validate_os_type(os_type)
            return os_type
        except Exception as e:
            raise e

    @validates('operating_system_distribution')
    def validate_operatingsystemdistribution(self, key, os_distribution):
        try:
            OSDistClass.validate_os_dist(os_distribution)
            return os_distribution
        except Exception as e:
            raise e

    @validates('operating_system_version')
    def validate_operatingsystemversion(self, key, os_version):
        try:
            OSVersionClass.validate_os_version(os_version)
            return os_version
        except Exception as e:
            raise e

    def auto_save(self):
   	if self.do_save:
       	    db.session.add(self)
	    db.session.commit()
    
    # Public methods
    def get_child_object(self):
    	for child_class in self.__child_classes:
            try:
            	return self.__getattribute__(child_class.lower())
            except eval(child_class).DoesNotExist:
        	return self
    
    def get_lock_identifier(self):
  	#Uniquely identifies object by a key
        return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)


    def setName(self, name):
    	try:
       	     validators.vm_name_validator(name)
             self.name = name
	     self.auto_save()
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
	return db_session.query(NetworkInterface).join(NetworkInterface.vm_associations, aliased=True).filter(VMNetworkInterfaces.virtualmachine_id == self.id).order_by(NetworkInterface.isMgmt.desc(), NetworkInterface.id).all()


