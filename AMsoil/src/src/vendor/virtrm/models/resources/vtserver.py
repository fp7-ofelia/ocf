from models.interfaces.networkinterface import NetworkInterface
from models.ranges.ip4range import Ip4Range
from models.ranges.macrange import MacRange
from sqlalchemy import desc
from sqlalchemy.dialects.mysql import TINYINT, DOUBLE, VARCHAR
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from utils import validators
from utils.base import db
from utils.choices import VirtTechClass, OSDistClass, OSVersionClass, OSTypeClass
from utils.mutexstore import MutexStore
import amsoil.core.log
import amsoil.core.pluginmanager as pm
import inspect
import uuid

logging=amsoil.core.log.getLogger('VTServer')

'''@author: msune, SergioVidiella'''

def validate_agent_url_wrapper(url):
        VTServer.validate_agent_url(url)

class VTServer(db.Model):
    """Virtualization Server Class."""

    config = pm.getService("config")
    __tablename__ = config.get("virtrm.DATABASE_PREFIX") + 'vtserver'

    __child_classes = (
    'XenServer',
       )
    
    '''General attributes'''
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    available = db.Column(TINYINT(1), nullable=False, default=1)
    enabled = db.Column(TINYINT(1), nullable=False, default=1)
    name = db.Column(VARCHAR(length=511), nullable=False, default="")
    uuid = db.Column(db.String(1024), nullable=False, default=uuid.uuid4())

    '''OS'''
    operating_system_type = db.Column("operatingSystemType", db.String(512), nullable=False)
    operating_system_distribution = db.Column("operatingSystemDistribution", db.String(512), nullable=False)
    operating_system_version = db.Column("operatingSystemVersion", db.String(512), nullable=False)

    '''Virtualization Technology'''
    virtualization_technology = db.Column("virtTech", db.String(512), nullable=False)

    ''' Hardware '''
    cpus_number = db.Column("numberOfCPUs", db.Integer)
    cpu_frequency = db.Column("CPUFrequency", db.Integer)
    virtual_memory_mb = db.Column("memory", db.Integer)
    hard_disk_space_gb = db.Column("discSpaceGB", DOUBLE)

    '''Agent Fields'''
    agent_url = db.Column("agentURL", db.String(200))
    agent_password = db.Column("agentPassword", db.String(128))
    url = db.Column(db.String(200))

    '''Network interfaces'''
    network_interfaces = association_proxy("vtserver_networkinterface", "networkinterface", creator=lambda iface:VTServerNetworkInterfaces(networkinterface=iface))

    '''Other networking parameters'''
    subscribed_mac_ranges = association_proxy("vtserver_mac_range", "subscribed_mac_range", creator=lambda mac_range:VTServerMacRange(subscribed_mac_range=mac_range))
    subscribed_ip4_ranges = association_proxy("vtserver_ip4_range", "subscribed_ip4_range", creator=lambda ip4_range:VTServerIp4Range(subscribed_ip4_range=ip4_range))

    ''' Mutex over the instance '''
    mutex = None
    
    '''Defines soft or hard state of the Server'''
    do_save = False
    
    '''Validators'''
    @validates('name')
    def validate_name(self, key, name):
        try:
            validators.resource_name_validator(name)
            return name
        except Exception as e:
            raise e
    
    @validates('operating_system_type')
    def validate_operating_system_type(self, key, os_type):
        try:
            OSTypeClass.validate_os_type(os_type)
            return os_type
        except Exception as e:
            raise e
    
    @validates('operating_system_distribution')
    def validate_operating_system_distribution(self, key, os_distribution):
        try:
            OSDistClass.validate_os_dist(os_distribution)
            return os_distribution
        except Exception as e:
            raise e
    
    @validates('operating_system_version')
    def validate_operating_system_version(self, key, os_version):
        try:
            OSVersionClass.validate_os_version(os_version)
            return os_version
        except Exception as e:
            raise e
    
    @validates('virtualization_technology')
    def validate_virtualization_technology(self, key, virt_tech):
        try:
            VirtTechClass.validate_virt_tech(virt_tech)
            return virt_tech
        except Exception as e:
            raise e
    
    @validates('agent_url')
    def validate_agent_url(self, key, agent_url):
        try:
            validate_agent_url_wrapper(agent_url)
            return agent_url
        except Exception as e:
            raise e
    
    @validates('agent_password')
    def validate_agent_password(self, key, agent_password):
        try:
            validators.resource_name_validator(agent_password)
            return agent_password
        except Exception as e:
            raise e
    
    '''Private methods'''
    def get_child_object(self):
        for child_class in self.__child_classes:
            try:
                return self.__getattribute__(child_class.lower())[0]
            except Exception as e:
                raise e
            
    def __tupleContainsKey(tu,key):
        for val in tu:
            if val[0] == key:
                return True
        return False
    
    def auto_save(self):
        if self.do_save:
            db.session.add(self)
            db.session.commit()   
    
    def get_lock_identifier(self):
        # Uniquely identifies object by a key
        return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)
    
    def destroy(self):
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            if len(self.vms.all())>0:
                raise Exception("Cannot destroy a server which hosts VMs. Delete VMs first")
            # Delete associated interfaces
            for interface in self.network_interfaces.all():
                interface.destroy()
            # Delete instance
            db.session.delete(self)
            db.session.commit()
    
    '''Getters and Setters'''
    def set_name(self, name):
        self.name = name
        self.auto_save()
    
    def get_name(self):
        return self.name
        
    def set_uuid(self, uuid):
        self.uuid = uuid
        self.auto_save()
        
    def get_uuid(self):
        return self.uuid
    
    def set_virtual_memory_mb(self,memory):
        self.virtual_memory_mb = memory
        self.auto_save()
    
    def get_virtual_memory_mb(self):
        return self.virtual_memory_mb
    
    def set_agent_url(self, url):
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            VTServer.validate_agent_url(url)
            self.agent_url = url
            self.auto_save()
         
    def get_agent_url(self):
        return self.agent_url
       
    def set_url(self, url):
        self.url = url
        self.auto_save()
      
    def get_url(self):
        return self.url
        
    def set_virtualization_technology(self, virt_tech):
        self.virtualization_technology = virt_tech
        self.auto_save()
        
    def get_virtualization_technology(self):
        return self.virtualization_technology
    
    def set_operating_system_type(self, os_type):
        self.operating_system_type = os_type
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
    
    def set_available(self,av):
        self.available = av
        self.auto_save()
        
    def get_available(self):
        return self.available
    
    def set_enabled(self,en):
        self.enabled = en
        self.auto_save()
        
    def get_enabled(self):
        return self.enabled
    
    def set_cpus_number(self, num):
        self.number_of_cpus = num
        self.auto_save()
    
    def get_cpus_number(self):
        return self.number_of_cpus
    
    def set_cpu_frequency(self, frequency):
        self.cpu_frequency = frequency
        self.auto_save()
    
    def get_cpu_frequency(self):
        return self.cpu_frequency
    
    def set_hard_disk_space_gb(self, disc_space):
        self.disc_space_gb = disc_space
        self.auto_save()
    
    def get_hard_disk_space_gb(self):
        return self.disc_space_gb
    
    def get_agent_password(self):
        return self.agent_password
    
    def set_agent_password(self, password):
        self.agent_password = password
        self.auto_save()

    def get_allocated_vms(self):
        return self.allocated_vms

    def set_allocated_vms(self, vm):
        self.allocated_vms.append(vm)
        self.auto_save() 
    
    ''' Ranges '''
    def subscribe_to_mac_range(self,new_range):
        if not isinstance(new_range,MacRange):
            raise Exception("Invalid instance type on subscribeToMacRange; must be MacRange")
        if new_range in self.subscribed_mac_ranges.all():
            raise Exception("Server is already subscribed to this range")
        self.subscribed_mac_ranges.append(new_range)
        self.auto_save()
    
    def unsubscribe_to_mac_range(self,o_range):
        if not isinstance(o_range,MacRange):
            raise Exception("Invalid instance type on unsubscribeToMacRange; must be MacRange")
        self.subscribed_mac_ranges.remove(o_range)
        self.auto_save()
    
    def get_subscribed_mac_ranges_no_global(self):
        return self.subscribed_mac_ranges
    
    def get_subscribed_mac_ranges(self):
        if len(self.subscribed_mac_ranges) > 0:
            return self.subscribed_mac_ranges
        else:
            # Return global (all) ranges
            return MacRange.query.filter_by(is_global=True).all()
    
    def subscribe_to_ip4_range(self,new_range):
        if not isinstance(new_range,Ip4Range):
            raise Exception("Invalid instance type on subscribeToIpRange; must be Ip4Range")
        if new_range in self.subscribed_ip4_ranges:
            raise Exception("Server is already subscribed to this range")
        self.subscribed_ip4_ranges.append(new_range)
        self.auto_save()
    
    def unsubscribe_to_ip4_range(self,o_range):
        if not isinstance(o_range,Ip4Range):
            raise Exception("Invalid instance type on unsubscribeToIpRange; must be Ip4Range")
        self.subscribed_ip4_ranges.remove(o_range)
        self.auto_save()
    
    def get_subscribed_ip4_ranges_no_global(self):
        return self.subscribed_ip4_ranges
    
    def get_subscribed_ip4_ranges(self):
        if len(self.subscribed_ip4_ranges) > 0:
            return self.subscribed_ip4_ranges
        else:
            # Return global (all) ranges
            return Ip4Range.query.filter_by(is_global=True).all()
    
    def __allocate_mac_from_subscribed_ranges(self):
        logging.debug("************************* MAC 1")
        mac_obj = None
        # Allocate Mac
        for mac_range in self.get_subscribed_mac_ranges():
            logging.debug("*********************** MAC 2")
        #    try:
            mac_obj = mac_range.allocate_mac()
         #   except Exception as e:
         #       logging.debug("******************** MAC ERROR 1 " + str(e))
         #       continue
            break
        if mac_obj == None:
            logging.debug("********************* MAC ERROR 2 " + str(e))
            raise Exception("Could not allocate Mac address for the VM over subscribed ranges")
        logging.debug("*************************** MAC 3")
        return mac_obj

    def __allocate_ip_from_subscribed_ranges(self):
        logging.debug("*********************** IP 1")
        ip_obj = None
        # Allocate Ip
        for ip_range in self.get_subscribed_ip4_ranges():
            logging.debug("*********************** IP 2 " + str(ip_range))
            try:
                logging.debug("*********************** IP 3")
                ip_obj = ip_range.allocate_ip()
            except Exception as e:
                logging.debug("*********************** IP ERROR " + str(e))
                continue
            break
        logging.debug("*********************** IP 4")
        if ip_obj == None:
            logging.debug("*********************** IP ERROR 2")
            raise Exception("Could not allocate Ip4 address for the VM over subscribed ranges")
        logging.debug("*********************** IP 5")
        return ip_obj
    
    ''' VM interfaces and VM creation methods '''
    def __create_enslaved_data_vm_network_interface(self, server_interface):
        # Obtain
        logging.debug("******************** A1") 
        mac_obj = self.__allocate_mac_from_subscribed_ranges()
        logging.debug("******************** A2")
        interface = NetworkInterface.create_vm_data_interface(server_interface.get_name()+"-slave",mac_obj)
        # Enslave it     
        logging.debug("******************* A3")
        server_interface.attach_interface_to_bridge(interface)
        logging.debug("********************* A4")
        return interface
    
    def __create_enslaved_mgmt_vm_network_interface(self, server_interface):
        # Obtain 
        logging.debug("*********************** A1")
        mac_obj = self.__allocate_mac_from_subscribed_ranges()
        logging.debug("*********************** A2")
        ip_obj = self.__allocate_ip_from_subscribed_ranges()
        logging.debug("*********************** A3")
        interface = NetworkInterface.create_vm_mgmt_interface(server_interface.get_name()+"-slave", mac_obj, ip_obj)
        # Enslave it     
        logging.debug("*********************** A4")
        server_interface.attach_interface_to_bridge(interface)
        logging.debug("*********************** A5")
        return interface
    
    def create_enslaved_vm_interfaces(self):
        logging.debug("********************** A")
        vm_interfaces = set()
        logging.debug("********************** B")
        try:
            # Allocate one interface for each Server's interface
            for server_interface in self.network_interfaces:
                logging.debug("********************** C " + str(server_interface))
                if server_interface.is_mgmt:
                    logging.debug("*********************** D1 - 1")
                    try:
                        created_interface = self.__create_enslaved_mgmt_vm_network_interface(server_interface)
                        logging.debug("********************* D1 - 2")
                        vm_interfaces.add(created_interface)
                        logging.debug("********************* D1 - 3 " + str(created_interface) + ' ' + str(vm_interfaces))
                    except Exception as e:
                        logging.debug("********************* CREATION FAIL " + str(e))
                else:
                    logging.debug("*********************** D2")
                    vm_interfaces.add(self.__create_enslaved_data_vm_network_interface(server_interface))
        except Exception as e:
            logging.debug("**************************** VTServer FAIL " + str(e))
            for interface in vm_interfaces:
                interface.destroy()
            raise e
        logging.debug("*************************** E")
        return vm_interfaces
    
    ''' Server interfaces '''
    # Network mgmt bridges
    def set_mgmt_bridge(self,name,mac_str):
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            n_inter = self.network_interfaces.filter_by(is_mgmt=True,is_bridge=True).all()
            if len(nInter) == 1:
                mgmt = n_inter.get()
                mgmt.set_name(name)
                mgmt.set_mac_str(macStr)
            elif len(n_inter) == 0:
                mgmt = NetworkInterface.create_server_mgmt_bridge(name,mac_str)
                self.network_interfaces.append(mgmt)
            else:
                raise Exception("Unexpected length of managment NetworkInterface query")
            self.auto_save()
    
    # Network data bridges
    def add_data_bridge(self,name,mac_str,switch_id,port):
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            if len(self.network_interfaces.filter_by(name=name).filter_by(isBridge=True).all())> 0:
                raise Exception("Another data bridge with the same name already exists in this Server")
            net_int = NetworkInterface.create_server_data_bridge(name,mac_str,switch_id,port)
            self.network_interfaces.append(net_int)
            self.auto_save()
    
    def update_data_bridge(self,interface):
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            if len(self.network_interfaces.filter_by(id = interface.id).all)!= 1:
                raise Exception("Can not update bridge interface because it does not exist or id is duplicated")
            NetworkInterface.update_server_data_bridge(interface.id,interface.get_name(),interface.get_mac_str(),interface.get_switch_id(),interface.get_port())
    
    def delete_data_bridge(self,net_int):
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            if not isinstance(net_int,NetworkInterface):
                raise Exception("Can only delete Data Bridge that are instances of NetworkInterace")
            # TODO: delete interfaces from VMs, for the moment forbid
            if net_int.get_number_of_connections() > 0:
                raise Exception("Cannot delete a Data bridge from a server if this bridge has VM's interfaces ensalved.")
            self.network_interfaces.remove(net_int)
            netInt.destroy()
            self.auto_save()
    
    def get_network_interfaces(self):
        return self.network_interfaces


