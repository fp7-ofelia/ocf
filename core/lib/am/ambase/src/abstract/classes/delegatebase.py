from abc import ABCMeta
from abc import abstractmethod

class DelegateBase:
    
    """
    Handle internal exceptions to pass to the handler
    """
    
    __metaclass__= ABCMeta
    
    @abstractmethod
    def get_version(self):
        return
    
    @abstractmethod
    def list_resources(self, geni_available=False):
        return
    
    @abstractmethod    
    def describe(self, urns=dict()):
        return

    @abstractmethod
    def reserve(self, slice_urn, reservation, expiration, users):
        """
        Allocate slivers
        """
        # If there is no value, use empty string
        #slice_urn = slice_urn or ""
        return
    
    @abstractmethod    
    def create(self, urns, expiration, users):
        """
        Provision slivers
        """
        return
    
    @abstractmethod
    def delete(self, urns=list()):
        """
        Delete slivers
        """
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

