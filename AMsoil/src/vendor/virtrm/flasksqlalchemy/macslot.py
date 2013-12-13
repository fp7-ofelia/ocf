from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import validates

import inspect

from utils.ethernetutils import EthernetUtils
from base import db

'''@author: SergioVidiella'''

class MacSlot(db.Model):
    """MacSlot Class."""

    __tablename__ = 'vt_manager_macslot'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    mac = db.Column(db.String(17), nullable=False)
    macRange_id = db.Column(db.Integer, db.ForeignKey('vt_manager_macrange.id'))
    macRange = db.relationship("MacRange", backref="macslot", lazy="dynamic")
    isExcluded = db.Column(TINYINT(1))
    comment = db.Column(db.String(1024))

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

