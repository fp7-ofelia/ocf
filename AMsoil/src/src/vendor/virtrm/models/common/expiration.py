from models.resources.virtualmachine import VirtualMachine
from models.resources.vmallocated import VMAllocated
from datetime import datetime
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection
from utils.base import db
import amsoil.core.log
import amsoil.core.pluginmanager as pm

logging=amsoil.core.log.getLogger('Expiration')

'''@author: SergioVidiella'''

class Expiration(db.Model):
    """Expiration time of the Virtual Machine (only GENI)."""

    config = pm.getService("config")
    __tablename__ = config.get("virtrm.DATABASE_PREFIX") + 'expiration'
    __table_args__ = {'extend_existing':True}
    # Table attributes
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    end_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    do_save = True
    # Resource relationships
    vm = association_proxy('expiration_vm', 'vm', creator=lambda vm:VMExpiration(vm=vm))

    @staticmethod    
    def __init__(self,start_time=None,end_time=None,save=False):
        self.start_time = start_time
        self.end_time = end_time
        do_save = save
        if save:
            db.session.add(self)
            db.session.commit()
    
    def destroy(self):
        db.session.delete(self)
        db.session.commit()
     
    def auto_save(self):
        if self.do_save:
            db.session.add(self)
            db.session.commit()

    def remove_virtualmachine(self, vm=None):
        if not vm:
            vm = self.vm[0]
        try:
            self.virtualmachine.remove(vm)
        except:
            raise Exception
        self.auto_save()

    '''Getters and Setters'''
    def set_start_time(self, start_time):
        self.start_time = start_time
        self.auto_save()
    
    def get_start_time(self):
        return self.start_time

    def set_end_time(self, end_time):
        self.end_time = end_time
        self.auto_save()
 
    def get_end_time(self):
        return self.end_time

    def set_do_save(self, save):
        self.do_save = save
    
    def get_do_save(self):
        return self.do_save

    def set_vm(self, vm):
        self.vm.append(vm)
        self.auto_save()

    def get_vm(self):
        # Try to avoid an out of index Exception if the list is empty
        try:
            virtualmachine = self.vm[0]
        except:
            virtualmachine = None
        return virtualmachine

class VMExpiration(db.Model):
    """Relation between VirtualMachines and their expiration time (only GENI)"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'virtualmachine_expiration'
    __table_args__ = {'extend_existing':True}
    # Table attributes
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vm_uuid = db.Column(db.ForeignKey(table_prefix + 'virtualmachine.uuid'), nullable=False)
    expiration_id = db.Column(db.ForeignKey(table_prefix + 'expiration.id'), nullable=False)
    # Relationships
    vm = db.relationship("VirtualMachine")
    vm_expiration = db.relationship("Expiration", backref=db.backref("expiration_vm", cascade = "all, delete-orphan"))

    def get_expiration(self):
        return self.vm_expiration
 
    def destroy(self):
        db.session.delete(self)
        db.session.commit()
