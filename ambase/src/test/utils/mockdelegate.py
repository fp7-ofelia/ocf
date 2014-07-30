from src.abstract.classes.delegatebase import DelegateBase
from src.ambase.exceptions import AllocationError, DeleteError
from src.ambase.exceptions import SliceAlreadyExists


class MockDelegate(DelegateBase):
    
    # TODO Mock Exceptions??
    
    def __init__(self, success_mode=True, raise_already_exists = False):
        self.success_mode = success_mode
        self.raise_already_exists = raise_already_exists
    
    def get_version(self):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock error")
    
    def list_resources(self, geni_available=False):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock error")
    
    def describe(self, urns=dict(),credentials=dict(),options=dict()):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock error")
    
    def reserve(self, slice_urn="", am=None, expiration=None):
        if self.raise_already_exists:
            raise SliceAlreadyExists("Mock error")
        if self.success_mode:
            return True
        else:
            raise AllocationError("Mock error")
    
    def create(self, urns=list()):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock error")
    
    def delete(self, urns=list()):
        if self.success_mode:
            return True
        else:
            raise DeleteError("Mock error") 
    
    def perform_operational_action(self, urns=list(), action=None, geni_besteffort=True):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock error")
    
    def status(self, urns=list()):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock error")
    
    def renew(self, urns=list(), expiration_time=None):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock error")
    
    def shut_down(self, urns=list()):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock error")
