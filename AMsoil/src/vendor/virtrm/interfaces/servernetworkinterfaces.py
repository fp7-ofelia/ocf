from utils.base import db
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

class VTServerNetworkInterfaces(db.Model):
    """Network interfaces related to a VTServer."""

    config = pm.getService("config")
    __tablename__ = config.get("virtrm.DATABASE_PREFIX") + 'vtserver_networkInterfaces'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = db.Column(db.Integer, db.ForeignKey(config.get("virtrm.DATABASE_PREFIX") + 'vtserver.id'), nullable=False)
    networkinterface_id = db.Column(db.Integer, db.ForeignKey(config.get("virtrm.DATABASE_PREFIX") + 'networkinterface.id'), nullable=False)

    vtserver = db.relationship("VTServer", backref="vtserver_networkinterface")
    networkinterface = db.relationship("NetworkInterface", backref="vtserver_assocation")


