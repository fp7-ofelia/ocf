from models.ranges.ip4range import Ip4Range
from models.resources.ip4slot import Ip4Slot
from models.ranges.macrange import MacRange
from models.resources.macslot import MacSlot
from models.resources.vtserver import VTServer
from utils.base import db
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

class Ip4RangeIps(db.Model):
    """Relation between Ip's and IpRange"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'ip4range_ips'

    id = db.Column(db.Integer, autoincrement=True, nullable=False,primary_key=True)
    ip4slot_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'ip4slot.id'), nullable=False)
    ip4range_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'ip4range.id'), nullable=False)

    ip4range = db.relationship("Ip4Range", backref="ip4range_ip4s")
    ip4slot = db.relationship("Ip4Slot")



class MacRangeMacs(db.Model):
    """Relation between Mac's and MacRange"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'macrange_macs'

    id = db.Column(db.Integer, autoincrement=True, nullable=False,primary_key=True)
    macslot_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'macslot.id'), nullable=False)
    macrange_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'macrange.id'), nullable=False)

    macrange = db.relationship("MacRange", backref="macrange_macslot")
    macslot = db.relationship("MacSlot", backref="macrange")



class VTServerIpRange(db.Model):
    """Subscribed IP4 ranges to the VTServer's."""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'vtserver_subscribedIp4Ranges'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'vtserver.id'), nullable=False)
    ip4range_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'ip4range.id'), nullable=False)

    vtserver = db.relationship("VTServer", backref="vtserver_ip4_range")
    subscribed_ip4_range = db.relationship("Ip4Range", backref="vtserver_association")



class VTServerMacRange(db.Model):
    """Subscribed Mac ranges to the VTServer's."""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'vtserver_subscribedMacRanges'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'vtserver.id'), nullable=False)
    macrange_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'macrange.id'), nullable=False)

    vtserver = db.relationship("VTServer", backref="vtserver_mac_range")
    subscribed_mac_range = db.relationship("MacRange", backref="vtserver_association")

