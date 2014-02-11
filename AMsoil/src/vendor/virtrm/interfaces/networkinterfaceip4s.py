from interfaces.networkinterface import NetworkInterface
from resources.ip4slot import Ip4Slot
from utils.base import db
import amsoil.core.log
import amsoil.core.pluginmanager as pm

logging=amsoil.core.log.getLogger('NetworkInterfaceIp4s')

'''@author: SergioVidiella'''

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

