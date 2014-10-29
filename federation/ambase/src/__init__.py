class Handler:
    
    def __init__(self):
        self.__component_manager_id = None
        self.__component_id = None
        
    def ListResources(self, credentials=list(), options=dict()):
        pass
    
    def Describe(self,urns=list(), credentials=list(), options=dict()):
        pass
    
    def Allocate(self, slice_urn, credentials=list(), rspec="", options=dict()):
        pass
    
    def Provision(self, urns=list(), credentials=list(), options=dict()):
        pass
        
    def Renew(self, urns=list(), credentials=list(), expiration_time="", options=dict()):
        pass
    
    def Status(self, urns=list(), credentials=list(), options=dict()):
        pass
    
    def PerformOperationalAction(self, urns=list(), credentials=list(), action="", options=dict()):
        pass
    
    def Delete(self, urns=list(), credentials=list(), options=dict()):
        pass
    
    def Shutdown(self, slice_urn, credentials=list(), options=dict()):
        pass
    
    
