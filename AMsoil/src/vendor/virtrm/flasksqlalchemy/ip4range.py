from sqlalchemy.dialects.mysql import TINYINT, BIGINT
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

import inspect

from base import db
from ip4utils import IP4Utils
from ipslot import Ip4Slot
from ip4rangeips import Ip4RangeIps
from utils.mutexstore import MutexStore

import amsoil.core.log

logging=amsoil.core.log.getLogger('Ip4Range')



'''@author: SergioVidiella'''


class Ip4Range(db.Model):
    """Ip4Range."""

    __tablename__ = 'vt_manager_ip4range'

    id = db.Column(db.Integer, autoincrement=True, nullable=False,primary_key=True)
    # Range name
    name = db.Column(db.String(255), nullable=False, unique=True)
    is_global = db.Column("isGlobal", TINYINT(1), nullable=False)
    # Range parameters
    start_ip = db.Column("startIp", db.String(15), nullable=False)
    end_ip = db.Column("endIp", db.String(15), nullable=False)
    netmask = db.Column("netMask", db.String(15), nullable=False)
    # Networking parameters associated to this range
    gw = db.Column(db.String(15))
    dns1 = db.Column(db.String(15))
    dns2 = db.Column(db.String(15))
    # Statistics
    number_slots = Column("numberOfSlots", BIGINT(20))
    # Pool of ips both assigned and excluded (particular case of assignment)
    next_available_ip = db.Column("nextAvailableIp", db.String(15))
    ips = association_proxy("ip4range_ips", "ipslot")
    # Mutex
    mutex = None
    # Defines soft or hard state of the range 
    do_save = True

    @staticmethod
    def constructor(name, start_ip, end_ip, netmask, gw, dns1, dns2, is_global=True, save=True):
        self = Ip4Range()
        try:
            # Default constructor
            IP4Utils.check_valid_ip(start_ip)
            IP4Utils.check_valid_ip(end_ip)
            IP4Utils.check_valid_netmask(netmask)
            IP4Utils.check_valid_ip(gw)
            IP4Utils.check_valid_ip(dns1)
            if not dns2 == "":
                IP4Utils.check_valid_ip(dns2)
            self.name = name
            self.is_global= is_global
            self.start_ip = start_ip
            self.end_ip = end_ip
            self.netmask = netmask
            self.gw = gw
            self.dns1 = dns1
            if not dns2 == "":
                self.dns2 = dns2
            # Create an iterator
            it = IP4Utils.get_ip_iterator(self.start_ip,self.end_ip,self.netmask)
            self.next_available_ip = it.get_next_ip()
            # Number of Slots
            try:
                self.number_slots = IP4Utils.get_number_of_slots_in_range(start_ip,end_ip,netmask)
            except Exception as e:
                print "Exception doing slot calculation"+str(e)
                self.number_slots = -1
            self.do_save = save
            if save:
                db.session.add(self)
                db.session.commit()
        except Exception as e:
            raise e
        return self

    '''Validators'''
    @validates('startIp')
    def validate_startip(self, key, ip):
        try:
            IP4Utils.check_valid_ip(ip)
            return ip
        except Exception as e:
            raise e

    @validates('endIp')
    def validate_endip(self, key, ip):
        try:
            IP4Utils.check_valid_ip(ip)
            return ip
        except Exception as e:
            raise e

    @validates('netmask')
    def validate_netmask(self, key, netmask):
        try:
            IP4Utils.checkValidNetmask(netmask)
            return netmask
        except Exception as e:
            raise e

    @validates('gw')
    def validate_gw(self, key, gw):
        try:
            IP4Utils.check_valid_ip(gw)
            return gw
        except Exception as e:
            raise e
 
    @validates('dns1')
    def validate_dns1(self, key, dns):
        try:
            IP4Utils.check_valid_ip(dns)
            return dns
        except Exception as e:
            raise e

    @validates('dns2')
    def validate_dns2(self, key, dns):
        try:
            IP4Utils.check_valid_ip(dns)
            return dns
        except Exception as e:
            raise e

    @validates('nextAvailableIp')
    def validate_next_available_ip(self, key, ip):
        try:
            IP4Utils.check_valid_ip(ip)
            return ip
        except Exception as e:
            raise e

    '''Private methods'''
    def __setStartIp(self, value):
        IP4Utils.check_valid_ip(value)
        self.start_ip = value
        self.auto_save()
    
    def __setEndIp(self, value):
        IP4Utils.check_valid_ip(value)
        self.end_ip = value
        self.auto_save()
    
    def __setNetmask(self, value):
        IP4Utils.check_valid_netmask(value)
        self.netmask = value
        self.auto_save()
    
    def __isIpAvailable(self,ip):
        return len(self.ips.filter_by(ip=ip).all()) == 0
    
    def auto_save(self):
        if self.do_save:
            db.session.add(self)
            db.session.commit()
    
    '''Public methods'''
    def get_lock_identifier(self):
        # Uniquely identifies object by a key
        return inspect.currentframe().f_code.co_filename+str(self)+str(self.id)

    def get_name(self):
        return self.name
    
    def get_is_global(self):
        return self.isGlobal
     
    def get_start_ip(self):
       return self.start_ip
        
    def get_end_ip(self):
        return self.end_ip
        
    def get_netmask(self):
        return self.netmask

    def get_gateway_ip(self):
        return self.gw
        
    def get_dns1(self):
        return self.dns1
       
    def get_dns2(self):
        return self.dns2
    
    def get_excluded_ips(self):
        return self.ips.filter_by(is_excluded=True).order_by(Ip4Slot.ip).all()
    
    def get_allocated_ips(self):
        return self.ips.filter_by(is_excluded=False).order_by(Ip4Slot.ip).all()
    
    def get_number_of_slots(self):
        return int(self.number_slots)
     
    def get_percentage_range_usage(self):
        if not self.number_slots == -1:
            return float((len(self.ips.all())/self.number_slots)*100)
        return -1
    
    def destroy(self):
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            if len(self.ips.filter_by(is_excluded=False)) > 0:
                raise Exception("Cannot delete Ip4Range. Range still contains allocated IPs")
            for ip in self.ips.all():
                # Delete excluded ips
                db.session.delete(ip)
                db.session.commit()
            db.session.delete(self)
            db.session.commit()
    
    def allocateIp(self):
        '''
        Allocates an IP address of the range    
        '''
        with MutexStore.get_object_lock(self.get_lock_identifier()):                        
            logging.debug("******************************************* RANGEIP 1")
            # Implements first fit algorithm
            if self.next_available_ip == None:                                
                logging.debug("******************************************* RANGEIP ERROR 1")
                raise Exception("Could not allocate any IP")
            logging.debug("******************************************* RANGEIP 2")
            new_ip = Ip4Slot.ip_factory(self,self.next_available_ip)
            logging.debug("******************************************* RANGEIP 3")
            self.ips.append(new_ip)
            logging.debug("******************************************* RANGEIP 4")
            # Try to find new slot
            try:
                logging.debug("******************************************* RANGEIP 5")
                it = IP4Utils.get_ip_iterator(self.next_available_ip,self.end_ip,self.netmask)
                logging.debug("******************************************* RANGEIP 6")
                while True:
                    ip = it.get_next_ip()
                    logging.debug("******************************************* RANGEIP 7 " + str(ip))
                    if self.__is_ip_available(ip):
                        logging.debug("******************************************* RANGEIP 9")
                        break
                    self.next_available_ip = ip
                logging.debug("******************************************* RANGEIP 8")
            except Exception as e:
                logging.debug("******************************************* RANGEIP ERROR 2 " + str(e))
                self.next_available_ip = None
            logging.debug("******************************************* RANGEIP 10")
            self.auto_save()
            return new_ip   
    
    def releaseIp(self,ip_obj):
        '''
        Releases an IP address of the range (but it does not destroy the object!!)      
        '''
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            ip_str = ip_obj.get_ip()
            if not len(self.ips.filter_by(ip=ip_str).filter_by(is_excluded=False).all()) > 0:
                raise Exception("Cannot release Ip %s. Reason may be is unallocated or is an excluded Ip",ip_str)
            self.ips.remove(ip_obj)
            # Determine new available Ip
            if not self.next_available_ip == None:
                if IP4Utils.compare_ips(ip_str,self.next_available_ip) > 0:
                    # Do nothing
                    pass
                else:
                    self.next_available_ip = ip_str
            else:
                # No more gaps
                self.next_available_ip = ip_str
            self.auto_save()                                                                        

    def addExcludedIp(self,ip_str,comment):
        '''
        Add an IP to the exclusion list 
        '''
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            # Check is not already allocated
            if not  self.__is_ip_available(ip_str):
                raise Exception("Ip already allocated or marked as excluded")
            # Then forbidd
            if not IP4Utils.is_ip_in_range(ip_str,self.start_ip,self.end_ip):
                raise Exception("Ip is not in range")
            new_ip = Ip4Slot.excluded_ip_factory(self,ip_str,comment)
            self.ips.append(new_ip)
            # If was nextSlot shift
            if self.next_available_ip == ip_str:
                try:
                    it = IP4Utils.get_ip_iterator(self.next_available_ip,self.end_ip,self.netmask)
                    while True:
                        ip = it.get_next_ip()
                        if self.__is_ip_available(ip):
                            break
                except Exception as e:
                    self.next_available_ip = None
            self.auto_save()
    
    def removeExcludedIp(self,ip_obj):
        '''
        Deletes an IP from the exclusion list (but it does not destroy the object!!)
        '''
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            ip_str = ip_obj.get_ip()
            if not self.ips.filter_by(ip=ip_str).one().is_excluded_ip():
                raise Exception("Cannot release Ip. Reason may be is unallocated or is not excluded Ip")
            self.ips.remove(ip_obj)
            # Determine new available Ip
            if not self.next_available_ip == None:
                if IP4Utils.compare_ips(ip_str,self.next_available_ip) > 0:
                    # Do nothing
                    pass
                else:
                    self.next_available_ip = ip_str
            else:
                # No more gaps
                self.next_available_ip = ip_str
            self.auto_save()
    
    '''
    Static methods
    '''
    @staticmethod
    def get_allocated_global_number_of_slots():
        allocated = 0
        for range in Ip4Range.query.filter_by(is_global=True).all():
            allocated += len(range.ips.all())
        return allocated

    @staticmethod
    def get_global_number_of_slots():
        slots = 0
        for range in Ip4Range.query.filter_by(is_global=True).all():
            slots += range.number_slots
        return int(slots)
    
    def rebase_pointer(self):
        '''Used when pointer has lost track mostly due to bug #'''
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            print "Rebasing pointer of range: "+str(self.id)
            print "Current pointer point to: "+self.nextAvailableIp
            try:
                it = IP4Utils.get_ip_iterator(self.start_ip,self.end_ip,self.netmask)
                while True:
                    ip = it.get_next_ip()
                    if self.__is_ip_available(ip):
                        break
                self.next_available_ip = ip
            except Exception as e:
                self.next_available_ip = None
            print "Pointer will be rebased to: "+self.nextAvailableIp
            db.session.add(self)
            db.session.commit()
    
    @staticmethod
    def rebase_pointers():
        '''Used when pointer has lost track mostly due to bug #'''
        for range in Ip4Range.query.all():
            range.rebase_pointer()

