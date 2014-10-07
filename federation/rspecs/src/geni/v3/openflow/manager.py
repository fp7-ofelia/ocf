from ambase.src.abstract.classes.rspecmanagerbase import RSpecManagerBase

class OpenFlowRSpecManager(RSpecManagerBase):
    
    def __init__(self):
        pass
    
    def compose_advertisement(self, resources):
        return ""
    
    def compose_manifest(self, slivers):
        return ""
    
    def parse_request(self):
        return None
    
