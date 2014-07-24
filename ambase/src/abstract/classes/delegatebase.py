from abc import ABCMeta
from abc import abstractmethod

class DelegateBase:
    
    __metaclass__= ABCMeta
    
    @abstractmethod
    def get_version(self):
        return
    
    @abstractmethod
    def list_resources(self, geni_available=False):
        return
    
    @abstractmethod    
    def describe(self, urns=dict(),credentials=dict(),options=dict()):
        return

    @abstractmethod
    def reserve(self, slice_urn="", resources):
        return
    
    @abstractmethod    
    def create(self, urns=list()):
        return
    
    @abstractmethod
    def delete(self, urns=list()):
        return  
    
    @abstractmethod
    def perform_operational_action(self, urns=list(), action=None, geni_besteffort=True):
        return
    
    @abstractmethod            
    def status(self, urns=list()):
        return 
        
    @abstractmethod
    def renew(self, urns=list(), expiration_time=None):
        return 
        
    @abstractmethod
    def shut_down(self, urns=list()):
        return 