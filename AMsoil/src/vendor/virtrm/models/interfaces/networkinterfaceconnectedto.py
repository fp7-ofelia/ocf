from models.interfaces.networkinterface import NetworkInterface
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

