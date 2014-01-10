from utils.base import db

'''@author: SergioVidiella'''


class NetworkInterfaceIp4s(db.Model):
    """Relation between Network interfaces and Ip's"""

    __tablename__ = 'vt_manager_networkinterface_ip4s'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    networkinterface_id = db.Column(db.Integer, db.ForeignKey('vt_manager_networkinterface.id'))
    ip4slot_id = db.Column(db.Integer, db.ForeignKey('vt_manager_ip4slot.id'))

    networkinterface = db.relationship("NetworkInterface", backref="networkinterface_ip4s")
    ip4slot = db.relationship("Ip4Slot", primaryjoin="Ip4Slot.id==NetworkInterfaceIp4s.ip4slot_id", backref="networkinterface_associations_ips")

