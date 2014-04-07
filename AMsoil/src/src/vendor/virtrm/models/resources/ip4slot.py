from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from utils.base import db
from utils.ip4utils import IP4Utils
import amsoil.core.pluginmanager as pm
import inspect

'''@author: msune, SergioVidiella'''

class Ip4Slot(db.Model):
    """Ip4Slot Class."""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'ip4slot'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    ip = db.Column(db.String(15), nullable=False)
    ip_range_id = db.Column("ipRange_id", db.Integer, db.ForeignKey(table_prefix + 'ip4range.id'), nullable=False)
    ip_range = association_proxy("ip4_ip4range", "ip4range")
    is_excluded = db.Column("isExcluded", TINYINT(1))
    comment = db.Column(db.String(1024))

    '''Defines soft or hard state of the interface'''
    do_save = True   
    
    @staticmethod
    def constructor(ip_range_id, ip, excluded, comment="", save=True):
        self = Ip4Slot()
        try:
            # Check IP
            IP4Utils.check_valid_ip(ip)
            self.ip = ip
            self.is_excluded = excluded
            self.ip_range_id = ip_range_id
            self.comment = comment
            self.do_save = save
            if save:
                db.session.add(self)
                db.session.commit()
        except Exception as e:
            raise e
        return self
    
    '''Getters'''
    def is_excluded_ip(self):
        return self.is_excluded

    def get_lock_identifier(self):
        # Uniquely identifies object by a key
        return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)
    
    def get_ip(self):
        return self.ip
     
    def get_netmask(self):
        return self.ip_range.get_netmask()
        
    def get_gateway_ip(self):
        return self.ip_range.get_gateway_ip()
    
    def get_dns1(self):
        return self.ip_range.get_dns1()
        
    def get_dns2(self):
        return self.ip_range.get_dns2()

    '''Destructor'''
    def destroy(self):
        if self.ip_range:
            if self.is_excluded_ip():
                self.ip_range[0].remove_excluded_ip(self)
            else:self.ip_range[0].release_ip(self)
        db.session.delete(self)
        db.session.commit()

    '''Validators'''
    @validates('ip')
    def validate_ip(self, key, ip):
        try:
            IP4Utils.check_valid_ip(ip)
            return ip
        except Exception as e:
            raise e
    
    ''' Factories '''
    @staticmethod
    def ip_factory(ip_range, ip, save=True):
        return Ip4Slot.constructor(ip_range, ip, False, "", save)
    
    @staticmethod
    def excluded_ip_factory(ip_range_id, ip, comment, save=True):
        return Ip4Slot.constructor(ip_range_id, ip, True, comment, save)
