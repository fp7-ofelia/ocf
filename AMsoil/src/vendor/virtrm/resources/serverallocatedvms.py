from utils.base import db
from sqlalchemy.orm import backref

'''@author: SergioVidiella'''

class ServerAllocatedVMs(db.Model):
    """Relation between Allocated Virtual Machines and Virtualization Server"""

    __tablename__ = 'vt_manager_vtserver_allocated_vms'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = db.Column(db.Integer, db.ForeignKey('vt_manager_vtserver.id'))
    allocated_vm_id = db.Column(db.Integer, db.ForeignKey('amsoil_vt_manager_virtualmachine_allocated.id'))

    vtserver = db.relationship("VTServer", backref="vtserver_vms")
    allocated_vm = db.relationship("VMAllocated", backref="vtserver_associations")


