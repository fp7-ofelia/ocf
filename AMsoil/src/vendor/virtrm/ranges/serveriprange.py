from utils.base import db

'''@author: SergioVidiella'''


class VTServerIpRange(db.Model):
    """Subscribed IP4 ranges to the VTServer's."""

    __tablename__ = 'vt_manager_vtserver_subscribedIp4Ranges'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = db.Column(db.Integer, db.ForeignKey('vt_manager_vtserver.id'))
    ip4range_id = db.Column(db.Integer, db.ForeignKey('vt_manager_ip4range.id'))

    vtserver = db.relationship("VTServer", backref="vtserver_ip4_range", lazy="dynamic")
    subscribed_ip4_range = db.relationship("Ip4Range", backref="vtserver_association", lazy="dynamic")

