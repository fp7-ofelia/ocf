from sqlalchemy.orm import validates
from utils.base import db
from utils.mutexstore import MutexStore
from resources.virtualmachine import VirtualMachine
from resources.vmallocated import VMAllocated
from resources.vtserver import VTServer
import common
import amsoil.core.pluginmanager as pm
import inspect

'''
   @author: SergioVidiella
   @author: OscarMoya
'''

class Template(db.Model):
    """Templates for the VMs disc images supported."""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'template'

    '''General parameters'''
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(512), nullable=False, default="")
    uuid = db.Column(db.String(1024), nullable=False)
    description = db.Column(db.String(1024), nullable=True)

    '''OS parameters'''
    operating_system_type = db.Column(db.String(512), nullable=False, default="")
    operating_system_version = db.Column(db.String(512), nullable=False, default="")
    operating_system_distribution = db.Column(db.String(512), nullable=False, default="")

    '''Virtualization parameteres'''
    virtualization_setup_type = db.Column(db.String(1024),nullable=False,default="")
    hard_disk_setup_type = db.Column(db.String(1024), nullable=False, default="")
    hard_disk_path = db.Column(db.String(1024), nullable=False, default="")
    
    '''Metadata'''
    metadata = db.Column(db.String(4096), nullable=True)

    '''Deployment procedures'''
    img_file_url = db.Column(db.String(1024), nullable=True)

    ''' Mutex over the instance '''
    mutex = None

    '''Defines soft or hard state of the Template'''
    do_save = True

    servers = association_proxy("vtserver_templates", "vtserver")
    allocated_vms = association_proxy("virtualmachine_allocated_template", "vmallocated")
    vms = association_proxy("virtualmachine_template", "virtualmachine")
    

    def __init__(name="",description="",os_type="",os_version="",os_distro="",virt_setup_type="",hd_setup_type="",hd_path="",metadata=None,img_url="", save=True):
        self.name = name
        self.description = description
        self.operating_system_type = os_type
        self.operating_system_version = os_version
        self.operating_system_distribution = os_distro
        self.virtualization_setup_type = virt_setup_type
        self.hard_disk_setup_type = hd_setup_type
        self.hard_disk_path = hd_path
        self.metadata = metadata
        self.img_file_url = img_url
        self.do_save = save
        if self.do_save:
            self.auto_save()

    def destroy(self):
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            db.session.delete(self)
            db.session.commit()

    def auto_save(self):
        if self.do_save():
            db.session.add(self)
            db.session.commit()

       
    '''Getters and Setters'''
    
    def set_do_save(self, boolean):
        self.do_save = boolean
        self.auto_save

    def get_do_save(self):
        return self.do_save

    def get_lock_identifier(self):
        # Uniquely identifies object by a key
        return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)

    def set_name(self, name):
        self.name = name
        self.auto_save()

    def get_name(self):
        return self.name

    def set_description(self, desc):
        self.description = desc
        self.auto_save()

    def get_description(self):
        return self.description

    def set_os_type(self, type):
        self.operating_system_type = type
        self.auto_save()

    def get_os_type(self):
        return self.operating_system_type

    def set_os_version(self, version):
        self.operating_system_version = version
        self.auto_save()

    def get_os_version(self):
        return self.operating_system_version

    def set_os_distribution(self, dist):
        self.operating_system_distribution = dist
        self.auto_save()

    def get_os_distribution(self):
        return self.operating_system_distribution

    def get_hard_disk_setup_type(self):
        return self.hd_setup_type

    def set_hard_disk_setup_type(self, hd_type):
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
        self.virtualization_setup_type = v_type
        self.auto_save()

    def set_virtualization_technology(self, virt_tech):
        self.virtualization_technology = virt_tech
        self.auto_save()

    def get_virtualization_technology(self):
        return self.virtualization_technology
    
    def get_raw_metadata(self):
        return self.metadata

    def set_metadata(self, metadata):
        self.metadata = metadata
        self.auto_save()

    def get_img_file_url(self):
        return self.img_file_url
  
    def set_img_file_url(self, url):
        self.img_file_url = url
        self.auto_save()

