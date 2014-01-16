from utils.base import db

'''@author: SergioVidiella'''

class VMAllocatedExpires(db.Model):
    """Relation between VirtualMachines and their expiration time (only GENIv3)"""
    
    __tablename__ = 'amsoil_vt_manager_virtualmachine_allocated_expires'
    
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vm_id = db.Column(db.Integer, db.ForeignKey('amsoil_vt_manager_virtualmachine_allocated.id'))
    expires_id = db.Column(db.Integer, db.ForeignKey('amsoil_vt_manager_expires.id'))
    
    vm = db.relationship("VMAllocated", backref="vm_expiration")
    expires = db.relationship("Expires", backref="expires_vm")
