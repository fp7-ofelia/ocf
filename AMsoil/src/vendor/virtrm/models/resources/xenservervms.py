from models.resources.xenserver import XenServer
from models.resources.xenvm import XenVM
from utils.base import db
import amsoil.core.pluginmanager as pm

'''@author: SergioVidiella'''

class XenServerVMs(db.Model):
    """Relation between Xen Virtual Machines and Xen Virtualization Server"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'xenserver_vms'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    xenserver_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'xenserver.vtserver_ptr_id'), nullable=False)
    xenvm_id = db.Column(db.Integer, db.ForeignKey(table_prefix + 'xenvm.virtualmachine_ptr_id'), nullable=False)

    xenserver = db.relationship("XenServer", backref="xenserver_vms", lazy="dynamic")
    xenvm = db.relationship("XenVM", backref="xenserver_associations", lazy="dynamic")


