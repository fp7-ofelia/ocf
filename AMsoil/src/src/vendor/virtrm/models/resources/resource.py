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
    vm_uuid = db.Column(db.ForeignKey(table_prefix + 'virtualmachine.uuid'), nullable=True)
    vm_allocated_uuid = db.Column(db.ForeignKey(table_prefix + 'virtualmachine_allocated.uuid'), nullable=True)

    vm = db.relationship("VirtualMachine", backref=db.backref("vm_resource", cascade = "all, delete-orphan"))
    vm_allocated = db.relationship("VMallocated", backref=db.backref("vm_allocated_resource", cascade="all, delete-orphan"))
     
    '''Defines soft or hard state of the Container'''
    do_save = False

    def __init__(self, GID=None, vm=None, vm_allocated=None, save=False):
        self.GID = GID
        self.do_save = save
        if vm and vm_allocated:
            raise Exception("Only a VM OR an AllocatedVM can be assigned to a Resource")
        if vm:
            try:
                self.set_vm(vm)
            except Exception as e:
                raise e
        if vm_allocated:
            try:
                self.set_vm_allocated(vm_allocated)
            except Exception as e:

    def auto_save(self):
        if self.do_save is True:
            self.save()

    def save(self):
        db.session.add(self)
        db.session.commit()

    '''Getters and Setters'''
    def set_GID(self, uuid):
        self.GID = GID
        self.auto_save()

    def get_GID(self):
        return self.GID

    def set_vm(self, vm):
        pass

    def get_vm(self):
        return self.vm

    def set_vm_allocated(self, vm_allocated):
        pass

    def get_vm_allocated(self):
        return self.vm_allocated

    '''Validators'''
    @db.validates('GID')
    def validate_GID(self, key, GID):
        container = Container.query.filter_by(GID=GID).all()
        if container:
            raise Exception("Given GID is taken and not unique")
        return GID
