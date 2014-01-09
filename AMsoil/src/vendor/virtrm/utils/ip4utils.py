from array import *
import re

IP4_MIN_VALUE=0
IP4_MAX_VALUE=255

class IP4Validator:
    @staticmethod
    def validate_ip(ip):
        controlIp = re.compile(r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}(/\d?\d)?$')
        if not controlIp.match(ip):
            raise Exception("Invalid IP format")
    
    @staticmethod
    def validate_netmask(mask):
        splitted = mask.split(".")
        netmask_started=False
        i=3
        while True:
            j=0
            value = int(splitted[i])&255
            while True:
                if not value&0x01 == 0x01:
                    if netmask_started:
                        raise Exception("Invalid Netmask format")        
                    else:
                        netmask_started = True        
                    if j<7:
                        value=value>>1
                        j+=1
                    else:         
                        break
                if i>0:
                    i-=1
                else:
                    break
    
    @staticmethod
    def __convert_to_numeric_value(ip):
        value =  ip.split(".")
        return (int(value[0]) <<24) + (int(value[1]) <<16) +  (int(value[2]) <<8) + (int(value[3]))
    
    @staticmethod
    def compare_ips(a,b):
        return IP4Validator.__convert_to_numeric_value(a) -  IP4Validator.__convert_to_numeric_value(b) 

    @staticmethod
    def is_ip_in_range(ip,start,end):
        IP4Validator.validate_ip(ip)        
        IP4Validator.validate_ip(start)        
        IP4Validator.validate_ip(end)        
        return IP4Validator.__convert_to_numeric_value(ip)>=IP4Validator.__convert_to_numeric_value(start) and  IP4Validator.__convert_to_numeric_value(ip)<=IP4Validator.__convert_to_numeric_value(end)
    
    @staticmethod
    def get_number_of_slots_in_range(start,end,netmask):
        IP4Utils.check_valid_ip(start)
        IP4Utils.check_valid_ip(end)
        IP4Utils.check_valid_netmask(netmask)    
        end_numeric = IP4Validator.__convert_to_numeric_value(end)
        start_numeric = IP4Validator.__convert_to_numeric_value(start)
        netmask_numeric = IP4Validator.__convert_to_numeric_value(netmask)
        import math
        value =  netmask.split(".")
        shift = 0
        for i in range(0,4):
            if not int(value[i]) == 0:
                shift += round(math.log(int(value[i]),2),0)
        shift = 32 - int(shift)
        #print "Shift value is: "+str(shift)
        #print "Numeric:"+str(end_numeric)+" shift:"+str(shift)+" start_numeric:"+str(start_numeric)
        #print "Numeric:"+str(end_numeric>>shift)+" start_numeric:"+str(start_numeric>>shift)
        #print str(int(end_numeric>>shift))+"-"+str(int(start_numeric>>shift))
        nsubnet = int(end_numeric>>shift)- int(start_numeric>>shift)
        #print "Number of subnets"+str(nsubnet)        
        slots = end_numeric - start_numeric - 2*(nsubnet+1) +1
        # Substract broadcast
        return slots
        
