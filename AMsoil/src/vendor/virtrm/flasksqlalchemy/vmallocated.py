from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.orm import validates

from datetime import datetime, timedelta
import inspect

from base import db
from utils.choices import HDSetupTypeClass, VirtTypeClass, VirtTechClass, OSDistClass, OSVersionClass, OSTypeClass
from utils.mutexstore import MutexStore
from utils import validators


'''@author: SergioVidiella'''


class VMAllocated(db.Model):
    """Virtual Machines allocated for GeniV3 calls."""

    __tablename__ = 'amsoil_vt_manager_virtualmachine_allocated'

    '''General parameters'''
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(512), nullable=False, default="")
    memory = db.Column(db.Integer)
    number_of_cpus = db.Column("numberOfCPUs", db.Integer)
    disc_space_gb = db.Column("discSpaceGB", DOUBLE)

    '''Property parameters'''
    project_name = db.Column("projectName", db.String(1024), nullable=False, default="")
    slice_id = db.Column("sliceId", db.String(1024), nullable=False, default="")
    slice_name = db.Column("sliceName", db.String(512), nullable=False, default="")
    #XXX: Should be a ForeignKey, the relationship between servers the allocated vms
    server_id = db.Column("serverId", db.Integer)

    '''OS parameters'''
    operating_system_type = db.Column("operatingSystemType", db.String(512), nullable=False, default="")
    operating_system_version = db.Column("operatingSystemVersion", db.String(512), nullable=False, default="")
    operating_system_distribution = db.Column("operatingSystemDistribution", db.String(512), nullable=False, default="")

    '''Virtualization parameteres'''
    virtualization_setup_type = db.Column("virtualizationSetupType", db.String(1024), nullable=False, default="")
    hd_setup_type = db.Column("hdSetupType", db.String(1024), nullable=False, default="")
    hd_origin_path = db.Column("hdOriginPath", db.String(1024), nullable=False, default="")
    hypervisor = db.Column(db.String(512), nullable=False, default="xen")

    '''Allocation expiration time'''
    expires = db.Column(db.Date, nullable=False) 

    ''' Mutex over the instance '''
    # Mutex
    mutex = None

    '''Defines soft or hard state of the VM'''
    do_save = True

    '''Possible virtualization technologies'''
    XEN = "xen"

    __possible_virt_technologies = (XEN)

    @staticmethod
    def constructor(name,project_id,slice_id,slice_name,server_id,os_type,os_version,os_dist,memory,disc_space_gb,number_of_cpus,hd_setup_type,hd_origin_path,virt_setup_type,hypervisor,expires,save=True):
	self = VMAllocated()
	try:
	    self.name = name 
	    self.project_id = project_id
	    self.slice_id = slice_id
	    self.slice_name = slice_name
	    self.server_id = server_id
	    self.operating_system_type = os_type
	    self.operating_system_version = os_version
	    self.operating_system_distribution = os_dist
	    self.memory = memory
	    self.disc_space_gb = disc_space_gb
	    self.number_of_cpus = number_of_cpus
	    self.hd_setup_type = hd_setup_type
	    self.hd_origin_path = hd_origin_path
	    self.virtualization_setup_type = virt_setup_type
	    self.hypervisor = hypervisor
	    self.expires = expires
	    self.do_save = save
	    if save:
		db.session.add(self)
	     	db.session.commit()
	except Exception as e:
	    self.destroy()
	    raise e
	return self
    
    def auto_save(self):
	db.session.add(self)
 	db.session.commit()
    
    '''Destructor'''
    def destroy(self):
        with MutexStore.get_object_lock(self.get_lock_identifier()):
	    db.session.delete(self)
	    db.session.commit()

    '''Validators'''
    @validates('hd_setup_type')
    def validate_hd_setup_type(self, key, hd_setup_type):
        try:
            HDSetupTypeClass.validate_hd_setup_type(hd_setup_type)
            return hd_setup_type
        except Exception as e:
            raise e

    @validates('virtualization_setup_type')
    def validate_virtualization_setup_type(self, key, virt_type):
        try:
            VirtTypeClass.validate_virt_type(virt_type)
            return virt_type
        except Exception as e:
            raise e

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

    '''Getters and Setters'''
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
    
   def set_project_id(self,projectId):
        if not isinstance(project_id,str):
            project_id = str(project_id)
        self.project_id = project_id
        self.auto_save()

    def get_project_id(self):
        return self.project_id

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
    
   def get_hd_setup_type(self):
        return self.hd_setup_type

    def set_hd_setup_type(self, hd_type):
        HDSetupTypeClass.validate_hd_setup_type(hd_type)
        self.hd_setup_type = hd_type
        self.auto_save()

    def get_hd_origin_path(self):
        return  self.hd_setup_type

    def set_hd_origin_path(self, path):
        self.hd_origin_path = path
        self.auto_save()

    def get_virtualization_setup_type(self):
        return self.virtualization_setup_type

    def set_virtualization_setup_type(self,v_type):
        VirtTypeClass.validate_virt_type(v_type)
        self.virtualization_setup_type = v_type
        self.auto_save()

    def set_expiration(self, expires):
	self.expires = expires
	self.auto_save()
    
    def get_expiration(self):
	return self.expires

    def set_hypervisor(self, hypervisor):
	if hypervisor not in __possible_virt_technologies:
	    raise KeyError, "Invalid virtualization technology"
	else:
	    self.hypervisor = hypervisor
	    self.auto_save()
    
    def get_hypervisor(self):
	return self.hypervisor    