class VTServerNetworkInterfaces(db.Model):
    """Network interfaces related to a VTServer"""
    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'vtserver_networkInterfaces'
    # Table attributes
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = db.Column(db.ForeignKey(table_prefix + 'vtserver.id'), nullable=False)
    networkinterface_id = db.Column(db.ForeignKey(table_prefix + 'networkinterface.id'), nullable=False)
    # Relationships
    vtserver = db.relationship("VTServer", primaryjoin="VTServer.id==VTServerNetworkInterfaces.vtserver_id", backref=db.backref("vtserver_networkinterface", cascade="all, delete-orphan"))
    networkinterface = db.relationship("NetworkInterface", primaryjoin="NetworkInterface.id==VTServerNetworkInterfaces.networkinterface_id", backref=db.backref("vtserver_assocation", cascade="all, delete-orphan"))


class VTServerIpRange(db.Model):
    """Subscribed IP4 ranges to the VTServer's."""
    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'vtserver_subscribedIp4Ranges'
    # Table attributes
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = db.Column(db.ForeignKey(table_prefix + 'vtserver.id'), nullable=False)
    ip4range_id = db.Column(db.ForeignKey(table_prefix + 'ip4range.id'), nullable=False)
    # Relationships
    vtserver = db.relationship("VTServer", primaryjoin="VTServer.id==VTServerIpRange.vtserver_id", backref=db.backref("vtserver_ip4_range", cascade="all, delete-orphan"))
    subscribed_ip4_range = db.relationship("Ip4Range", primaryjoin="Ip4Range.id==VTServerIpRange.ip4range_id", backref=db.backref("vtserver_association", cascade="all, delete-orphan"))
 

class VTServerMacRange(db.Model):
    """Subscribed Mac ranges to the VTServer's."""
    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'vtserver_subscribedMacRanges'
    # Table attributes
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = db.Column(db.ForeignKey(table_prefix + 'vtserver.id'), nullable=False)
    macrange_id = db.Column(db.ForeignKey(table_prefix + 'macrange.id'), nullable=False)
    # Relationships
    vtserver = db.relationship("VTServer", primaryjoin="VTServer.id==VTServerMacRange.vtserver_id", backref=db.backref("vtserver_mac_range", cascade="all, delete-orphan"))
    subscribed_mac_range = db.relationship("MacRange", primaryjoin="MacRange.id==VTServerMacRange.macrange_id", backref=db.backref("vtserver_association", cascade="all, delete-orphan"))

