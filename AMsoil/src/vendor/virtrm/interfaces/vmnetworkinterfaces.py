from interfaces.networkinterface import NetworkInterface
from resources.virtualmachine import VirtualMachine
from utils.base import db
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

class VMNetworkInterfaces(db.Model):
    """Network interfaces related to a Virtual Machine"""

    config = pm.getService("config")
    __tablename__ = config.get("virtrm.DATABASE_PREFIX") + 'virtualmachine_networkInterfaces'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    virtualmachine_id = db.Column(db.Integer, db.ForeignKey(config.get("virtrm.DATABASE_PREFIX") + 'virtualmachine.id'), nullable=False)
    networkinterface_id = db.Column(db.Integer, db.ForeignKey(config.get("virtrm.DATABASE_PREFIX") + 'networkinterface.id'), nullable=False)

    vm = db.relationship("VirtualMachine", backref="vm_networkinterfaces")
    networkinterface = db.relationship("NetworkInterface", backref="vm_associations")

