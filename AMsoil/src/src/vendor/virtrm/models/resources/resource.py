from models.resources.virtualmachine import VirtualMachine
from models.resources.vmallocated import VMAllocated
from sqlalchemy.ext.associationproxy import association_proxy
from utils.base import db
import amsoil.core.log
import amsoil.core.pluginmanager as pm

logging=amsoil.core.log.getLogger('Resource')

'''@author: SergioVidiella'''

class Resource(db.Model):
    """General class for resources"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'resource'

    '''General parameters'''
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    GID = db.Column(db.String(1024), nullable=True)

    '''Specific resources type (due to heritage is no possible currently)'''
    vm_uuid = db.Column(db.ForeignKey(table_prefix + 'virtualmachine.uuid'))
    vm_allocated_uuid = db.Column(db.ForeignKey(table_prefix + 'virtualmachine_allocated.uuid'))

    vm = db.relationship("VirtualMachine", backref=db.backref("vm_resource", cascade = "all, delete-orphan"))
    vm_allocated = db.relationship("VMAllocated", backref=db.backref("vm_allocated_resource", cascade="all, delete-orphan"))
     
    '''Defines soft or hard state of the Container'''
    do_save = False

