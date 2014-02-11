from resources.virtualmachine import VirtualMachine
from utils.base import db
from utils.expires import Expires
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

class VMExpires(db.Model):
    """Relation between VirtualMachines and their expiration time (only GENIv3)"""
    
    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'virtualmachine_expires'
    
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vm_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'virtualmachine.id'), nullable=False)
    expires_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'expires.id'), nullable=False)
    
    vm = db.relationship("VirtualMachine", backref="vm_expiration")
    expires = db.relationship("Expires", backref="expires_vm")
