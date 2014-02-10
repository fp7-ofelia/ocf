from utils.base import db
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

class VMExpires(db.Model):
    """Relation between VirtualMachines and their expiration time (only GENIv3)"""
    
    config = pm.getService("config")
    __tablename__ = config.get("virtrm.DATABASE_PREFIX") + 'virtualmachine_expires'
    
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vm_id = db.Column(db.Integer, db.ForeignKey(config.get("virtrm.DATABASE_PREFIX") + 'virtualmachine.id'), nullable=False)
    expires_id = db.Column(db.Integer, db.ForeignKey(config.get("virtrm.DATABASE_PREFIX") + 'expires.id'), nullable=False)
    
    vm = db.relationship("VirtualMachine", backref="vm_expiration")
    expires = db.relationship("Expires", backref="expires_vm")
