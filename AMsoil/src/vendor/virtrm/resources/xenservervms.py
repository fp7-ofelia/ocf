from utils.base import db
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

class XenServerVMs(db.Model):
    """Relation between Xen Virtual Machines and Xen Virtualization Server"""

    config = pm.getService("config")
    __tablename__ = config.get("virtrm.DATABASE_PREFIX") + 'xenserver_vms'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    xenserver_id = db.Column(db.Integer, db.ForeignKey(config.get("virtrm.DATABASE_PREFIX") + 'xenserver.vtserver_ptr_id'), nullable=False)
    xenvm_id = db.Column(db.Integer, db.ForeignKey(config.get("virtrm.DATABASE_PREFIX") + 'xenvm.virtualmachine_ptr_id'), nullable=False)

    xenserver = db.relationship("XenServer", backref="xenserver_vms", lazy="dynamic")
    xenvm = db.relationship("XenVM", backref="xenserver_associations", lazy="dynamic")


