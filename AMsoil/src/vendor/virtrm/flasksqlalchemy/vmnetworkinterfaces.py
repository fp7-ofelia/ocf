from base import db

from virtualmachine import VirtualMachine
from networkinterface import NetworkInterface


'''@author: SergioVidiella'''


class VMNetworkInterfaces(db.Model):
    """Network interfaces related to a Virtual Machine"""

    __tablename__ = 'vt_manager_virtualmachine_networkInterfaces'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    virtualmachine_id = db.Column(db.Integer, db.ForeignKey('vt_manager_virtualmachine.id'))
    networkinterface_id = db.Column(db.Integer, db.ForeignKey('vt_manager_networkinterface.id'))

    vm = db.relationship("VirtualMachine", backref="vm_networkinterfaces")
    networkinterface = db.relationship("NetworkInterface", backref="vm_associations")

