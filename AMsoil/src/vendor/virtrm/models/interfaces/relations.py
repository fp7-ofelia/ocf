from models.interfaces.networkinterface import NetworkInterface
from models.resources.ip4slot import Ip4Slot
from models.resources.vtserver import VTServer
from models.resources.virtualmachine import VirtualMachine
from utils.base import db
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

class NetworkInterfaceConnectedTo(db.Model):
    """Connections between Network interfaces"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'networkinterface_connectedTo'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    from_networkinterface_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'networkinterface.id'), nullable=False)
    to_networkinterface_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'networkinterface.id'), nullable=False)

    to_networkinterface = db.relationship("NetworkInterface", primaryjoin="NetworkInterface.id==NetworkInterfaceConnectedTo.to_networkinterface_id", backref="from_networkinterface")
    from_networkinterface = db.relationship("NetworkInterface", primaryjoin="NetworkInterface.id==NetworkInterfaceConnectedTo.from_networkinterface_id", backref="to_network_interface")



class NetworkInterfaceIp4s(db.Model):
    """Relation between Network interfaces and Ip's"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'networkinterface_ip4s'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    networkinterface_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'networkinterface.id'), nullable=False)
    ip4slot_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'ip4slot.id'), nullable=False)

    networkinterface = db.relationship("NetworkInterface", backref="networkinterface_ip4s")
    ip4slot = db.relationship("Ip4Slot", primaryjoin="Ip4Slot.id==NetworkInterfaceIp4s.ip4slot_id", backref="networkinterface_associations_ips")



class VTServerNetworkInterfaces(db.Model):
    """Network interfaces related to a VTServer"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'vtserver_networkInterfaces'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'vtserver.id'), nullable=False)
    networkinterface_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'networkinterface.id'), nullable=False)

    vtserver = db.relationship("VTServer", backref="vtserver_networkinterface")
    networkinterface = db.relationship("NetworkInterface", backref="vtserver_assocation")



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
