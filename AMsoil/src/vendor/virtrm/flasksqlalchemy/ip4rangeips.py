from base import db

'''@author: SergioVidiella'''


class Ip4RangeIps(db.Model):
    """Relation between Ip's and IpRange"""

    __tablename__ = 'vt_manager_ip4range_ips'
   
    id = db.Column(db.Integer, autoincrement=True, nullable=False,primary_key=True)
    ip4slot_id = db.Column(db.Integer, db.ForeignKey('vt_manager_ip4slot.id'))
    ip4range_id = db.Column(db.Integer, db.ForeignKey('vt_manager_ip4range.id'))

    ip4range = db.relationship("Ip4Range", backref="ip4range_ip4s", lazy="dynamic")
    ip4slot = db.relationship("Ip4Slot", lazy="dynamic")

