from interfaces.networkinterface import NetworkInterface
from resources.vtserver import VTServer
from utils.base import db
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

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


