from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.dialects.mysql import TINYINT, BIGINT
from sqlalchemy.orm import validates

from utils import validators
from utils.commonbase import Base, db_session

from resources.macslot import MacSlot
from resources.ip4slot import Ip4Slot
from interfaces.networkinterfaceip4s import NetworkInterfaceIp4s
from interfaces.networkinterfaceconnectedto import NetworkInterfaceConnectedTo

import amsoil.core.log

logging=amsoil.core.log.getLogger('NetworkInterface')


'''@author: SergioVidiella'''


class NetworkInterface(Base):
    """Network interface model."""

    __tablename__ = 'vt_manager_networkinterface'

    '''Generic parameters'''
    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    name = Column(String(128), nullable=False)
    mac_id = Column(Integer, ForeignKey('vt_manager_macslot.id'))
    mac = relationship("MacSlot", backref="networkInterface", uselist=False, lazy="dynamic")
    ip4s = association_proxy("networkinterface_ip4s", "ip4slot")
    isMgmt = Column(TINYINT(1), nullable=False, default=0)
    isBridge = Column(TINYINT(1), nullable=False, default=0)

    '''Interfaces connectivy'''
    vtserver = association_proxy("vtserver_assocation", "vtserver")
    vm = association_proxy("vm_associations", "vm")
    connectedTo = association_proxy("to_networkinterface", "to_networkinterface")
    connectedFrom = association_proxy("from_networkinterface", "from_networkinterface")

    '''Physical connection details for bridged interfaces''' 
    switchID = Column(String(23))
    port = Column(Integer)
    idForm = Column(Integer)

    '''Interface constructor '''
    @staticmethod
    def constructor(name, macStr, macObj, switchID, port, ip4Obj, isMgmt=False, isBridge=False):
	logging.debug("******************************* I1")
	self = NetworkInterface()
	try:
	    logging.debug("******************************* I2 " + name + str(macObj) + ' ' + str(self.mac.all()))
            self.name = name
	    if macObj == None:
		logging.debug("******************************* I3 - 1")
            	self.mac = MacSlot.macFactory(None,macStr)
            else:
		logging.debug("******************************* I3 - 2")
            	if not isinstance(macObj,MacSlot):
		    logging.debug("******************************* I - ERROR - 1")
                    raise Exception("Cannot construct NetworkInterface with a non MacSlot object as parameter")
		logging.debug("******************************* I4 " + str(macObj) + ' ' + str(type(macObj)))
#		self.mac_id = macObj.id
		logging.debug("************************************ YEAH")
