from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import validates, relationship, backref

import inspect

from utils.commonbase import Base, db_session
from utils.ethernetutils import EthernetUtils

'''@author: SergioVidiella'''

class MacSlot(Base):
    """MacSlot Class."""

    __tablename__ = 'vt_manager_macslot'

    id = Column(Integer, autoincrement=True, primary_key=True)
    mac = Column(String(17), nullable=False)
    macRange_id = Column(Integer, ForeignKey('vt_manager_macrange.id'))
    macRange = relationship("MacRange", backref="macslot")
    networkInterface = relationship("NetworkInterface", backref="mac", lazy='joined')
    isExcluded = Column(TINYINT(1))
    comment = Column(String(1024))

    @staticmethod
    def constructor(macRange, mac, excluded, comment=""):
    	self = MacSlot()

	#Check MAC
        if not mac == "":
            EthernetUtils.checkValidMac(mac)

        self.mac = mac
        self.isExcluded = excluded
        self.macRange = macRange
        self.comment = comment
	db_session.add(self)
	db_session.commit()

        return self

    '''Getters'''
    def getLockIdentifier(self):
    	#Uniquely identifies object by a key
        return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)

    def getAssociatedVM(self):
    	return self.interface.vm.name

    '''Validators'''
    @validates('mac')
    def validate_mac(self, key, mac):
        try:
            EthernetUtils.checkValidMac(mac)
            return mac
        except Exception as e:
            raise e

    ''' Factories '''
    @staticmethod
    def macFactory(macRange, mac):
        return MacSlot.constructor(macRange, mac, False, "")

    @staticmethod
    def excludedMacFactory(macRange, mac, comment):
        return MacSlot.constructor(macRange, mac, True, comment)

