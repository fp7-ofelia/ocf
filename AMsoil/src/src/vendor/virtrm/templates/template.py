from sqlalchemy.orm import validates
from utils.base import db
from utils.mutexstore import MutexStore
from models.resources.virtualmachine import VirtualMachine
from models.resources.vmallocated import VMAllocated
from models.resources.vtserver import VTServer
import common
import amsoil.core.pluginmanager as pm
import inspect
from sqlalchemy.ext.associationproxy import association_proxy
from templates.extendeddata import ExtendedData
import uuid

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
    uuid = db.Column(db.String(1024), nullable=False, default ="")
    description = db.Column(db.String(1024), nullable=True)

    '''OS parameters'''
    operating_system_type = db.Column(db.String(512), nullable=False, default="")
    operating_system_version = db.Column(db.String(512), nullable=False, default="")
    operating_system_distribution = db.Column(db.String(512), nullable=False, default="")

    '''Virtualization parameteres'''
    virtualization_type = db.Column(db.String(128),nullable=False,default="")
    virtualization_technology = db.Column(db.String(128),nullable=False,default="")
    
    ''' HD '''
    hard_disk_setup_type = db.Column(db.String(1024), nullable=False, default="")
    hard_disk_origin_path = db.Column(db.String(1024), nullable=False, default="")
    
    '''Metadata'''
    extended_data = db.Column(db.String(4096), nullable=True)

    '''Deployment procedures'''
    img_file_url = db.Column(db.String(1024), nullable=True)

    ''' Mutex over the instance '''
    mutex = None

    '''Defines soft or hard state of the Template'''
    do_save = True

    servers = association_proxy("vtserver_templates", "vtserver", creator=lambda server:ServerTemplates(vtserver=server))
    allocated_vms = association_proxy("virtualmachine_allocated_template", "vmallocated", creator=lambda vm:VMAllocatedTemplate(vmallocated=vm))
    vms = association_proxy("virtualmachine_template", "virtualmachine", creator=lambda vm:VMTemplate(virtualmachine=vm))

    def __init__(self,name="",description="",os_type="",os_version="",os_distro="",virt_type="",hd_setup_type="",hd_path="",extended_data=None,img_url="",virt_tech="" ,save=False):
        self.name = name
        self.description = description
        self.operating_system_type = os_type
        self.operating_system_version = os_version
        self.operating_system_distribution = os_distro
        self.virtualization_type = virt_type
        self.hard_disk_setup_type = hd_setup_type
        self.hard_disk_origin_path = hd_path
        self.extended_data = extended_data
        self.img_file_url = img_url
        self.virtualization_technology = virt_tech
        self.do_save = save
        self.uuid = str(uuid.uuid4())
        self.extended_data_manager = ExtendedData()
        if extended_data:
           try:
               self.extended_data_manager = self.extended_data_manager.deserialize(extended_data)
           except:
               pass
        if self.do_save:
            self.auto_save()

    def destroy(self):
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            db.session.delete(self)
            db.session.commit()

    def auto_save(self):
        if self.do_save:
            db.session.add(self)
            db.session.commit()

    def add_extension(self, name, value):
        self.extended_data_manager.add_extension(name,value)
        if self.get_do_save():
            serialized_extensions = self.extended_data_manager.serialize()
            self.extended_data = serialized_extensions
            self.auto_save()

    def remove_extension(self, name):
        self.extended_data_manager.remove_extension(name)
        if self.get_do_save():
            serialized_extensions = self.extended_data_manager.serialize()
            self.extended_data = serialized_extensions
            self.auto_save()
       
    '''Getters and Setters'''

    def get_uuid(self):
        return self.uuid
    
    def set_do_save(self, boolean):
        self.do_save = boolean
        self.auto_save

    def get_do_save(self):
        return self.do_save

    def __get_lock_identifier(self):
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

    def set_operating_system_type(self, type):
        self.operating_system_type = type
        self.auto_save()

    def get_operating_system_type(self):
        return self.operating_system_type

    def set_operating_system_version(self, version):
        self.operating_system_version = version
        self.auto_save()

    def get_operating_system_version(self):
        return self.operating_system_version

    def set_operating_system_distribution(self, dist):
        self.operating_system_distribution = dist
        self.auto_save()

    def get_operating_system_distribution(self):
        return self.operating_system_distribution

    def get_hard_disk_setup_type(self):
        return self.hard_disk_setup_type

    def set_hard_disk_setup_type(self, hd_type):
        self.hard_disk_setup_type = hd_type
        self.auto_save()

    def get_hard_disk_origin_path(self):
        return  self.hard_disk_origin_path

    def set_hard_disk_origin_path(self, path):
        self.hard_disk_origin_path = path
        self.auto_save()

    def get_virtualization_type(self):
        return self.virtualization_type

    def set_virtualization_type(self,v_type):
        self.virtualization_type = v_type
        self.auto_save()

    def set_virtualization_technology(self, virt_tech):
        self.virtualization_technology = virt_tech
        self.auto_save()

    def get_virtualization_technology(self):
        return self.virtualization_technology
    
    def get_extended_data(self):
        try:
            ed = self.extended_data_manager.deserialize(self.extended_data)
            return ed.dump()
        except:
            return self.extended_data

    def set_extended_data(self, extended_data):
        self.extended_data = extended_data
        self.auto_save()

    def get_img_file_url(self):
        return self.img_file_url
  
    def set_img_file_url(self, url):
        self.img_file_url = url
        self.auto_save()

    def __repr__(self):
        return "<Template: %s with uuid: %s>" %(self.get_name(),self.get_uuid())

    def __eq__(self,obj):
        if not isinstance(obj, Template):
            print 1
            return False
        if not self.get_uuid() == obj.get_uuid():
            print 2
            return False
        if not self.get_name() == obj.get_name():
            print 3
            return False
        if not self.get_description() == obj.get_description():
            print 4
            return False
        if not self.get_operating_system_type() == obj.get_operating_system_type():
            print 5
            return False
        if not self.get_operating_system_distribution() == obj.get_operating_system_distribution():
            print 6
            return False
        if not self.get_operating_system_version() == obj.get_operating_system_version():
            print 7
            return False
        if not self.get_hard_disk_setup_type() == obj.get_hard_disk_setup_type():
            print 8
            return False
        if not self.get_hard_disk_origin_path() == obj.get_hard_disk_origin_path():
            print 9
            return False
        if not self.get_virtualization_type() == obj.get_virtualization_type():
            print 10
            return False
        if not self.get_virtualization_technology() == obj.get_virtualization_technology():
            print 11
            return False
        if not self.get_img_file_url() == obj.get_img_file_url():
            print 12
            return False
        return True 
       

