from ambase.src.abstract.classes.rspecmanagerbase import RSpecManagerBase
from rspecs.src.geni.v3.openflow.foamlibcrafter import FOAMLibCrafter
from rspecs.src.geni.v3.openflow.foamlibparser import FOAMLibParser

class OpenFlowRSpecManager(RSpecManagerBase):
    
    def __init__(self):
        self.__crafter = FOAMLibCrafter()
        self.__parser = FOAMLibParser()
    
    def compose_advertisement(self, resources):
        return self.__crafter.get_advertisement(resources)
    
    def compose_manifest(self, slivers):
        return self.__crafter.get_manifest(slivers)
    
    def parse_request(self,rspec):
        return self.__parser.parse_request(rspec)
    
