from utils.base import db

'''@author: SergioVidiella'''


class VTServerNetworkInterfaces(db.Model):
    """Network interfaces related to a VTServer."""

    __tablename__ = 'vt_manager_vtserver_networkInterfaces'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = db.Column(db.Integer, db.ForeignKey('vt_manager_vtserver.id'))
    networkinterface_id = db.Column(db.Integer, db.ForeignKey('vt_manager_networkinterface.id'))

    vtserver = db.relationship("VTServer", backref="vtserver_networkinterface")
    networkinterface = db.relationship("NetworkInterface", backref="vtserver_assocation")


