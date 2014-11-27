from ambase.src.abstract.classes.rspecmanagerbase import RSpecManagerBase
from rspecs.src.geni.v3.craftermanager import CrafterManager
from rspecs.src.geni.v3.parsermanager import ParserManager

class RSpecManager(RSpecManagerBase):
    
    def __init__(self):
        self.__crafter = CrafterManager()
        self.__parser = ParserManager()
    
    def compose_advertisement(self, resources):
        return self.__crafter.get_advertisement(resources)
    
    def compose_manifest(self, slivers):
        return self.__crafter.manifest_slivers(slivers)

    def parse_request(self, request_rspec):
        return self.__parser.parse_request_rspec(request_rspec)
