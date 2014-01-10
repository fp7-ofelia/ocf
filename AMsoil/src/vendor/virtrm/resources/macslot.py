from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import validates
from utils.base import db
from utils.ethernetutils import EthernetUtils
import inspect

'''@author: SergioVidiella'''

class MacSlot(db.Model):
    """MacSlot Class."""

    __tablename__ = 'vt_manager_macslot'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    mac = db.Column(db.String(17), nullable=False)
    mac_range_id = db.Column("macRange_id", db.Integer, db.ForeignKey('vt_manager_macrange.id'))
    mac_range = db.relationship("MacRange", backref="macslot", lazy="dynamic")
    is_excluded = db.Column("isExcluded", TINYINT(1))
    comment = db.Column(db.String(1024))
    
    '''Defines soft or hard state of the interface'''
    do_save = True
    
    # Private methods
    def auto_save(self):
        if self.do_save:
            db.session.add(self)
            db.session.commit()
    
    def get_lock_identifier(self):
        # Uniquely identifies object by a key
        return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)
    
    @staticmethod
    def constructor(mac_range, mac, excluded, comment="", save=True):
        self = MacSlot()
        # Check MAC
        if not mac == "":
            EthernetUtils.check_valid_mac(mac)
        self.mac = mac
        self.is_excluded = excluded
        self.mac_range = mac_range
        self.comment = comment
        self.do_save = save
        if save:
            db.session.add(self)
            db.session.commit()
        return self
    
    def destroy(self):
        if self.mac_range != None:
            if self.is_excluded:
                self.mac_range.remove_excluded_mac(self)
            else:
                self.mac_range.release_mac(self)
        db.session.delete(self)
        db.session.commit()
    
    def get_associated_vm(self):
        return self.interface.vm.name
    
    def get_mac(self):
       return self.mac
    
    def is_excluded_mac(self):
        return self.is_excluded
    
    def set_mac(self, mac)
        self.mac = mac
        self.auto_save()
    
    '''Validators'''
    @validates('mac')
    def validate_mac(self, key, mac):
        try:
            EthernetUtils.check_valid_mac(mac)
            return mac
        except Exception as e:
            raise e
    
    ''' Factories '''
    @staticmethod
    def mac_factory(mac_range, mac, save=True):
        return MacSlot.constructor(mac_range, mac, False, "", save)
    
    @staticmethod
    def excluded_mac_factory(macRange, mac, comment, save=True):
        return MacSlot.constructor(mac_range, mac, True, comment, save)

