from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import validates

import logging
import uuid

from utils.commonbase import Base
from utils import settings
from utils.choices import PossibleStatusClass, PossibleTypeClass


'''@author: SergioVidiella'''


class Action(Base):
    """Class to store actions"""

    __tablename__ = 'vt_manager_action'

    '''General parameters'''
    id = Column(Integer, autoincrement=True, primary_key=True)
    type = Column(String(16), nullable=False, default="")
    uuid = Column(String(512), nullable=False, default="")
    callBackUrl = Column(String(200), nullable=False)
    status = Column(String(16), nullable=False default="")
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
    	if Action.objects.filter (uuid = self.uuid).count() != 0:
            logging.error("Action with the same uuid already exists")
            raise Exception("Action with the same uuid already exists")

    '''Validators'''
    @validates('type')
    def validate_type(self, key, type):
        try:
            PossibleTypesClass.validate_type(type)
            return type
        except Exception as e:
            raise e

    @validates('status')
    def validate_status(self, key, status):
	try:
	    PossibleStatusClass.validate_status(status)
	    return status
	except Exception as e:
	    raise e

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
	try:
	    PossibleStatusClass.validate_status(status)
	    self.status = status
	except Exception as e:
	    raise e

    def getStatus(self):
        return self.status

    def setType(self, type):
	try:
	    PossibleTypesClass.validate_type(type)
	    self.type = type
	except Exception as e:
	    raise e

    def getType(self):
        return self.type

    def isProvisioningType(self):
        return self.type in settings.PROVISIONING_TYPES
 
    def isMonitoringType(self):
        return self.type in settings.MONITORING_TYPES

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