class VMAllocatedTemplate(db.Model):
    """Relation between Servers and their supported Templates"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'virtualmachine_allocated_template'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    virtualmachine_allocated_uuid = db.Column(db.Integer, db.ForeignKey(table_prefix + 'virtualmachine_allocated.uuid'), nullable=False)
    template_uuid = db.Column(db.Integer, db.ForeignKey(table_prefix + 'template.uuid'), nullable=False)

    template = db.relationship("Template", backref=db.backref("vmallocated_template", cascade = "all, delete-orphan"))
    vmallocated = db.relationship("VMAllocated")


class VMTemplate(db.Model):
    """Relation between Servers and their supported Templates"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'virtualmachine_template'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    virtualmachine_uuid = db.Column(db.Integer, db.ForeignKey(table_prefix + 'virtualmachine.uuid'), nullable=False)
    template_uuid = db.Column(db.Integer, db.ForeignKey(table_prefix + 'template.uuid'), nullable=False)

    template = db.relationship("Template", backref=db.backref("virtualmachine_template", cascade = "all, delete-orphan"))
    virtualmachine = db.relationship("VirtualMachine")


class ServerTemplates(db.Model):
    """Relation between Servers and their supported Templates"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'vtserver_templates'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_uuid = db.Column(db.Integer, db.ForeignKey(table_prefix + 'vtserver.uuid'), nullable=False)
    template_uuid = db.Column(db.Integer, db.ForeignKey(table_prefix + 'template.uuid'), nullable=False)

    template = db.relationship("Template", backref=db.backref("vtserver_templates", cascade = "all, delete-orphan"))
    vtserver = db.relationship("VTServer")
 
