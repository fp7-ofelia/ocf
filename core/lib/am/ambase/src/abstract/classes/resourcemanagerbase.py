from abc import ABCMeta
from abc import abstractmethod

class ResourceManagerBase:
    
    __metaclass__= ABCMeta
    
    @abstractmethod
    def get_resources(self, urns = None):
        return
    
    @abstractmethod
    def create_resources(self, urns, expiration, users):
        return
    
    @abstractmethod
    def reserve_resources(self, slice_urn, reservation, expiration, users):
        return
    
    @abstractmethod
    def start_resources(self, urns, geni_best_effort): 
        return 
    
    @abstractmethod
    def stop_resources(self, urns, geni_best_effort):
        return 
    
    @abstractmethod
    def reboot_resources(self, urns, geni_best_effort):
        return
    
    @abstractmethod
    def delete_resources(self, urns, geni_best_effort): 
        return
    
    @abstractmethod
    def renew_resources(self, urns, geni_best_effort):
        return
    
