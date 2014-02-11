from ranges.ip4range import Ip4Range
from resources.vtserver import VTServer
from utils.base import db
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

class VTServerIpRange(db.Model):
    """Subscribed IP4 ranges to the VTServer's."""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'vtserver_subscribedIp4Ranges'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'vtserver.id'), nulable=False)
    ip4range_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'ip4range.id'), nullable=False)

    vtserver = db.relationship("VTServer", backref="vtserver_ip4_range")
    subscribed_ip4_range = db.relationship("Ip4Range", backref="vtserver_association")

