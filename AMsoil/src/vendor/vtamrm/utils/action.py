from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import validates

import uuid
import logging 

from utils.commonbase import Base, db_session
import amsoil.core.log
logging=amsoil.core.log.getLogger('Action')


'''@author: SergioVidiella'''


class Action(Base):
    """Class to store actions"""

    __tablename__ = 'vt_manager_action'

    '''Action status Types'''
    QUEUED_STATUS = "QUEUED"
    ONGOING_STATUS= "ONGOING"
    SUCCESS_STATUS  = "SUCCESS"
    FAILED_STATUS   = "FAILED"

    __possibleStatus = (QUEUED_STATUS, ONGOING_STATUS, SUCCESS_STATUS, FAILED_STATUS)

    '''Action type Types'''
    ##Monitoring
    #Servers
    MONITORING_SERVER_VMS_TYPE="listActiveVMs"

    __monitoringTypes = (
    	#Server
    	MONITORING_SERVER_VMS_TYPE,
    )

    #VMs
    ##Provisioning 
    #VM provisioning actions        
    PROVISIONING_VM_CREATE_TYPE = "create"
    PROVISIONING_VM_START_TYPE = "start"
    PROVISIONING_VM_DELETE_TYPE = "delete"
    PROVISIONING_VM_STOP_TYPE = "hardStop"
    PROVISIONING_VM_REBOOT_TYPE = "reboot"

    __provisioningTypes = (
    	#VM
        PROVISIONING_VM_CREATE_TYPE,
        PROVISIONING_VM_START_TYPE,
        PROVISIONING_VM_DELETE_TYPE,
        PROVISIONING_VM_STOP_TYPE,
        PROVISIONING_VM_REBOOT_TYPE,
    )

    '''All possible types '''
    __possibleTypes = (
    	#Monitoring
        #Server
        MONITORING_SERVER_VMS_TYPE,

        ##Provisioning
        #VM
        PROVISIONING_VM_CREATE_TYPE,
        PROVISIONING_VM_START_TYPE,
        PROVISIONING_VM_DELETE_TYPE,
        PROVISIONING_VM_STOP_TYPE,
        PROVISIONING_VM_REBOOT_TYPE,
    )

    '''General parameters'''
    id = Column(Integer, autoincrement=True, primary_key=True)
    type = Column(String(16), nullable=False, default="")
    uuid = Column(String(512), nullable=False, default="")
    callBackUrl = Column(String(200), nullable=False)
    status = Column(String(16), nullable=False, default="")
    description = Column(String(2048), default="")
    objectUUID = Column(String(512), default="")

    '''Public methods'''
    @staticmethod
    def constructor(aType,status,objectUUID=None,description=""):
    	self = Action()
        self.setType(aType)
        self.setStatus(status)
        self.setUUID(uuid.uuid4())
        if not objectUUID == None:
            self.setObjectUUID(objectUUID)
        if not description == "":
            self.setDescription(description)
        return self

    def destroy(self):
        self.delete()

    def checkActionIsPresentAndUnique(self):
    	if len(db_session.query(Action).filter(Action.uuid == self.uuid).all()) != 0:
	    db_session.expunge_all()
            logging.error("Action with the same uuid already exists")
            raise Exception("Action with the same uuid already exists")
	db_session.expunge_all()

    '''Validators'''
    @validates('type')
    def validate_type(self, key, type):
        if type not in self.__possibleTypes:
            raise Exception("Action type not valid")
        return type


    @validates('status')
    def validate_status(self, key, status):
    	if status not in self.__possibleStatus:
            raise Exception("Status not valid")
        return status

    '''Getters and setters'''
    @staticmethod
    def getAndCheckActionByUUID(uuid):
    	actions = Action.objects.filter (uuid = uuid)
        if actions.count() ==  1:
            return actions[0]
        elif actions.count() == 0:
            logging.error("Action with uuid %s does not exist" % uuid)
            raise Exception("Action with uuid %s does not exist" % uuid)
        elif actions.count() > 1:
            logging.error("Action with uuid %s does not exist" % uuid)
            raise Exception("More than one Action with uuid %s" % uuid)

    def setStatus(self, status):
    	if status not in self.__possibleStatus:
            raise Exception("Status not valid")
        self.status = status

    def getStatus(self):
        return self.status

    def setType(self, type):
    	if type not in self.__possibleTypes:
            raise Exception("Action type not valid")
        self.type = type

    def getType(self):
        return self.type

    def isProvisioningType(self):
	return self.type in self.__provisioningTypes
 
    def isMonitoringType(self):
	return self.type in self.__monitoringTypes

    def setDescription(self, description):
        self.description = description

    def getDescription(self):
        return self.descripion

    def setUUID(self, uuid):
        self.uuid = uuid

    def getUUID(self):
        return self.uuid

    def setCallBackUrl(self, url):
        self.uuid = url

    def getCallBackUrl(self):
        return self.url

    def setObjectUUID(self, objUUID):
        self.objectUUID = objUUID
        
    def getObjectUUID(self):
        return self.objectUUID

