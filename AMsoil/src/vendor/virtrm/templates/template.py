from sqlalchemy.orm import validates
from utils.base import db
from utils.choices import HDSetupTypeClass, VirtTypeClass, VirtTechClass, OSDistClass, OSVersionClass, OSTypeClass
from utils.mutexstore import MutexStore
#from resources.vtserver import VTServer
#from resources.virtualmachine import VirtualMachine
#from resources.vmallocated import VMAllocated
import common
import amsoil.core.pluginmanager as pm
import inspect

'''@author: SergioVidiella'''

class Template(db.Model):
    """Templates for the VMs disc images supported."""

    config = pm.getService("config")
    __tablename__ = config.get("virtrm.DATABASE_PREFIX") + 'template'

    '''General parameters'''
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(512), nullable=False, default="")
    uuid = db.Column(db.String(1024), nullable=False)
    minimum_memory = db.Column(db.Integer, nullable=False)

    '''OS parameters'''
    operating_system_type = db.Column(db.String(512), nullable=False, default="")
    operating_system_version = db.Column(db.String(512), nullable=False, default="")
    operating_system_distribution = db.Column(db.String(512), nullable=False, default="")

    '''Virtualization parameteres'''
    virtualization_setup_type = db.Column(db.String(1024),nullable=False,default="")
    hard_disk_setup_type = db.Column(db.String(1024), nullable=False, default="")
    hard_disk_path = db.Column(db.String(1024), nullable=False, default="")

    ''' Mutex over the instance '''
    mutex = None

    '''Defines soft or hard state of the Template'''
    do_save = True

#    servers = association_proxy("vt_manager_vtserver", "vtserver")
#    allocated_vms = association_proxy("vt_manager_virtualmachine_allocated", "vmallocated")
#    vms = association_proxy("vt_manager_virtualmachine", "virtualmachine")

    @staticmethod
    def constructor(name,minimum_memory,os_type,os_version,os_distro,virt_setup_type,hd_setup_type,hd_path,save=True):
        self = Template()
        try:
            self.name = name
            # If no minimum memory given for template, set default one
            self.minimum_memory = minimum_memory or common.default_minimum_memory
            self.operating_system_type = os_type
            self.operating_system_version = os_version
            self.operating_system_distribution = os_distro
            self.virtualization_setup_type = virt_setup_type
            self.hard_disk_setup_type = hd_setup_type
            self.hard_disk_path = hd_path
            self.do_save = save
            if save:
                db.session.add(self)
                db.session.commit()
        except Exception as e:
            raise e
        return self

    def destroy(self):
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            db.session.delete(self)
            db.session.commit()

    def auto_save(self):
        db.session.add(self)
        db.session.commit()

    '''Validators'''
    @validates('hard_disk_setup_type')
    def validate_hard_disk_setup_type(self, key, hd_setup_type):
        try:
            HDSetupTypeClass.validate_hard_disk_setup_type(hd_setup_type)
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

    @validates('virtualization_technology')
    def validate_hypervisor(self, key, virt_tech):
        try:
            VirtTechClass.validate_virt_tech(virt_tech)
            return virt_tech
        except Exception as e:
            raise e
       
    '''Getters and Setters'''
    def get_lock_identifier(self):
        # Uniquely identifies object by a key
        return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)

    def set_name(self, name):
        self.name = name
        self.auto_save()

    def get_name(self):
        return self.name

    def set_memory(self,memory):
        self.memory = memory
        self.auto_save()

    def get_memory(self):
        return self.memory

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

    def get_hard_disk_setup_type(self):
        return self.hd_setup_type

    def set_hard_disk_setup_type(self, hd_type):
        HDSetupTypeClass.validate_hard_disk_setup_type(hd_type)
        self.hd_setup_type = hd_type
        self.auto_save()

    def get_hard_disk_origin_path(self):
        return  self.hd_setup_type

    def set_hard_disk_origin_path(self, path):
        self.hd_origin_path = path
        self.auto_save()

    def get_virtualization_setup_type(self):
        return self.virtualization_setup_type

    def set_virtualization_setup_type(self,v_type):
        VirtTypeClass.validate_virt_type(v_type)
        self.virtualization_setup_type = v_type
        self.auto_save()

    def set_virtualization_technology(self, virt_tech):
        VirtTechClass.validate_virt_tech(virt_tech)
        self.virtualization_technology = virt_tech
        self.auto_save()

    def get_virtualization_technology(self):
        return self.virtualization_technology
