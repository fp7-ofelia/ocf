from models.resources.ip4slot import Ip4Slot
from models.resources.macslot import MacSlot
from sqlalchemy.dialects.mysql import TINYINT, BIGINT
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from utils import validators
from utils.base import db
from utils.mutexstore import MutexStore
import amsoil.core.log
import amsoil.core.pluginmanager as pm
import inspect

logging=amsoil.core.log.getLogger('NetworkInterface')

'''@author: msune, SergioVidiella'''

class NetworkInterface(db.Model):
    """Network interface model."""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'networkinterface'

    '''Generic parameters'''
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    name = db.Column(db.String(128), nullable=False, default="")
    mac_id = db.Column(db.ForeignKey(table_prefix + 'macslot.id'), nullable=False, index=True)
    mac = db.relationship("MacSlot", backref="networkInterface", uselist=False, lazy='dynamic')
    ip4s = association_proxy("networkinterface_ip4s", "ip4slot", creator=lambda ip:NetworkInterfaceIp4s(ip4slot=ip))
    is_mgmt = db.Column("isMgmt", TINYINT(1), nullable=False, default=0)
    is_bridge = db.Column("isBridge", TINYINT(1), nullable=False, default=0)

    '''Interfaces connectivy'''
    vtserver = association_proxy("vtserver_assocation", "vtserver")
    vm = association_proxy("vm_associations", "vm")
    connected_to = association_proxy("to_network_interface", "to_networkinterface", creator=lambda iface:NetworkInterfaceConnectedTo(to_networkinterface=iface))
    connected_from = association_proxy("from_network_interface", "from_networkinterface", creator=lambda iface:NetworkInterfaceConnectedTo(from_networkinterface=iface))

    '''Physical connection details for bridged interfaces''' 
    switch_id = db.Column("switchID", db.String(23), nullable=True, default="")
    port = db.Column(db.Integer, nullable=True)
    id_form = db.Column("idForm", db.Integer, nullable=True)

    '''Defines soft or hard state of the VM'''
    do_save = False


    '''Interface constructor '''
    @staticmethod
    def constructor(name,mac_str,mac_obj,switch_id,port,ip4_obj,is_mgmt=False,is_bridge=False,save=True):
        logging.debug("******************************* I1")
        self = NetworkInterface()
        try:
            logging.debug("******************************* I2 " + name + str(mac_obj) + ' ' + str(self.mac))
            self.name = name
            if mac_obj == None:
                logging.debug("******************************* I3 - 1")
                self.mac = MacSlot.mac_factory(None,mac_str)
            else:
                logging.debug("******************************* I3 - 2")
                if not isinstance(mac_obj,MacSlot):
                    logging.debug("******************************* I - ERROR - 1")
                    raise Exception("Cannot construct NetworkInterface with a non MacSlot object as parameter")
                logging.debug("******************************* I4 " + str(mac_obj) + ' ' + str(type(mac_obj)))
                logging.debug("************************************ YEAH")
                logging.debug("************************************ YEAH")
                self.mac.append(mac_obj)
            logging.debug("******************************* I5 " + str(self.mac))
            self.is_mgmt = is_mgmt
            logging.debug("******************************* I6")            
            '''Connectivity'''
            if is_bridge:
                logging.debug("******************************* I7 - 1")
                self.is_bridge = is_bridge
                self.switch_id = switch_id
                self.port = port
            logging.debug("******************************* I7 " + str(self.mac))
            if not ip4_obj == None:
                logging.debug("******************************* I7 - 2")
                if not isinstance(ip4_obj,Ip4Slot):
                    logging.debug("******************************* I - ERROR - 2")
                    raise Exception("Cannot construct NetworkInterface with a non Ip4Slot object as parameter")
                else:
                    logging.debug("******************************* I7 - 3")
                    db.session.add(self)
                    db.session.commit()
                    self.ip4s.append(ip4_obj)
                    logging.debug("****************************** I7 - 4 " + str(ip4_obj.id) + ' ' + str(self.id))
            self.do_save = save
            if save:
                db.session.add(self)
                db.session.commit()
        except Exception as e:
            logging.debug("******************************* I - ERROR - 3")
            raise e
        logging.debug("******************************* I8")
        return self
    
    def update(self, name, mac_str, switch_id, port):
        try:
            self.name = name
            self.set_mac_str(mac_str)
            self.switch_id = switch_id
            self.port = port
            if save:
                self.auto_save()
        except Exception as e:
            raise e
    
    ''' Private methods '''
    def auto_save(self):
        if self.do_save:
            db.session.add(self)
            db.session.commit()
    
    ''' Public methods '''
    def get_lock_identifier(self):
        # Uniquely identifies object by a key
        return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)
    
    def get_name(self):
        return self.name
    
    def set_name(self,name):
        self.name=name
        self.auto_save()
    
    def get_mac_str(self):
        return self.mac.first().mac
    
    def set_mac_str(self,mac_str):
        self.mac.first().set_mac(mac_str)
        self.autosave()
    
    def set_port(self,port):
        self.port = port
        self.auto_save()
    
    def get_port(self):
        return self.port
    
    def set_switch_id(self, switch_id):
        self.switch_id = switch_id
        self.auto_save()
    
    def get_switch_id(self):
        return self.switch_id
    
    def set_is_mgmt(self, is_mgmt):
        self.is_mgmt = is_mgmt
        self.auto_save()
    
    def get_is_mgmt(self):
        return self.is_mgmt
    
    def get_number_of_connections(self):
        return len(self.connected_from)
    
    def attach_interface_to_bridge(self,interface):
        logging.debug("*********************************** BRIDGE 1")
        if not self.is_bridge:
            logging.debug("*********************************** BRIDGE ERROR - 1")
            raise Exception("Cannot attach interface to a non-bridged interface")
        if not isinstance(interface,NetworkInterface):
            logging.debug("*********************************** BRIDGE ERROR - 2")
            raise Exception("Cannot attach interface; object type unknown -> Must be NetworkInterface instance")
        logging.debug("*********************************** BRIDGE 2 " + str(interface.id) + ' ' + str(self.id))
        self.connected_from.append(interface)
        self.auto_save()
        logging.debug("*********************************** BRIDGE 3 " + str(interface.connected_from))
    
    def detach_interface_to_bridge(self,interface):
        if not self.is_bridge:
            raise Exception("Cannot detach interface from a non-bridged interface")
        if not isinstance(interface,NetworkInterface):
            raise Exception("Cannot detach interface; object type unknown -> Must be NetworkInterface instance")
        self.connected_from.remove(interface)
        self.auto_save()
    
    def add_ip4_to_interface(self,ip4):
        if not self.is_mgmt:
            raise Exception("Cannot add IP4 to a non mgmt interface")
        if not isinstance(ip4,Ip4Slot):
            raise Exception("Cannot add IP4 to interface; object type unknown -> Must be IP4Slot instance")
        self.ip4s.append(ip4)
        self.auto_save()
    
    def remove_ip4_from_interface(self,ip4):
        if not isinstance(ip4,Ip4Slot):
            raise Exception("Cannot remove IP4 to interface; object type unknown -> Must be IP4Slot instance")
        if not self.is_mgmt:
            raise Exception("Cannot add IP4 to a non mgmt interface")
        self.ip4s.remove(ip4)
        self.auto_save()
    
    def destroy(self):
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            if self.get_number_of_connections():
                raise Exception("Cannot destroy a bridge which has enslaved interfaces")
            for ip in self.ip4s:
                ip.destroy()
            self.mac[0].destroy()
            db.session.delete(self)
            db.session.commit()
    
    '''Validators'''
    @validates('name')
    def validate_name(self, key, name):
        try:
            # XXX: Fails when a name like eth1.999-slave is set, solve this
            # validators.resource_name_validator(name)
            return name
        except Exception as e:
            raise e
    
    @validates('switch_id')
    def validate_switch_id(self, key, switch_id):
        try:
            validators.datapath_validator(switch_id)
            return switch_id
        except Exception as e:
            raise e
    
    @validates('port')
    def validate_port(self, key, port):
        try:
            validators.number_validator(port)
            return port
        except Exception as e:
            raise e
    
    '''Server interface factories'''
    @staticmethod
    def create_server_data_bridge(name, mac_str, switch_id, port, save=True):
        return NetworkInterface.constructor(name, mac_str, None, switch_id, port, None, False, True, save)
    
    @staticmethod
    def update_server_data_bridge(name, mac_str, switch_id, port, save=True):
        return NetworkInterface.update(name, mac_str, switch_id, port, save)
    
    @staticmethod
    def create_server_mgmt_bridge(name, mac_str, save=True):
        return NetworkInterface.constructor(name, mac_str, None, None, None, None, True, True, save)
    
    '''VM interface factories'''
    @staticmethod
    def create_vm_data_interface(name, mac_obj, save=True):
        return NetworkInterface.constructor(name, None, mac_obj, None, None, None, False, False, save)
    
    @staticmethod
    def create_vm_mgmt_interface(name, mac_obj, ip4, save=True):
        return NetworkInterface.constructor(name, None, mac_obj, None, None, ip4, True, False, save)


