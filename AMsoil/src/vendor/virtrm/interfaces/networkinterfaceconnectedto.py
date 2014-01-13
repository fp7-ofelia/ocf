from utils.base import db

'''@author: svidiella'''

class NetworkInterfaceConnectedTo(db.Model):
    """Connections between Network interfaces"""

    __tablename__ = 'vt_manager_networkinterface_connectedTo'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    from_networkinterface_id = db.Column(db.Integer, db.ForeignKey('vt_manager_networkinterface.id'))
    to_networkinterface_id = db.Column(db.Integer, db.ForeignKey('vt_manager_networkinterface.id'))

    to_networkinterface = db.relationship("NetworkInterface", primaryjoin="NetworkInterface.id==NetworkInterfaceConnectedTo.to_networkinterface_id", backref="from_networkinterface")
    from_networkinterface = db.relationship("NetworkInterface", primaryjoin="NetworkInterface.id==NetworkInterfaceConnectedTo.from_networkinterface_id", backref="to_network_interface")

