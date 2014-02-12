from models.interfaces.networkinterface import NetworkInterface
from models.resources.virtualmachine import VirtualMachine
from utils.base import db
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

class VMNetworkInterfaces(db.Model):
    """Network interfaces related to a Virtual Machine"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'virtualmachine_networkInterfaces'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    virtualmachine_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'virtualmachine.id'), nullable=False)
    networkinterface_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'networkinterface.id'), nullable=False)

    vm = db.relationship("VirtualMachine", backref="vm_networkinterfaces")
    networkinterface = db.relationship("NetworkInterface", backref="vm_associations")