class NetworkInterfaceIp4s(db.Model):
    """Relation between Network interfaces and Ip's"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'networkinterface_ip4s'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    networkinterface_id = db.Column(db.ForeignKey(table_prefix + 'networkinterface.id'), nullable=False, index=True)
    ip4slot_id = db.Column(db.ForeignKey(table_prefix + 'ip4slot.id'), nullable=False, index=True)

    networkinterface = db.relationship("NetworkInterface", backref=db.backref("networkinterface_ip4s"))
    ip4slot = db.relationship("Ip4Slot", primaryjoin="Ip4Slot.id==NetworkInterfaceIp4s.ip4slot_id", backref=db.backref("networkinterface_associations_ips", cascade="all, delete-orphan"))


class NetworkInterfaceConnectedTo(db.Model):
    """Connections between Network interfaces"""

    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'networkinterface_connectedTo'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    from_networkinterface_id = db.Column(db.ForeignKey(table_prefix + 'networkinterface.id'), nullable=False)
    to_networkinterface_id = db.Column(db.ForeignKey(table_prefix + 'networkinterface.id'), nullable=False)

    to_networkinterface = db.relationship("NetworkInterface", primaryjoin="NetworkInterface.id==NetworkInterfaceConnectedTo.from_networkinterface_id", backref=db.backref("from_network_interface"))
    from_networkinterface = db.relationship("NetworkInterface", primaryjoin="NetworkInterface.id==NetworkInterfaceConnectedTo.to_networkinterface_id", backref=db.backref("to_network_interface", cascade="all, delete-orphan"))

