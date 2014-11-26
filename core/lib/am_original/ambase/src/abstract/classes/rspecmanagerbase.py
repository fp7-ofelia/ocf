from abc import ABCMeta
from abc import abstractmethod

class RSpecManagerBase:
    """
    Abstract class, to be implemented in a new class.
    """
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def compose_advertisement(self, resources):
        """
        Returns the advertisement RSpec using a set of 
        resources as input.
        """
        return
    
    @abstractmethod
    def compose_manifest(self, slivers):
        """
        Returns the manifest RSpec using a set of slivers 
        (group of resources) as input.
        """
        return
    
    @abstractmethod
    def parse_request(self, request_rspec):
        """
        Translates the request RSpec into a set of
        resources.
        """
        return

