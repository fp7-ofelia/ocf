from abc import ABCMeta
from abc import abstractmethod

class HandlerBase:
    
    """
    1. Handle credentials & options
    2. Translate RSpecs to {aggregate, slice, sliver, resource} instances
    """
    
    __metaclass__= ABCMeta
    
    @abstractmethod
    def GetVersion(self, options=dict()):
        """
        Does not require credentials
        """
        return
    
    @abstractmethod
    def ListResources(self, credentials=list(), options=dict()):
        return
    
    @abstractmethod    
    def Describe(self, urns=dict(), credentials=dict(),options=dict()):
        return

    @abstractmethod
    def Allocate(self, slice_urn="", credentials=list(), rspec="", options=dict()):
        return
    
    @abstractmethod    
    def Provision(self, urns=list(), credentials=list(), options=dict()):
        return
    
    @abstractmethod
    def Delete(self, urns=list(), credentials=list(), options=dict()):
        return
    
    @abstractmethod
    def PerformOperationalAction(self, urns=list(), credentials=list(), action=None, options=dict()):
        return
    
    @abstractmethod            
    def Status(self, urns=list(), credentials=list(), options=dict()):
        return
        
    @abstractmethod
    def Renew(self, urns=list(), credentials=list(), expiration_time=None, options=dict()):
        return
        
    @abstractmethod
    def Shutdown(self, slice_urn="", credentials=list(), options=dict()):
        return 

