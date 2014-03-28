from array import *
import re

ETH_MIN_VALUE=0
ETH_MAX_VALUE=255

class EthernetMacValidator:
    @staticmethod
    def validate_mac(mac):
        Mac_RE = r'^([0-9a-fA-F]{2}([:-]?|$)){6}$'
        mac_re = re.compile(Mac_RE)                                
        if not mac_re.match(mac):
            # raise ValidationError("Invalid Ethernet Mac format")
            raise Exception("Invalid Ethernet Mac format")
    
    @staticmethod
    def _dec2hex(n):
        """return the hexadecimal string representation of integer n"""
        return "%02X" % n
    
    @staticmethod
    def _hex2dec(s):
        """return the integer value of a hexadecimal string s"""
        return int(s, 16)
        
    @staticmethod
    def __convert_to_numeric_value(mac):
        value =  mac.split(":")
        return (EthernetMacValidator._hex2dec(value[0]) <<40) +(EthernetMacValidator._hex2dec(value[1]) <<32) +(EthernetMacValidator._hex2dec(value[2]) <<24) + (EthernetMacValidator._hex2dec(value[3]) <<16) +  (EthernetMacValidator._hex2dec(value[4]) <<8) + (EthernetMacValidator._hex2dec(value[5]))
            
    @staticmethod
    def compare_macs(a,b):
        return EthernetMacValidator.__convert_to_numeric_value(a) -  EthernetMacValidator.__convert_to_numeric_value(b) 
    
    @staticmethod
    def is_mac_in_range(mac,start,end):
        EthernetMacValidator.validate_mac(mac)        
        EthernetMacValidator.validate_mac(start)        
        EthernetMacValidator.validate_mac(end)                     
        return EthernetMacValidator.__convert_to_numeric_value(mac)>=EthernetMacValidator.__convert_to_numeric_value(start) and  EthernetMacValidator.__convert_to_numeric_value(mac)<=EthernetMacValidator.__convert_to_numeric_value(end)
        
