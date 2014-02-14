from models.resources.macslot import MacSlot
from sqlalchemy.dialects.mysql import TINYINT, BIGINT
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from utils.base import db
from utils.ethernetutils import EthernetUtils
from utils.mutexstore import MutexStore
import amsoil.core.log
import amsoil.core.pluginmanager as pm
import inspect

logging=amsoil.core.log.getLogger('MacRange')

'''@author: msune, SergioVidiella'''

class MacRange(db.Model):
    """MacRange."""
   
    config = pm.getService("config")
    __tablename__ = config.get("virtrm.DATABASE_PREFIX") + 'macrange'
    __table_args__ = {'extend_existing':True}

    id = db.Column(db.Integer, autoincrement=True, nullable=False,primary_key=True)
    # Range name
    name = db.Column(db.String(255), nullable=False, unique=True)
    is_global = db.Column("isGlobal", TINYINT(1), nullable=False)
    # Range parameters
    start_mac = db.Column("startMac", db.String(17), nullable=False)
    end_mac = db.Column("endMac", db.String(17), nullable=False)
    # Pool of resources both assigned and excluded (particular case of assignment)
    # Associated MACs for this range
    resources = association_proxy("macrange_macslot", "macslot")
    next_available_mac = db.Column("nextAvailableMac", db.String(17))
    # Statistics
    number_slots = db.Column("numberOfSlots", BIGINT(20))
    # Defines soft or hard state of the range 
    do_save = True
    
    def constructor(name, start_mac, end_mac, is_global=True, save=True):
        self = MacRange()
        try:
            # Default constructor
            EthernetUtils.check_valid_mac(start_mac)
            EthernetUtils.check_valid_mac(end_mac) 
            self.start_mac = start_mac.upper()
            self.end_mac = end_mac.upper()
            self.name = name
            self.is_global= is_global
            # Create an iterator
            it = EthernetUtils.getMacIterator(self.start_mac,self.end_mac)
            self.next_available_mac = it.getNextMac()
            # Number of Slots
            try:
                self.number_slots = EthernetUtils.getNumberOfSlotsInRange(start_mac,end_mac)
            except Exception as e:
                print "Exception doing slot calculation"+str(e)
                self.number_slots = -1
            do_save = save
            if save:
                db.session.add(self)
                db.session.commit()
        except Exception as e:
            print e
            raise e
        return self
    
    '''Validators'''
    @validates('start_mac')
    def validate_start_mac(self, key, mac):
        try:
            EthernetUtils.check_valid_mac(mac)
            return mac
        except Exception as e:
            raise e

    @validates('end_mac')
    def validate_end_mac(self, key, mac):
        try:
            EthernetUtils.check_valid_mac(mac)
            return mac
        except Exception as e:
            raise e

    '''Private methods'''
    def autosave(self):
        if self.do_save:
            db.session.add(self)
            db.session.commit()
    
    def __set_start_mac(self, value):
        EthernetUtils.check_valid_mac(value)
        self.start_mac = value.upper()
        self.autosave()

    def __set_end_mac(self, value):
        EthernetUtils.check_valid_mac(value)
        self.end_mac = value.upper()
        self.autosave()

    def __is_mac_available(self, mac):
        return len(self.resources.filter_by(mac=mac).all()) == 0

    '''Public methods'''
    def get_lock_identifier(self):
        # Uniquely identifies object by a key
        return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)
    
    def get_name(self):
        return self.name
    
    def get_is_global(self):
        return self.is_global
    
    def get_start_mac(self):
        return self.start_mac
        
    def get_end_mac(self):
        return self.end_mac
        
    def get_excluded_macs(self):
        return self.resources.filter_by(is_excluded=True).order_by(MacSlot.mac).all()
    
    def get_allocated_macs(self):
        return self.resources.filter_by(is_excluded=False).order_by(MacSlot.mac).all()
    
    def get_number_slots(self):
        return int(self.number_slots)
    
    def get_percentage_range_usage(self):
        if not self.number_slots == -1:
            return float((len(self.resources.all())/float(self.number_slots))*100,2)
        return -1
    
    def destroy(self):
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            if len(self.resources.filter_by(is_excluded=False).all()) > 0:
                raise Exception("Cannot delete MacRange. Range still contains allocated Macs")
            for mac in self.resources.all():
                # Delete excluded resources
                db.session.delete(mac)
                db.session.commit()
            db.session.delete(self)
            db.session.commit()
    
    def allocate_mac(self):
        '''
        Allocates a MAC address of the range    
        '''
        with MutexStore.get_object_lock(self.get_lock_identifier()):                        
            logging.debug("************************ RANGE 1")
            # Implements first fit algorithm
            if self.next_available_mac == None:                                
                raise Exception("Could not allocate any MAC")
                logging.debug("********************* RANGE 2")
            new_mac = MacSlot.mac_factory(self,self.next_available_mac)
            self.resources.append(new_mac)
            # Try to find new slot
            try:
                logging.debug("********************** RANGE 3")
                it= EthernetUtils.getMacIterator(self.next_available_mac,self.end_mac)
                logging.debug("********************** RANGE 4")
                while True:
                    mac = it.getNextMac()
                    logging.debug("***************** RANGE 5 " + str(mac))
                    if self.__is_mac_available(mac):
                        logging.debug("******************* RANGE 6")
                        break
                    self.next_available_mac = mac
            except Exception as e:
                logging.debug("************************ ERROR RANGE " + str(e))
                self.next_available_mac = None
        logging.debug("*************************** RANGE 7")
        self.autosave()
        return new_mac  
    
    def release_mac(self,mac_obj):
        '''
        Releases an MAC address of the range (but it does not destroy the object!!)     
        '''
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            mac_str = mac_obj.get_mac()
            if not len(self.resources.filter_by(mac=mac_str).all()) > 0:
                raise Exception("Cannot release Mac %s. Reason may be is unallocated or is an excluded Mac",mac_str)
            self.resources.remove(mac_obj)
            # Determine new available Mac
            if not self.next_available_mac == None:
                if EthernetUtils.compare_macs(mac_str,self.next_available_mac) > 0:
                    # Do nothing
                    pass
                else:
                    self.next_available_mac = mac_str
            else:
                # No more gaps
                self.next_available_mac = mac_str
            self.autoSave()                                                                           
    
    def add_excluded_mac(self,mac_str,comment=""):
        '''
        Add a MAC to the exclusion list 
        '''
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            # Check is not already allocated
            if not  self.__is_mac_available(mac_str):
                raise Exception("Mac already allocated or marked as excluded")
            # Then forbidd
            if not EthernetUtils.is_mac_in_range(mac_str,self.start_mac,self.end_mac):
                raise Exception("Mac is not in range")
            new_mac = MacSlot.excluded_mac_factory(self,mac_str,comment)
            self.resources.append(new_mac)
            # If was nextSlot shift
            if self.next_available_mac == mac_str:
                try:
                    it = EthernetUtils.get_mac_iterator(self.next_available_mac,self.end_mac)
                    while True:
                        mac = it.get_next_mac()
                        if self.__is_mac_available(mac):
                            break
                except Exception as e:
                    self.next_available_mac = None
            self.autosave()    
     
    def removeExcludedMac(self,mac_obj):
        '''
        Deletes an Mac from the exclusion list  (but it does not destroy the object!!)
        '''
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            mac_str = mac_obj.get_mac()
            if (not self.macs.filter_by(mac=mac_str).first().is_excluded_mac()):
                raise Exception("Cannot release Mac. Reason may be is unallocated or is not excluded Mac")
            self.macs.remove(mac_obj)
            # Determine new available Mac
            if not self.next_available_mac == None:
                if EthernetUtils.compare_macs(mac_str,self.next_available_mac) > 0:
                    # Do nothing                 
                    pass
                else:
                    self.next_available_mac = mac_str
            else:
                # No more gaps
                self.nextAvailableMac = mac_str
            self.autoSave()
     
    '''
    Static methods
    '''
    @staticmethod
    def get_allocated_global_number_of_slots():
        allocated = 0
        for range in MacRange.query.filter_by(is_global=True).all():
            allocated += len(range.macs.all())
        return allocated
    
    @staticmethod
    def get_global_number_of_slots():
        slots = 0
        for range in MacRange.query.filter_by(is_global=True).all():
            slots += range.numberOfSlots
        return int(slots)
    
    def rebase_pointer(self):
        '''Used when pointer has lost track mostly due to bug #'''
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            print "Rebasing pointer of range: "+str(self.id)
            print "Current pointer point to: "+self.next_available_mac
            try:
                it = EthernetUtils.get_mac_iterator(self.start_mac,self.end_mac)
                while True:
                    mac = it.get_next_mac()
                    if self.__is_mac_available(mac):
                        break
                self.next_available_mac = mac
            except Exception as e:
                self.next_available_mac = None
            print "Pointer will be rebased to: "+self.next_available_mac
            db.session.add(self)
            db.session.commit()
    
    @staticmethod
    def rebase_pointers():
        for range in MacRange.query.all():
            range.rebase_pointer()