#		macObj.networkInterface = [self,]
		logging.debug("************************************ YEAH")
            	self.mac.append(macObj)
		db_session.add(self)
		db_session.commit()
	    logging.debug("******************************* I5 " + str(self.mac.all()) + ' ' + str(self.mac_id))
            self.isMgmt = isMgmt
	    logging.debug("******************************* I6")	    
            '''Connectivity'''
            if isBridge:
		logging.debug("******************************* I7 - 1")
            	self.isBridge = isBridge
                self.switchID = switchID
                self.port = port
	    db_session.add(self)
            db_session.commit()
            logging.debug("******************************* I7 " + str(self.mac))
            if not ip4Obj == None:
		logging.debug("******************************* I7 - 2")
                if not isinstance(ip4Obj,Ip4Slot):
		    logging.debug("******************************* I - ERROR - 2")
                    raise Exception("Cannot construct NetworkInterface with a non Ip4Slot object as parameter")
		else:
		    logging.debug("******************************* I7 - 3")
		    self.ip4s.append(ip4Obj)
		    db_session.add(self)
		    db_session.commit()
		    logging.debug("****************************** I7 - 4 " + str(ip4Obj.id) + ' ' + str(self.id))
	except Exception as e:
	    logging.debug("******************************* I - ERROR - 3")
            raise e
	logging.debug("******************************* I8")
	return self

    def update(self, name, macStr, switchID, port):
    	try:
            self.name = name
            self.setMacStr(macStr)
            self.switchID = switchID
            self.port = port
        except Exception as e:
            raise e

    ##Public methods
    def getLockIdentifier(self):
    	#Uniquely identifies object by a key
        return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)

    def getName(self):
        return self.name

    def setName(self,name):
        self.name=name

    def getMacStr(self):
        return self.mac.mac

    def setMacStr(self,macStr):
        self.mac.setMac(macStr)

    def setPort(self,port):
        self.port = port

    def getPort(self):
        return self.port

    def setSwitchID(self, switchID):
        self.switchID = switchID

    def getSwitchID(self):
        return self.switchID

    def getNumberOfConnections(self):
        return self.connectedTo.all().count()

    def attachInterfaceToBridge(self,interface):
	logging.debug("*********************************** BRIDGE 1")
        if not self.isBridge:
	    logging.debug("*********************************** BRIDGE ERROR - 1")
            raise Exception("Cannot attach interface to a non-bridged interface")
        if not isinstance(interface,NetworkInterface):
	    logging.debug("*********************************** BRIDGE ERROR - 2")
            raise Exception("Cannot attach interface; object type unknown -> Must be NetworkInterface instance")
	logging.debug("*********************************** BRIDGE 2 " + str(interface.id) + ' ' + str(self.id))
	self.connectedTo.append(interface)
	db_session.add(self)
	db_session.commit()
	logging.debug("*********************************** BRIDGE 3 " + str(interface.connectedFrom))


    def detachInterfaceToBridge(self,interface):
  	if not self.isBridge:
            raise Exception("Cannot detach interface from a non-bridged interface")
        if not isinstance(interface,NetworkInterface):
            raise Exception("Cannot detach interface; object type unknown -> Must be NetworkInterface instance")
        self.connectedTo.remove(interface)

    def addIp4ToInterface(self,ip4):
        if not self.isMgmt:
            raise Exception("Cannot add IP4 to a non mgmt interface")
        if not isinstance(ip4,Ip4Slot):
            raise Exception("Cannot add IP4 to interface; object type unknown -> Must be IP4Slot instance")
        self.ip4s.add(ip4)

    def removeIp4FromInterface(self,ip4):
        if not isinstance(ip4,Ip4Slot):
            raise Exception("Cannot remove IP4 to interface; object type unknown -> Must be IP4Slot instance")
        if not self.isMgmt:
            raise Exception("Cannot add IP4 to a non mgmt interface")
        self.ip4s.remove(ip4)

    def destroy(self):
        with MutexStore.getObjectLock(self.getLockIdentifier()):
            if self.getNumberOfConnections():
           	raise Exception("Cannot destroy a bridge which has enslaved interfaces")
            for ip in self.ip4s.all():
            	ip.destroy()
                self.mac.destroy()
                self.delete()


    '''Validators'''
    @validates('name')
    def validate_name(self, key, name):
        try:
	    #XXX: Fails when a name like eth1.999-slave is set, solve this
	    #validators.resource_name_validator(name)
	    return name
	except Exception as e:
            raise e

    @validates('switchID')
    def validate_switchID(self, key, switchID):
	try:
	    validators.datapath_validator(switchID)
	    return switchID
	except Exception as e:
	    raise e

    @validates('port')
    def validate_port(self, key, port):
	try:
	    validators.number_validator(port)
	    return port
	except Exception as e:
	    raise e
    
    '''Server interface factories'''
    @staticmethod
    def createServerDataBridge(name, macStr, switchID, port):
        return NetworkInterface.constructor(name, macStr, None, switchID, port, None, False, True)

    @staticmethod
    def updateServerDataBridge(name, macStr, switchID, port):
        return NetworkInterface.update(name, macStr, switchID, port)

    @staticmethod
    def createServerMgmtBridge(name, macStr):
        return NetworkInterface.constructor(name, macStr, None, None, None, None, True, True)

    '''VM interface factories'''
    @staticmethod
    def create_vm_data_interface(name, macObj):
        return NetworkInterface.constructor(name, None, macObj, None, None, None, False, False)

    @staticmethod
    def create_vm_management_interface(name, macObj, ip4):
        return NetworkInterface.constructor(name, None, macObj, None, None, ip4, True, False)
    