class EthernetMacIterator:
    # TODO: this is not thread safe!
    _mac = array('l',[0,0,0,0,0,0]) 
    _start_range_mac = array('l',[0,0,0,0,0,0]) 
    _end_range_mac = array('l',[0,0,0,0,0,0]) 
    _network = array('l',[0,0,0,0,0,0])
    _broadcast = array('l',[255,255,255,255,255,255])
    _is_first_increment=True
    '''
    Constructor
    '''        
    def __init__(self,startmac,endmac):    
        # Check well formed MAC
        EthernetUtils.check_valid_mac(startmac)
        EthernetUtils.check_valid_mac(endmac)
        # Check Range
        if EthernetMacValidator.compare_macs(startmac,endmac) >= 0:
            raise Exception("Invalid Range")
        splitted = startmac.split(":")                
        # Translate MAC
        self._mac[0] = self._hex2dec(splitted[0]) 
        self._mac[1] = self._hex2dec(splitted[1])
        self._mac[2] = self._hex2dec(splitted[2])
        self._mac[3] = self._hex2dec(splitted[3])
        self._mac[4] = self._hex2dec(splitted[4])
        self._mac[5] = self._hex2dec(splitted[5])
        # Put start
        self._start_range_mac[0] = self._hex2dec(splitted[0]) 
        self._start_range_mac[1] = self._hex2dec(splitted[1])
        self._start_range_mac[2] = self._hex2dec(splitted[2])
        self._start_range_mac[3] = self._hex2dec(splitted[3])
        self._start_range_mac[4] = self._hex2dec(splitted[4])
        self._start_range_mac[5] = self._hex2dec(splitted[5])
        splitted = endmac.split(":")       
        # Put end
        self._end_range_mac[0] = self._hex2dec(splitted[0]) 
        self._end_range_mac[1] = self._hex2dec(splitted[1])
        self._end_range_mac[2] = self._hex2dec(splitted[2])
        self._end_range_mac[3] = self._hex2dec(splitted[3])
        self._end_range_mac[4] = self._hex2dec(splitted[4])
        self._end_range_mac[5] = self._hex2dec(splitted[5])       
        
    '''
    Hexadecimal aids
    '''
    def _dec2hex(self,n):
        """return the hexadecimal string representation of integer n"""
        return "%02X" % n
             
    def _hex2dec(self,s):
        """return the integer value of a hexadecimal string s"""
        return int(s, 16)
    
    '''
    Private method that increments Mac
    '''
    def __increment(self,i=5):
        self._mac[i]+=1
        if self._mac[i] > ETH_MAX_VALUE:
            self._mac[i] = ETH_MIN_VALUE
            if i != 0: 
                self.__increment(i-1)
            else:
                raise Exception("No more MACs")
    
    '''
    Private method that decrements Mac
    '''
    def __decrement(self,i=5):
        self._mac[i]-=1
        if self._mac[i] < ETH_MIN_VALUE:
            self._mac[i] = ETH_MAX_VALUE
            if i != 0: 
                self.__decrement(i-1)
            else:
                raise Exception("No more MACs")
    
    '''Checkings'''
    def __is_broadcast_mac(self):
        return self._mac[0] == ETH_MAX_VALUE and self._mac[1] == ETH_MAX_VALUE and self._mac[2] == ETH_MAX_VALUE and self._mac[3] == ETH_MAX_VALUE and self._mac[4] == ETH_MAX_VALUE and self._mac[5] == ETH_MAX_VALUE
    
    def __is_network_mac(self):
        return self._mac[0] == ETH_MIN_VALUE and self._mac[1] == ETH_MIN_VALUE and self._mac[2] == ETH_MIN_VALUE and self._mac[3] == ETH_MIN_VALUE and self._mac[4] == ETH_MIN_VALUE and self._mac[5] == ETH_MIN_VALUE
                
    def __is_broadcast_or_network_mac(self):
        return self.__is_broadcast_mac() or self.__is_network_mac()
        
    def __convert_to_numeric_value(self,value):
        return (value[0] <<40) + (value[1] <<32) +  (value[2] <<24) + (value[3]<<16)+(value[4]<<8)+(value[5])

    def __is_mac_not_in_range(self):
        return self.__convert_to_numeric_value(self._start_range_mac)>self.__convert_to_numeric_value(self._mac) or self.__convert_to_numeric_value(self._end_range_mac)<self.__convert_to_numeric_value(self._mac)
    
    '''
    Public method that gets current Mac
    '''
    def get_pointed_mac_as_string(self):
        return self._dec2hex(self._mac[0])+":"+self._dec2hex(self._mac[1])+":"+self._dec2hex(self._mac[2])+":"+self._dec2hex(self._mac[3])+":"+self._dec2hex(self._mac[4])+":"+self._dec2hex(self._mac[5])
    
    '''
    Public method that increments IP and returns the next non-broadcast non-network ip of the iteration
    '''
    def get_next_mac(self):
        while True:
            if not self._is_first_increment:
                # Increment
                self.__increment()
            else:
                self._is_first_increment = False
            # Check if we are in range
            if self.__is_mac_not_in_range():
                raise Exception("No More MACs")
            # Check if broadcast or network
            if not self.__is_broadcast_or_network_mac():
                break
        # Return stringified IP
        return self.get_pointed_mac_as_string()
        
    '''
    Public method that decrements IP and returns the next non-broadcast non-network ip of the iteration
    '''
    def get_previous_mac(self):
        while True:
            if not self._is_first_increment:
                # Increment
                self.__decrement()
            else:
                self._is_first_increment = False
            # Check if we are in range
            if self.__is_mac_not_in_range():
                raise Exception("No More MACs")
            # Check if broadcast or network
            if not self.__is_broadcast_or_network_mac():
                break
        # Return stringified IP
        return self.get_pointed_mac_as_string()
        
class EthernetUtils():
    @staticmethod
    def check_valid_mac(mac):
        return EthernetMacValidator.validate_mac(mac)

    @staticmethod
    def get_mac_iterator(mac_start,mac_end):
        return EthernetMacIterator(mac_start,mac_end)
    
    @staticmethod
    def is_mac_in_range(mac,start,end):
        return EthernetMacValidator.is_mac_in_range(mac,start,end)
            
    @staticmethod
    def compare_macs(a,b):
        return EthernetMacValidator.compare_macs(a,b)
    
    @staticmethod
    def get_number_of_slots_in_range(start,end):
        EthernetUtils.check_valid_mac(start)        
        EthernetUtils.check_valid_mac(end)                
        slots = abs(EthernetMacValidator.compare_macs(end,start))
        # Substract broadcast
        if EthernetUtils.is_mac_in_range("00:00:00:00:00:00",start,end):
            slots -=1        
        return slots


#it = EthernetUtils.getMacIterator("FF:FF:FF:FF:FE:00","FF:FF:FF:FF:FF:FF")

#print it.getPointedMacAsString()
#i=0
#while True:
#        print it.getNextMac()
#        i+=1
#        if i >1024:
#                break
#print EthernetUtils.getNumberOfSlotsInRange("00:00:00:00:00:00","FF:FF:FF:FU:FF:FF")
#EthernetUtils.check_valid_mac("00:11:22:11f:aa:bb")

