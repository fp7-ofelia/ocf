from models.common.expiration import Expiration
from models.resources.virtualmachine import VirtualMachine
from models.resources.vmallocated import VMAllocated
from utils.base import db
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

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
    vm = db.relationship("VirtualMachine", lazy="dynamic")
    vm_expiration = db.relationship("Expiration", primaryjoin="Expiration.id==VMExpiration.expiration_id", backref="expiration_vm", lazy="dynamic")
    
    def __init__(self, vm_uuid=None, expiration_id=None, save=False):
        self.vm_uuid = vm_uuid
        self.expiration_id = expiration_id
        self.do_save = save
        if save:
            db.session.add(self)
            db.session.commit()

    def auto_save(self):
        if self.do_save:
            db.session.add(self)
            db.session.commit()

    def set_vm_uuid(self, uuid):
        self.vm_uuid = uuid
        self.auto_save()

    def get_vm_uuid(self):
        return self.vm_uuid

    def set_vm(self, vm):
        self.vm.append(vm)
        self.auto_save()

    def get_vm(self):
        return self.vm[0]

    def set_expiration_id(self, id):
        self.expiration_id = id
        self.auto_save()

    def get_expiration_id(self):
        return self.expiration_id

    def set_expiration(self, expiration):
        self.vm_expiration.append(expiration)
        self.auto_save()
 
    def get_expiration(self):
        return self.expiration[0]



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
    vm_allocated_expiration = db.relationship("Expiration", primaryjoin="Expiration.id==VMAllocatedExpiration.expiration_id", backref="expiration_vm_allocated")

