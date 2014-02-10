from sqlalchemy.orm import backref
from utils.base import db
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

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

