from utils.base import db
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

class NetworkInterfaceIp4s(db.Model):
    """Relation between Network interfaces and Ip's"""

    config = pm.getService("config")
    __tablename__ = config.get("virtrm.DATABASE_PREFIX") + 'networkinterface_ip4s'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    networkinterface_id = db.Column(db.Integer, db.ForeignKey(config.get("virtrm.DATABASE_PREFIX") + 'networkinterface.id'), nullable=False)
    ip4slot_id = db.Column(db.Integer, db.ForeignKey(config.get("virtrm.DATABASE_PREFIX") + 'ip4slot.id'), nullable=False)

    networkinterface = db.relationship("NetworkInterface", backref="networkinterface_ip4s")
    ip4slot = db.relationship("Ip4Slot", primaryjoin="Ip4Slot.id==NetworkInterfaceIp4s.ip4slot_id", backref="networkinterface_associations_ips")

