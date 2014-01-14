from utils.base import db

'''@author: SergioVidiella'''


class VTServerMacRange(db.Model):
    """Subscribed Mac ranges to the VTServer's."""

    __tablename__ = 'vt_manager_vtserver_subscribedMacRanges'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = db.Column(db.Integer, db.ForeignKey('vt_manager_vtserver.id'))
    macrange_id = db.Column(db.Integer, db.ForeignKey('vt_manager_macrange.id'))

    vtserver = db.relationship("VTServer", backref="vtserver_mac_range")
    subscribed_mac_range = db.relationship("MacRange", backref="vtserver_association")
