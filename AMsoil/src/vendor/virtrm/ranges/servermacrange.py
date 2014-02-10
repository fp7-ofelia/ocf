from utils.base import db
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

class VTServerMacRange(db.Model):
    """Subscribed Mac ranges to the VTServer's."""

    config = pm.getService("config")
    __tablename__ = config.get("virtrm.DATABASE_PREFIX") + 'vtserver_subscribedMacRanges'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = db.Column(db.Integer, db.ForeignKey(config.get("virtrm.DATABASE_PREFIX") + 'vtserver.id'), nullable=False)
    macrange_id = db.Column(db.Integer, db.ForeignKey(config.get("virtrm.DATABASE_PREFIX") + 'macrange.id'), nullable=False)

    vtserver = db.relationship("VTServer", backref="vtserver_mac_range")
    subscribed_mac_range = db.relationship("MacRange", backref="vtserver_association")
