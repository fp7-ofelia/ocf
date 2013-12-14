from base import db

'''@author: SergioVidiella'''

class XenServerVMs(db.Model):
    """Relation between Xen Virtual Machines and Xen Virtualization Server"""

    __tablename__ = 'vt_manager_xenserver_vms'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    xenserver_id = db.Column(db.Integer, db.ForeignKey('vt_manager_xenserver.vtserver_ptr_id'))
    xenvm_id = db.Column(db.Integer, db.ForeignKey('vt_manager_xenvm.virtualmachine_ptr_id'))

    xenserver = db.relationship("XenServer", backref="xenserver_vms", lazy="dynamic")
    xenvm = db.relationship("XenVM", backref="xenserver_associations", lazy="dynamic")


