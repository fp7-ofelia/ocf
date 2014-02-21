from models.resources.vtserver import VTServer
from models.resources.vmallocated import VMAllocated
from models.resources.xenserver import XenServer
from models.resources.xenvm import XenVM
from utils.base import db
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

class ServerAllocatedVMs(db.Model):
    """Relation between Allocated Virtual Machines and Virtualization Server"""
    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'vtserver_allocated_vms'
    # Table attributes
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = db.Column(db.ForeignKey(table_prefix + 'vtserver.id'), nullable=False)
    allocated_vm_id = db.Column(db.ForeignKey(table_prefix + 'virtualmachine_allocated.id'), nullable=False)
    # Relationships
    vtserver = db.relationship("VTServer", backref="vtserver_vms")
    allocated_vm = db.relationship("VMAllocated", backref="vtserver_associations")

class XenServerVMs(db.Model):
    """Relation between Xen Virtual Machines and Xen Virtualization Server"""
    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'xenserver_vms'
    # Table attributes
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    xenserver_id = db.Column(db.ForeignKey(table_prefix + 'xenserver.vtserver_ptr_id'), nullable=False)
    xenvm_id = db.Column(db.ForeignKey(table_prefix + 'xenvm.virtualmachine_ptr_id'), nullable=False)
    # Relationships
    xenserver = db.relationship("XenServer", backref="xenserver_vms", lazy="dynamic")
    xenvm = db.relationship("XenVM", backref="xenserver_associations", lazy="dynamic")
