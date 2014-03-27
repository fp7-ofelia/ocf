from models.resources.virtualmachine import VirtualMachine
from sqlalchemy.ext.associationproxy import association_proxy
from utils.base import db
import amsoil.core.log
import amsoil.core.pluginmanager as pm
import uuid

logging=amsoil.core.log.getLogger('Container')

'''@author: SergioVidiella'''

class Container(db.Model):
    """Container of the resources."""

    config = pm.getService("config")
    __tablename__ = config.get("virtrm.DATABASE_PREFIX") + 'container'

    '''General parameters'''
    uuid = db.Column(db.String(512), nullable=False, primary_key=True)
    GID = db.Column(db.String(1024), nullable=False, default="")
    prefix = db.Column(db.String(512), nullable=False, default="")

    '''Container relations'''
    vms = association_proxy("vms_container", "vms", creator=lambda vm:ContainerVMs(vms=vm))

    '''Defines soft or hard state of the Container'''
    do_save = False

    def __init__(self, GID="", prefix="", uuid=None, save=False):
        self.uuid = str(uuid.uuid4())
        self.GID = GID
        self.prefix = prefix
        if not uuid:
            uuid = uuid.uuid4()
        self.uuid = uuid
        self.do_save = save
        if self.do_save:
            self.auto_save()

    def auto_save(self):
        if self.do_save is True:
            self.save()

    def save(self):
        db.session.add(self)
        db.session.commit()

    '''Getters and Setters'''
    def set_uuid(self, uuid):
        self.uuid = uuid
        self.auto_save()

    def get_uuid(self):
        return self.uuid

    def set_GID(self, gid):
        self.GID = gid
        self.auto_save()
 
    def get_GID(self):
        return self.GID

    def set_prefix(self, prefix):
        self.prefix = prefix
        self.auto_save()

    def get_prefix(self):
        return self.prefix

    '''Validators'''
    @db.validates('GID')
    def validate_GID(self, key, GID):
        try:
            Container.query.filter_by(GID=GID, prefix=self.prefix).one()
            return GID
        except Exception as e:
            raise e
            
    @db.validates('prefix')
    def validate_prefix(self, key, prefix):
        try:
            ContainerPrefixClass.validate_prefix(prefix)
            # If GID is given, validate that is not duplicated for given prefix
            if self.GID:
                container = Container.query.filter_by(GID=self.GID, prefix=prefix).one()
            return prefix
        except Exception as e:
            raise e
    
    
class ContainerVMs(db.Model):
    """Relation between Containers and the contained Resources"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'container_virtualmachines'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    container_uuid = db.Column(db.ForeignKey(table_prefix + 'container.uuid'), nullable=False)
    resource_id = db.Column(db.ForeignKey(table_prefix + 'virtualmachine.uuid'), nullable=False)

    container = db.relationship("Container", backref=db.backref("vms_container", cascade="all, delete-orphan"))
    vms = db.relationship("VirtualMachine", backref=db.backref("container_vm", cascade="all, delete-orphan"))


