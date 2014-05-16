from models.resources.virtualmachine import VirtualMachine
from sqlalchemy.dialects.mysql import TINYINT, DOUBLE
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from utils.base import db
from utils.choices import HDSetupTypeClass, VirtTypeClass
from utils.mutexstore import MutexStore
import amsoil.core.log
import amsoil.core.pluginmanager as pm

logging=amsoil.core.log.getLogger('XenVM')

'''@author: msune, SergioVidiella'''

class XenVM(VirtualMachine):
    """XEN VM data model class"""
    
    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'xenvm'
    __table_args__ = {'extend_existing':True}
    
    '''General Attributes'''
    virtualmachine_ptr_id = db.Column(db.ForeignKey(table_prefix + 'virtualmachine.id'), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity':'xen',
        'inherit_condition':(virtualmachine_ptr_id==VirtualMachine.id)
    }
    hd_setup_type = db.Column("hdSetupType", db.String(1024), nullable=False, default="")
    hd_origin_path = db.Column("hdOriginPath", db.String(1024), nullable=False, default="")
    virtualization_setup_type = db.Column("virtualizationSetupType", db.String(1024), nullable=False, default="")
    vm = db.relationship("VirtualMachine", uselist=False, backref=db.backref("xenvm", cascade = "all, delete-orphan"))
    server = association_proxy("xenserver_associations", "xenserver")
    
    @staticmethod
    def __init__(self,name,uuid,project_id,project_name,slice_id,slice_name,os_type,os_version,os_dist,memory,disc_space_gb,number_of_cpus,callback_url,interfaces,hd_setup_type,hd_origin_path,virt_setup_type,save=True):
        logging.debug("************************************* XENVM 2")
        try:
            self.do_save = False
            # Set common fields
            self.set_name(name)
            logging.debug("******************************** XENVM - NAME IS %s" % name)
            self.set_uuid(uuid)
            logging.debug("******************************** XENVM - UUID IS %s" % uuid)
            self.set_project_id(project_id)
            self.set_project_name(project_name)
            self.set_slice_id(slice_id)
            self.set_slice_name(slice_name)
            self.set_os_type(os_type)
            self.set_os_version(os_version)
            self.set_os_distribution(os_dist)
            self.set_memory_mb(memory)
            self.set_disc_space_gb(disc_space_gb)
            self.set_number_of_cpus(number_of_cpus)
            self.set_callback_url(callback_url)
            self.set_state(self.UNKNOWN_STATE)
            self.type = "xen"
            logging.debug("************************************* XENVM 3")
            for interface in interfaces:
                logging.debug("************************************* XENVM 4")
                self.network_interfaces.append(interface)
            # Xen parameters
            self.hd_setup_type = hd_setup_type
            self.hd_origin_path = hd_origin_path
            self.virtualization_setup_type = virt_setup_type
            self.do_save = save
            if save:
                db.session.add(self)
                db.session.commit()
        except Exception as e:
            logging.debug("************************************* XENVM ERROR - 1 " + str(e))
            print e
            raise e
    
    '''Destructor'''
    def destroy(self):
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            # Destroy interfaces
            for inter in self.network_interfaces:
                inter.destroy()
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
    
    ''' Getters and setters '''
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
    
    def get_server(self):
        return self.xenserver[0]
    
    ''' Factories '''
    @staticmethod
    def create(name,uuid,project_id,project_name,slice_id,slice_name,os_type,os_version,os_dist,memory,disc_space_gb,number_of_cpus,callback_url,interfaces,hd_setup_type,hd_origin_path,virt_setup_type,save):
        logging.debug("************************************* XENVM 1")
        xen_vm =  XenVM(name,uuid,project_id,project_name,slice_id,slice_name,os_type,os_version,os_dist,memory,disc_space_gb,number_of_cpus,callback_url,interfaces,hd_setup_type,hd_origin_path,virt_setup_type,save)
        return xen_vm
