from models.resources.virtualmachine import VirtualMachine
from models.resources.vmallocated import VMAllocated
from datetime import datetime
from sqlalchemy.ext.associationproxy import association_proxy
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
    expiration = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    do_save = True
    # Resource relationships
    virtualmachine = association_proxy('expiration_vm', 'vm', creator=lambda vm:VMExpiration(vm=vm))
    virtualmachine_allocated = association_proxy('expiration_vm_allocated', 'vm_allocated', creator=lambda vm:VMAllocatedExpiration(vm_allocated=vm))

    @staticmethod    
    def __init__(self,expiration=None,save=False):
        self.expiration = expiration
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
            vm = self.virtualmachine[0]
        try:
            self.virtualmachine.remove(vm)
        except:
            raise Exception
        self.auto_save()

    def remove_virtualmachine_allocated(self, vm=None):
        if not vm:
            vm = self.virtualmachine_allocated[0]
        try:
            self.virtualmachine.remove(vm)
        except:
            raise Exception
        self.auto_save()

    '''Getters and Setters'''
    def set_expiration(self, expiration):
        self.expiration = expiration
        self.auto_save()
    
    def get_expiration(self):
        return self.expiration

    def set_do_save(self, save):
        self.do_save = save
    
    def get_do_save(self):
        return self.do_save

    def set_virtualmachine(self, vm):
        self.virtualmachine.append(vm)
        self.auto_save()

    def get_virtualmachine(self):
        # Try to avoid an out of index Exception if the list is empty
        try:
            virtualmachine = self.virtualmachine[0]
        except:
            virtualmachine = None
        return virtualmachine

    def set_virtualmachine_allocated(self, vm):
        self.virtualmachine_allocated.append(vm)
        self.auto_save()

    def get_virtualmachine_allocated(self):
        # Try to avoid an out of index Exception if the list is empty
        try:
            virtualmachine_allocated = self.virtualmachine_allocated 
        except:
            virtualmachine_allocated = None
        return virtualmachine_allocated

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
    # Defines hard or soft status of the table
    do_save = False
    # Relationships
    vm = db.relationship("VirtualMachine")
    vm_expiration = db.relationship("Expiration", primaryjoin="Expiration.id==VMExpiration.expiration_id", backref=db.backref("expiration_vm", cascade = "all, delete-orphan"))

    def get_expiration(self):
        return self.vm_expiration
 
    def destroy(self):
        db.session.delete(self)
        db.session.commit()

class VMAllocatedExpiration(db.Model):
    """Relation between Allocated VirtualMachines and their expiration time (only GENIv3)"""
    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'virtualmachine_allocated_expiration'
    __table_args__ = {'extend_existing':True}
    # Table attributes
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vm_uuid = db.Column(db.ForeignKey(table_prefix + 'virtualmachine_allocated.uuid'), nullable=False)
    expiration_id = db.Column(db.ForeignKey(table_prefix + 'expiration.id'), nullable=False)
    # Relationships
    vm_allocated = db.relationship("VMAllocated", primaryjoin="VMAllocated.uuid==VMAllocatedExpiration.vm_uuid")
    vm_allocated_expiration = db.relationship("Expiration", primaryjoin="Expiration.id==VMAllocatedExpiration.expiration_id", backref=db.backref("expiration_vm_allocated", cascade="all, delete-orphan"))

    def get_expiration(self):
        return self.vm_allocated_expiration
   
    def destroy(self)
        db.session.delete(self)
        db.session.commit()
