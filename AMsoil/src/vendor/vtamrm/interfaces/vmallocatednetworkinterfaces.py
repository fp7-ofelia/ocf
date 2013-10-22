from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import validates

from utils import validators
from utils.commonbase import Base



'''@author: SergioVidiella'''


class VMAllocatedNetworkInterfaces(Base):
    """NetworkInterfaces params for allocated VMs."""

    __tablename__ = 'vt_manager_virtualmachine_allocated_networkInterfaces'

    '''Generic parameters'''
    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    allocated_vm_id = Column(Integer, ForeignKey('vt_manager_virtualmachine_allocated.id'))
    name = Column(String(128), nullable=False)
    isMgmt = Column(TINYINT(1), nullable=False)
    gw = Column(String(15))
    ip = Column(String(15))
    mac = Column(String(17))
    dns1 = Column(String(15))
    dns2 = Column(String(15))
    mask = Column(String(15))

    vm = relationship('VMAllocated', backref= backref('interfaces', lazy='dynamic', cascade="all,delete"))

    '''Interface constructor '''
    @staticmethod
    def constructor(name, macStr, macObj, switchID, port, ip4Obj, isMgmt=False, isBridge=False):
	self = NetworkInterface()
	try:
            self.name = name
	    if macObj == None:
            	self.mac = MacSlot.macFactory(None,macStr)
            else:
            	if not isinstance(macObj,MacSlot):
                    raise Exception("Cannot construct NetworkInterface with a non MacSlot object as parameter")
            	self.mac = macObj
            self.isMgmt = isMgmt
            '''Connectivity'''
            if isBridge:
            	self.isBridge = isBridge
                self.switchID = switchID
                self.port = port
            if not ip4Obj == None:
                if not isinstance(ip4Obj,Ip4Slot):
                    raise Exception("Cannot construct NetworkInterface with a non Ip4Slot object as parameter")
		else:
                    self.ip4s.append(ip4Obj)
	except Exception as e:
            raise e
	return self

    '''Validators'''
    @validates('name')
    def validate_name(self, key, name):
        try:
	    validators.resource_name_validator(name)
	    return name
	except Exception as e:
            raise e

    @validates('mac')
    def validate_mac(self, key, mac):
	try:
	    validators.mac_validator(mac)
	    return mac
	except Exception as e:
	    raise e
