#from abc import ABCMeta
#from abc import abstractmethod

from federation.ambase.src.abstract.classes.delegatebase import DelegateBase

class GeniV3Delegate(DelegateBase):
    
    """
    Handle internal exceptions to pass to the handler
    """
    
    def __init__(self):
        self.__resource_manager = None
    
    def get_version(self):
        return
    
    def list_resources(self, geni_available=False):
        return
    
    def describe(self, urns=dict()):
        return

    def reserve(self, slice_urn, am,expiration):
        """
        Allocate slivers
        """
        # If there is no value, use empty string
        #slice_urn = slice_urn or ""
        return
    
    def create(self, urns=list()):
        """
        Provision slivers
        """
        return
    
    def delete(self, urns=list()):
        """
        Delete slivers
        """
        return
    
    def perform_operational_action(self, urns=list(), action=None, geni_besteffort=True):
        return
    
    def status(self, urns=list()):
        return
        
    def renew(self, urns=list(), expiration_time=None):
        return
        
    def shut_down(self, urns=list()):
        return
