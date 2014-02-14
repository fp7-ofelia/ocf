from models.common.expires import Expires
from models.resources.virtualmachine import VirtualMachine
from models.resources.vtserver import VTServer
from models.resources.vmallocated import VMAllocated
from models.resources.xenserver import XenServer
from models.resources.xenvm import XenVM
from utils.base import db
from sqlalchemy.orm import backref
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

class ServerAllocatedVMs(db.Model):
    """Relation between Allocated Virtual Machines and Virtualization Server"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'vtserver_allocated_vms'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'vtserver.id'), nullable=False)
    allocated_vm_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'virtualmachine_allocated.id'), nullable=False)

    vtserver = db.relationship("VTServer", backref="vtserver_vms")
    allocated_vm = db.relationship("VMAllocated", backref="vtserver_associations")



class VMExpires(db.Model):
    """Relation between VirtualMachines and their expiration time (only GENIv3)"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'virtualmachine_expires'
    __table_args__ = {'extend_existing':True}

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vm_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'virtualmachine.id'), nullable=False)
    expires_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'expires.id'), nullable=False)

    vm = db.relationship("VirtualMachine", backref="vm_expiration")
    expires = db.relationship("Expires", backref="expires_vm")



class XenServerVMs(db.Model):
    """Relation between Xen Virtual Machines and Xen Virtualization Server"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'xenserver_vms'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    xenserver_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'xenserver.vtserver_ptr_id'), nullable=False)
    xenvm_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'xenvm.virtualmachine_ptr_id'), nullable=False)

    xenserver = db.relationship("XenServer", backref="xenserver_vms", lazy="dynamic")
    xenvm = db.relationship("XenVM", backref="xenserver_associations", lazy="dynamic")
