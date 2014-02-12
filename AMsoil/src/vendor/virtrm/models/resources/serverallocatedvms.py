from models.resources.vtserver import VTServer
from models.resources.vmallocated import VMAllocated
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


