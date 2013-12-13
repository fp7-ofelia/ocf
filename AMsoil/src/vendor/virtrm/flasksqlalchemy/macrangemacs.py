from sqlalchemy.orm import backref

from base import db


'''@author: SergioVidiella'''


class MacRangeMacs(db.Model):
    """Relation between Mac's and MacRange"""

    __tablename__ = 'vt_manager_macrange_macs'
   
    id = db.Column(db.Integer, autoincrement=True, nullable=False,primary_key=True)
    macslot_id = db.Column(db.Integer, db.ForeignKey('vt_manager_macslot.id'))
    macrange_id = db.Column(db.Integer, db.ForeignKey('vt_manager_macrange.id'))

    macrange = db.relationship("MacRange", backref="macrange_macslot", lazy="dynamic")
    macslot = db.relationship("MacSlot", backref="macrange", lazy="dynamic")

