from ambase.src.abstract.classes.resourcemanagerbase import ResourceManagerBase
from rspecs.src.geni.v3.container.resource import Resource
from rspecs.src.geni.v3.container.sliver import Sliver

class MockResourceManager(ResourceManagerBase):
    
    def __init__(self, default_resources=list()):
        resources = list()
        for self.i in range(0,4):
            r = Resource()
            r.set_id(self.i)
            r.set_uuid(self.i)
            #r.set_status("READY")
            r.set_component_id("urn:publicid:mocked+resource+%d" %self.i)
            r.set_component_manager_id("urn:publicid:mocked+resource+%d" %self.i)
            r.set_component_name("urn:publicid:mocked+resource+%d" %self.i)
            r.set_component_manager_name("urn:publicid:mocked+resource+%d" %self.i)
            s = Sliver()
            s.set_urn(r.get_component_manager_id())
            r.set_allocation_state("Free")
            s.set_resource(r)
            r.set_sliver(s)
            resources.append(r)
        self.resources = resources
        self.resources.extend(default_resources)
        print self.resources
        
              
    def get_resources(self, urns = None):
        if urns:
            result = list()
            print "Mocked_resource with urns", urns
            for urn in urns:
                for r in self.resources:
                    print r.get_sliver()
                    if r.get_sliver():
                        print urn, r.get_sliver().get_urn()
                        if r.get_sliver().get_urn() == urn:
                            result.append(r)
            return result            
        else:                
            return self.resources
        
    def create_resources(self, urns):
        result = list()
        for urn in urns:
            for r in self.resources:
                if r.get_sliver().get_urn() == urn :
                    if r.get_allocation_state() ==  "RESERVED":
                        r.set_allocation_state("provisioned")
                        result.append(r)
                        
        return result
    
    def reserve_resources(self, slice_urn, reservation, expiration):
        for res in reservation:
            res.set_allocation_state("RESERVED")
        self.resources.extend(reservation)       
        return True
    
    def start_resources(self, urns, geni_best_effort):
        result = list()
        for urn in urns:
            for r in self.resources:
                if r.get_sliver().get_urn() == urn :
                    r.set_operational_state = "STARTED"
                    result.append(r)
        return  result
    
    def stop_resources(self, urns, geni_best_effort):
        result = list()
        for urn in urns:
            for r in self.resources:
                if r.get_sliver().get_urn() == urn :
                    r.set_operational_state = "STOPPED"
                    result.append(r)
        return  result 
    
    def reboot_resources(self, urns, geni_best_effort):
        result = list()
        for urn in urns:
            for r in self.resources:
                if r.get_sliver().get_urn() == urn :
                    r.set_operational_state = "STARTED"
                    result.append(r)
        return  result

    
    def renew_resources(self, urns, geni_best_effort):
        return True
        