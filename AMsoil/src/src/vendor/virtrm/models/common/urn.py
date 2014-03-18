from utils.base import db
import amsoil.core.log
import amsoil.core.pluginmanager as pm
import uuid

logging=amsoil.core.log.getLogger('URN')

'''@author: SergioVidiella'''

class URN(db.Model):
    """URN of the Virtual Machine (only GENI)."""

    config = pm.getService("config")
    __tablename__ = config.get("virtrm.DATABASE_PREFIX") + 'urn'
    __table_args__ = {'extend_existing':True}
    # Table attributes
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    urn = db.Column(db.String(1024), nullable=False, default=uuid.uuid4())
    do_save = True
    # Resource relationships
    virtualmachine = association_proxy('urn_vm', 'vm', creator=lambda urn:VirtualMachineURN(vm=vm))
    virtualmachine_allocated = association_proxy('urn_vm_allocated', 'vm_allocated', creator=lambda vm:VMAllocatedURN(vm_allocated=vm))

    class VirtualMachineURN(db.Model):
    """Relation between VirtualMachines and their URN (only GENI)"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'virtualmachine_urn'
    __table_args__ = {'extend_existing':True}
    # Table attributes
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vm_uuid = db.Column(db.ForeignKey(table_prefix + 'virtualmachine.uuid'), nullable=False)
    urn_id = db.Column(db.ForeignKey(table_prefix + 'urn.id'), nullable=False)
    # Relationships
    vm = db.relationship("VirtualMachine", primaryjoin="VirtualMachine.uuid==VirtualMachineURN.vm_uuid", backref=db.backref("urn_from_vm", cascade="all, delete-orphan")
    vm_urn = db.relationship("URN", primaryjoin="URN.id==VirtualMachineURN.urn_id", backref=db.backref("urn_vm", cascade = "all, delete-orphan"))

    def get_urn(self)
        return self.vm_urn

    def get_vm(self):
        return self.vm

    def destroy(self):
        db.session.delete(self)
        db.session.commit()


class VMAllocatedURN(db.Model):
    """Relation between Allocated VirtualMachines and their URN (only GENIv3)"""
    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'virtualmachine_allocated_urn'
    __table_args__ = {'extend_existing':True}
    # Table attributes
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vm_uuid = db.Column(db.ForeignKey(table_prefix + 'virtualmachine_allocated.uuid'), nullable=False)
    urn_id = db.Column(db.ForeignKey(table_prefix + 'urn.id'), nullable=False)
    # Relationships
    vm_allocated = db.relationship("VMAllocated", primaryjoin="VMAllocated.uuid==VMAllocatedURN.vm_uuid", backref=db.backref("urn_from_vm_allocated", cascade="all, delete-orphan"))
    vm_allocated_urn = db.relationship("URN", primaryjoin="URN.id==VMAllocatedURN.urn_id", backref=db.backref("urn_vm_allocated", cascade="all, delete-orphan"))

    def get_urn(self):
        return self.vm_allocated_urn

    def get_vm(self)
        return sef.vm_allocated

    def destroy(self):
        db.session.delete(self)
        db.session.commit()
                                                                                              151,12        Bot

