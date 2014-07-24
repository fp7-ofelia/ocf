from abc import ABCMeta
from abc import abstractmethod

class RSpecManager:
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def advertise_resources(self, resources):
        return
    
    @abstractmethod
    def manifest_slivers(self, slivers):
        return
    
    @abstractmethod
    def parse_request(self, rspec):
        return

