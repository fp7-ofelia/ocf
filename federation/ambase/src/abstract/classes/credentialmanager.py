from abc import ABCMeta
from abc import abstractmethod

class CredentialManager:
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def validate_for(self, credentials, method):
        return ""
    
    @abstractmethod
    def get_valid_creds(self):
        return ""
    
    @abstractmethod
    def get_expiration_list(self):
        return ""
    
    #TODO add methods to this class

