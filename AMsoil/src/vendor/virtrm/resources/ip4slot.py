from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import validates
from utils.base import db
from utils.ip4utils import IP4Utils
import amsoil.core.pluginmanager as pm
import inspect

'''@author: SergioVidiella'''

class Ip4Slot(db.Model):
    """Ip4Slot Class."""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'ip4slot'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    ip = db.Column(db.String(15), nullable=False)
    ip_range_id = db.Column("ipRange_id", db.Integer, db.ForeignKey(table_prefix + 'ip4range.id'), nullable=False)
    ip_range = db.relationship('Ip4Range')
    is_excluded = db.Column("isExcluded", TINYINT(1))
    comment = db.Column(db.String(1024))

    '''Defines soft or hard state of the interface'''
    do_save = True   
    
    @staticmethod
    def constructor(ip_range, ip, excluded, comment="", save=True):
        self = Ip4Slot()
        try:
            # Check IP
            IP4Utils.check_valid_ip(ip)
            self.ip = ip
            self.is_excluded = excluded
            self.ip_range = ip_range
            self.comment = comment
            self.do_save = save
            if save:
                db.session.add(self)
                db.session.commit()
        except Exception as e:
            raise e
        return self
    
    '''Getters'''
    def isExcludedIp(self):
        return self.isExcluded

    def get_lock_identifier(self):
        # Uniquely identifies object by a key
        return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)
    
    def getIp(self):
        return self.ip
     
    def getNetmask(self):
        return self.ipRange.getNetmask()
        
    def getGatewayIp(self):
        return self.ipRange.getGatewayIp()
    
    def getDNS1(self):
        return self.ipRange.getDNS1()
        
    def getDNS2(self):
        return self.ipRange.getDNS2()

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
    def ipFactory(ipRange, ip, save=True):
        return Ip4Slot.constructor(ipRange, ip, False, "", save)
    
    @staticmethod
    def excludedIpFactory(ipRange, ip, comment, save=True):
        return MacSlot.constructor(ipRange, ip, True, comment, save)
