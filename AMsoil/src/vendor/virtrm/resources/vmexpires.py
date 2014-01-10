from datetime import datetime, timedelta
from sqlalchemy.dialects.mysql import TINYINT, DOUBLE
from utils.base import db

'''@author: SergioVidiella'''

class VMExpires(db.Model):
    """Expiration time of the Virtual Machine (only GeniV3)."""
    __tablename__ = 'amsoil_vt_manager_virtualmachine_expires'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    #XXX: Should be a ForeignKey, this class should have the vms as an attribute?
    vm_id = db.Column(db.Integer, nullable=False)
    expires = db.Column(db.Date)
    do_save = True
    
    @staticmethod
    def consctructor(vm_id, expiration, save=True):
        self = VMExpires()
        try:
            self.vm_id = vm_id
            self.expires = expiration
            do_save = save
            if save:
                db.session.add(self)
                db.session.commit()
        except Exception as e:
            print e
            raise e
        return self
    
    def auto_save(self):
        if self.do_save:
            db.session.add(self)
            db.session.commit()
    
    '''Getters and Setters'''
    def set_expiration(self, expires):
        # XXX: Expiration validator?
        self.expires = expires
        self.auto_save()
    
    def get_expiration(self):
        return self.expires
    
    #XXX: Very ugly. Should be a relationship between VM and Expiration or a VM attribute
    def set_vm_id(self, vm_id):
        self.vm_id = vm_id
        self.auto_save()
    
    def get_vm_id(self):
        return self.vm_id
