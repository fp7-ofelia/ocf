from models.interfaces.networkinterface import NetworkInterface
from sqlalchemy import desc
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from utils import validators
from utils.base import db
from utils.choices import VirtTechClass, OSDistClass, OSVersionClass, OSTypeClass
import amsoil.core.log
import amsoil.core.pluginmanager as pm
import inspect
import uuid

logging=amsoil.core.log.getLogger('VirtualMachine')

'''@author: msune, SergioVidiella'''

class VirtualMachine(db.Model):
    """VirtualMachine Class."""

    config = pm.getService("config")
    __tablename__ = config.get("virtrm.DATABASE_PREFIX") + 'virtualmachine'
    __table_args__ = {'extend_existing':True}
    __mapper_args__ = {
        'polymorphic_on':'type'
    }

    __child_classes = (
            'XenVM',
            'AllocatedVM',
    )

    ''' General parameters '''
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(512), nullable=False, default="")
    uuid = db.Column(db.String(1024), nullable=False, default=uuid.uuid4())
    memory_mb = db.Column("memory_mb", db.Integer)
    number_of_cpus = db.Column("numberOfCPUs", db.Integer)
    disc_space_gb = db.Column("discSpaceGB", DOUBLE)
    urn = db.Column(db.String(1024), nullable=True)
    type = db.Column(db.String(1024), nullable=False, default="xen")

    '''Property parameters'''
    project_id = db.Column("projectId", db.String(1024), nullable=False, default="")
    project_name = db.Column("projectName", db.String(1024), nullable=False, default="")
    slice_id = db.Column("sliceId", db.String(1024), nullable=False, default="")
    slice_name = db.Column("sliceName", db.String(1024), nullable=False, default="")
    gui_user_name = db.Column("guiUserName", db.String(1024), nullable=False, default="")
    gui_user_uuid = db.Column("guiUserUUID", db.String(1024), nullable=False, default="")
    expedient_id = db.Column("expedientId", db.Integer)

    '''OS parameters'''
    operating_system_type = db.Column("operatingSystemType", db.String(512), nullable=False, default="")
    operating_system_version = db.Column("operatingSystemVersion", db.String(512), nullable=False, default="")
    operating_system_distribution = db.Column("operatingSystemDistribution", db.String(512), nullable=False, default="")

    '''Networking'''
    network_interfaces = association_proxy("vm_networkinterfaces", "networkinterface", creator=lambda iface:VMNetworkInterfaces(networkinterface=iface))

    '''Other'''
    callback_url = db.Column("callBackURL", db.String(200))
    state = db.Column(db.String(24))

    '''Possible states'''
    ALLOCATED_STATE = 'allocated'
    RUNNING_STATE = 'running'
    CREATED_STATE = 'created (stopped)'
    STOPPED_STATE = 'stopped'
    UNKNOWN_STATE = 'unknown'
    FAILED_STATE = 'failed'
    ONQUEUE_STATE = 'on queue'
    STARTING_STATE = 'starting...'
    STOPPING_STATE = 'stopping...'
    CREATING_STATE = 'creating...'
    DELETING_STATE = 'deleting...'
    REBOOTING_STATE = 'rebooting...'

    __possible_states = (RUNNING_STATE,CREATED_STATE,STOPPED_STATE,UNKNOWN_STATE,FAILED_STATE,ONQUEUE_STATE,STARTING_STATE,STOPPING_STATE,CREATING_STATE,DELETING_STATE,REBOOTING_STATE)

    ''' Mutex over the instance '''
    mutex = None

    '''Defines soft or hard state of the VM'''
    do_save = True

    '''Validators'''
    @validates('name')
    def validate_name(self, key, name):
        try:
            validators.vm_name_validator(name)
            return name
        except Exception as e:
            logging.debug("************* VALIDATION NAME %s ERROR => %s" % (name, e))
            raise e
    
    @validates('operating_system_type')
    def validate_operatingsystemtype(self, key, os_type):
        try:
            OSTypeClass.validate_os_type(os_type)
            return os_type
        except Exception as e:
            raise e
    
    @validates('operating_system_distribution')
    def validate_operatingsystemdistribution(self, key, os_distribution):
        try:
            OSDistClass.validate_os_dist(os_distribution)
            return os_distribution
        except Exception as e:
            raise e
    
    @validates('operating_system_version')
    def validate_operatingsystemversion(self, key, os_version):
        try:
            OSVersionClass.validate_os_version(os_version)
            return os_version
        except Exception as e:
            raise e
    
    def auto_save(self):
        if self.do_save:
            self.save()
 
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    ''' Public methods '''
    def get_child_object(self):
        for child_class in self.__child_classes:
            try:
                logging.debug("*********** POSSIBLE CHILD CLASS %s" % child_class)
                child =  self.__getattribute__(child_class.lower())[0]
                logging.debug("********** %s IS CHILD CLASS %s" %(child_class, str(child.__dict__)))
                return child
            except:
                logging.debug("*********** %s IS NOT THE CHILD CLASS" % child_class)
                pass
        return self
