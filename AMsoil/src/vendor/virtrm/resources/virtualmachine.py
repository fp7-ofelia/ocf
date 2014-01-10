from interfaces.networkinterface import NetworkInterface
from sqlalchemy import desc
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from utils import validators
from utils.base import db
from utils.choices import VirtTechClass, OSDistClass, OSVersionClass, OSTypeClass
import inspect

'''@author: SergioVidiella'''

class VirtualMachine(db.Model):
    """VirtualMachine Class."""

    __tablename__ = 'vt_manager_virtualmachine'

    __child_classes = (
            'XenVM',
    )

    ''' General parameters '''
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(512), nullable=False, default="")
    uuid = db.Column(db.String(1024), nullable=False, default="")
    memory = db.Column(db.Integer)
    number_of_cpus = db.Column("numberOfCPUs", db.Integer)
    disc_space_gb = db.Column("discSpaceGB", DOUBLE)

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
    network_interfaces = association_proxy("vm_networkinterfaces", "networkinterface")

    '''Other'''
    callback_url = db.Column("callBackURL", db.String(200))
    state = db.Column(db.String(24))

    '''Possible states'''
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
            db.session.add(self)
            db.session.commit()
    
    ''' Public methods '''
    def get_child_object(self):
        for child_class in self.__child_classes:
            try:
                return self.__getattribute__(child_class.lower())
            except eval(child_class).DoesNotExist:
                return self
    
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
    
    def set_uuid(self,expedient_id):
        if not isinstance(expedient_id,int):
            expedient_id = int(expedient_id)
        self.expedient_id = expedient_id
        self.auto_save()
        
    def get_uuid(self):
        return self.expedient_id
    
    def set_state(self,state):
        if state not in self.__possible_states:
            raise KeyError, "Unknown state"
        else:
            self.state = state
            self.auto_save()
        
    def get_state(self):
        return self.state
    
    def set_memory(self,memory):
        self.memory = memory
        self.auto_save()
    
    def get_memory(self):
        return self.memory
    
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
