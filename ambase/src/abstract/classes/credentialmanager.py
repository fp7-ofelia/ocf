from abc import ABCMeta
from abc import abstractmethod

class CredentialManager:
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def validate_for(self, credentials, method):
        return ""
    
    #TODO add methods to this class