class IP4Iterator:
    # TODO: this is not thread safe!
    _ip = array('l',[0,0,0,0]) 
    _start_range_ip = array('l',[0,0,0,0]) 
    _end_range_ip = array('l',[0,0,0,0]) 
    _netmask = array('l',[0,0,0,0]) 
    _is_first_increment=True
    '''
    Constructor
    '''        
    def __init__(self,startip,endip,netmask):            
        # Check well formed IPs
        IP4Utils.check_valid_ip(startip)
        IP4Utils.check_valid_ip(endip)
        IP4Utils.check_valid_netmask(netmask)
        # Check Range
        if IP4Validator.compare_ips(startip,endip) >= 0:
            raise Exception("Invalid Range")
        splitted = startip.split(".")                
        # Translate IP
        self._ip[0] = int(splitted[0]) 
        self._ip[1] = int(splitted[1])
        self._ip[2] = int(splitted[2])
        self._ip[3] = int(splitted[3])
        # Put start
        self._start_range_ip[0] = int(splitted[0]) 
        self._start_range_ip[1] = int(splitted[1])
        self._start_range_ip[2] = int(splitted[2])
        self._start_range_ip[3] = int(splitted[3])
        splitted = netmask.split(".")
        # Translate Netmask
        self._netmask[0] = int(splitted[0]) 
        self._netmask[1] = int(splitted[1])
        self._netmask[2] = int(splitted[2])
        self._netmask[3] = int(splitted[3])        
        splitted = endip.split(".")                
        # Put end
        self._end_range_ip[0] = int(splitted[0]) 
        self._end_range_ip[1] = int(splitted[1])
        self._end_range_ip[2] = int(splitted[2])
        self._end_range_ip[3] = int(splitted[3])
    
    '''
    Private method that increments IP
    '''
    def __increment(self,i=3):
        self._ip[i]+=1
        if self._ip[i] > IP4_MAX_VALUE:
            self._ip[i] = IP4_MIN_VALUE
            if i != 0: 
                self.__increment(i-1)
            else:
                raise Exception("No more IPs")
    
    '''
    Private method that decrements IP
    '''
    def __decrement(self,i=3):
        self._ip[i]-=1
        if self._ip[i] < IP4_MIN_VALUE:
            self._ip[i] = IP4_MAX_VALUE
            if i != 0: 
                self.__decrement(i-1)
            else:
                raise Exception("No more IPs")
    
    '''Checkings'''
    def __get_current_network_segment(self):
        toreturn = array('l',[0,0,0,0]) 
        toreturn[0] = self._ip[0] & self._netmask[0]
        toreturn[1] = self._ip[1] & self._netmask[1]
        toreturn[2] = self._ip[2] & self._netmask[2]
        toreturn[3] = self._ip[3] & self._netmask[3]
        return toreturn 
    
    def __isBroadcastIp(self):
        self.__increment()
        toReturn = self.__is_network_ip()
        self.__decrement()
        return toReturn
        
    def __is_network_ip(self):
        net = self.__get_current_network_segment() 
        return net[0] == self._ip[0] and net[1] == self._ip[1] and net[2] == self._ip[2] and net[3] == self._ip[3]
                
    def __is_broadcast_or_network_ip(self):
        return self.__isBroadcastIp() or self.__is_network_ip()
        
    def __convert_to_numeric_value(self,value):
        return (value[0] <<24) + (value[1] <<16) +  (value[2] <<8) + (value[3])

    def __is_ip_not_in_range(self):
        return self.__convert_to_numeric_value(self._start_range_ip)>self.__convert_to_numeric_value(self._ip) or self.__convert_to_numeric_value(self._end_range_ip)<self.__convert_to_numeric_value(self._ip)
    
    '''
    Public method that gets current IP
    '''
    def get_pointed_ip_as_string(self):
        return str(self._ip[0])+"."+str(self._ip[1])+"."+str(self._ip[2])+"."+str(self._ip[3])
    
    '''
    Public method that increments IP and returns the next non-broadcast non-network ip of the iteration
    '''
    def get_next_ip(self):
        while True:
            if not self._is_first_increment:
                # Increment
                self.__increment()
            else:
                self._is_first_increment = False 
            # Check if we are in range
            if self.__is_ip_not_in_range():
                raise Exception("No More Ips")
            # Check if broadcast or network
            if not self.__is_broadcast_or_network_ip():
                break
        # Return stringified IP
        return self.get_pointed_ip_as_string()
        
    '''
    Public method that decrements IP and returns the next non-broadcast non-network ip of the iteration
    '''
    def get_previous_ip(self):
        while True:
            if not self._is_first_increment:
                # Decrement
                self.__decrement()
            else:
                self._is_first_increment = False          
            # Check if we are in range
            if self.__is_ip_not_in_range():
                raise Exception("No More Ips")  
            # Check if broadcast or network
            if not self.__is_broadcast_or_network_ip():
                break
        # Return stringified IP
        return self.get_pointed_ip_as_string()
        
class IP4Utils():
    @staticmethod
    def check_valid_ip(ip):
        return IP4Validator.validate_ip(ip)
    
    @staticmethod
    def is_ip_in_range(ip,start,end):
        return IP4Validator.is_ip_in_range(ip,start,end)
            
    @staticmethod
    def compare_ips(a,b):
        return IP4Validator.compare_ips(a,b)
    
    @staticmethod
    def check_valid_netmask(ip):
        return IP4Validator.validate_netmask(ip)
                
    @staticmethod
    def get_ip_iterator(ip_start,ip_end,netmask):
        return IP4Iterator(ip_start,ip_end,netmask)
        
    @staticmethod
    def get_number_of_slots_in_range(start,end,netmask):
        return IP4Validator.get_number_of_slots_in_range(start,end,netmask)
                
#it = IP4Utils.get_ip_iterator("192.168.0.0","192.168.1.255","255.255.255.0")
#print IP4Utils.get_number_of_slots_in_range("192.168.0.0","192.168.10.255","255.255.255.0")

#print it.get_pointed_ip_as_string()
#i=0
#while True:
#        print it.get_next_ip()
#        i+=1
#        if i >512:
#                break
print 
#IP4Utils.check_valid_netmask("240.0.0.0")

