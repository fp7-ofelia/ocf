from models.ranges.ip4range import Ip4Range
from models.resources.ip4slot import Ip4Slot
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

