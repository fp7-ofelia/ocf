from datetime import datetime, timedelta
from models.common.expires import Expires
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from utils import validators
from utils.base import db
from utils.choices import HDSetupTypeClass, VirtTypeClass, VirtTechClass, OSDistClass, OSVersionClass, OSTypeClass
from utils.mutexstore import MutexStore
import amsoil.core.pluginmanager as pm
import inspect
from models.resources.vtserver import VTServer


'''@author: SergioVidiella'''

class VMAllocated(db.Model):
    """Virtual Machines allocated for GeniV3 calls."""

    config = pm.getService("config")
    __tablename__ = config.get("virtrm.DATABASE_PREFIX") + 'virtualmachine_allocated'

    '''General parameters'''
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(512), nullable=False, default="")
    uuid = db.Column(db.String(1024), nullable=False, default="")
    memory = db.Column(db.Integer)
    number_of_cpus = db.Column(db.Integer, nullable=True)
    disc_space_gb = db.Column(DOUBLE, nullable=True)

    '''Property parameters'''
    project_id = db.Column(db.String(1024), nullable=False, default="")
    project_name = db.Column(db.String(1024), nullable=False, default="")
    slice_id = db.Column(db.String(1024), nullable=False, default="")
    slice_name = db.Column(db.String(512), nullable=False, default="")
    server_id = db.Column(db.ForeignKey(config.get("virtrm.DATABASE_PREFIX") + 'vtserver.id'), nullable=False)
    server = db.relationship("VTServer", backref='allocated_vms')
        
    '''Virtualization parameteres'''
    virtualization_technology = db.Column(db.String(512), nullable=False, default="xen")

    ''' Mutex over the instance '''
    # Mutex
    mutex = None

    '''Defines soft or hard state of the VM'''
    do_save = True

    @staticmethod
    def __init__(self,name="",project_id="",slice_id="",slice_name="",project_name="",server=None,memory=0,disc_space_gb=None,number_of_cpus=None,virt_tech="xen",expires=None,save=False):
        self.name = name 
        self.project_id = project_id
        self.slice_id = slice_id
        self.slice_name = slice_name
        self.project_name = project_name
        self.memory = memory
        self.disc_space_gb = disc_space_gb
        self.number_of_cpus = number_of_cpus
        self.virtualization_technology = virt_tech
        try:
            self.server = server
        except:
            pass
        try:
            self.expires.append(expires)
        except:
            pass
        self.do_save = save
        if save:
            db.session.add(self)
            db.session.commit()
    
    def auto_save(self):
        if self.do_save is True:
            db.session.add(self)
            db.session.commit()
    
    '''Destructor'''
    def destroy(self):
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            db.session.delete(self)
            db.session.commit()
    
    @validates('virtualization_technology')
    def validate_virtualization_technology(self, key, virt_tech):
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
    
    def set_project_id(self,project_id):
        if not isinstance(project_id,str):
            project_id = str(project_id)
        self.project_id = project_id
        self.auto_save()
    
    def get_project_id(self):
        return self.project_id

    def set_project_name(self, project_name):
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
    
    def set_expires(self, expires):
        self.expires.append(expires)
        sel.auto_save()
    
    def get_expires(self):
        return self.expires.first().expires
    
    def set_virtualization_technology(self, virt_tech):
        self.virtualization_technology = virt_tech
        self.auto_save()
    
    def get_virtualization_technology(self):
        return self.virtualization_technology
    
    def set_server(self, server):
        try:
            self.server = server
        except:
            pass
        self.auto_save()
    
    def get_server(self): 
        return self.server

    def set_do_save(self, save):
        self.do_save = save
    
    def get_do_save(self):
        return self.do_save