#            except eval(child_class).DoesNotExist:
#                return self
    
    def get_lock_identifier(self):
        # Uniquely identifies object by a key
        return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)
    
    def set_name(self, name):
        try:
            validators.vm_name_validator(name)
            self.name = name
            self.auto_save()
        except Exception as e:
            raise e
        
    def get_name(self):
        return self.name
    
    def set_uuid(self, uuid):
        self.uuid = uuid
        self.auto_save()
        
    def get_uuid(self):
        return self.uuid
 
    def set_urn(self, urn):
        self.urn = urn
        self.auto_save()

    def get_urn(self):
        return self.urn
    
    def set_project_id(self,projectId):
        if not isinstance(project_id,str):
            project_id = str(project_id)
        self.project_id = project_id
        self.auto_save()
        
    def get_project_id(self):
        return self.project_id
    
    def set_project_name(self,project_name):
        if not isinstance(project_name,str):
            project_name = str(project_name)
        self.project_name = project_name
        self.auto_save()
        
    def get_project_name(self):
        return self.project_name
    
    def set_slice_id(self, value):
        self.slice_id = value
        self.auto_save()
         
    def get_slice_id(self):
        return self.slice_id
    
    def set_slice_name(self, value):
        self.slice_name = value
        self.auto_save()
    
    def get_slice_name(self):
        return self.slice_name
    
    def set_uuid(self, uuid):
        self.uuid = uuid
        self.auto_save()
        
    def get_uuid(self):
        return self.uuid
    
    def set_state(self,state):
        if state not in self.__possible_states:
            raise KeyError, "Unknown state"
        else:
            self.state = state
            self.auto_save()
        
    def get_state(self):
        return self.state
    
    def set_memory_mb(self,memory):
        self.memory_mb = memory
        self.auto_save()
    
    def get_memory_mb(self):
        return self.memory_mb
    
    def set_number_of_cpus(self,num):
        self.number_of_cpus = num
        self.auto_save()
        
    def get_number_of_cpus(self):
        return self.number_of_cpus
    
    def set_disc_space_gb(self,num):
        self.disc_space_gb = num
        self.auto_save()
         
    def get_disc_space_gb(self):
        return self.disc_space_gb
    
    def set_os_type(self, type):
        OSTypeClass.validate_os_type(type)
        self.operating_system_type = type
        self.auto_save()
        
    def get_os_type(self):
        return self.operating_system_type
    
    def set_os_version(self, version):
        OSVersionClass.validate_os_version(version)
        self.operating_system_version = version
        self.auto_save()
        
    def get_os_version(self):
        return self.operating_system_version
    
    def set_os_distribution(self, dist):
        OSDistClass.validate_os_dist(dist)
        self.operating_system_distribution = dist
        self.auto_save()
        
    def get_os_distribution(self):
        return self.operating_system_distribution
    
    def set_callback_url(self, url):
        self.callback_url = url
        self.auto_save()
        
    def get_callback_url(self):
        return self.callback_url
    
    def get_network_interfaces(self):
        return self.network_interfaces.order_by('-isMgmt','id').all()


class VMNetworkInterfaces(db.Model):
    """Network interfaces related to a Virtual Machine"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'virtualmachine_networkInterfaces'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    virtualmachine_id = db.Column(db.ForeignKey(table_prefix + 'virtualmachine.id'), nullable=False)
    networkinterface_id = db.Column(db.ForeignKey(table_prefix + 'networkinterface.id'), nullable=False)

    vm = db.relationship("VirtualMachine", primaryjoin="VirtualMachine.id==VMNetworkInterfaces.virtualmachine_id", backref=db.backref("vm_networkinterfaces", cascade="all, delete-orphan"))
    networkinterface = db.relationship("NetworkInterface", primaryjoin="NetworkInterface.id==VMNetworkInterfaces.networkinterface_id", backref=db.backref("vm_associations", cascade="all, delete-orphan"))
