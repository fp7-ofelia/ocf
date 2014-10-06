from xml.dom.minidom import parseString
from rspecs.src.geni.v3.container.resource import Resource
from rspecs.src.geni.v3.container.sliver import Sliver

class ParserManager:
    
    def __init__(self):
        pass
    
    def parse_request_rspec(self,rspec):
        rspec_dom = parseString(rspec)
        nodes = rspec_dom.getElementsByTagName('node')
        resources = self.parse_nodes(nodes)
        return resources
    
    def parse_nodes(self, nodes):
        vms = list()
        for element in nodes:
            node = element.attributes
            resource = Resource()
            sliver = Sliver()
            if node.has_key('client_id'):
                resource.set_id(node.get('client_id').value)
            if node.has_key('interfaces'):
                pass #Implement when needed    
            if node.has_key('component_manager_id'):
                resource.set_component_manager_id(node.get('component_manager_id').value)
                
            if node.has_key('component_manager_name'):
                resource.set_component_manager_name(node.get('component_manager_name').value)
                
            if node.has_key('component_id'):
                resource.set_component_id(node.get('component_id').value)
                
            if node.has_key('component_name'):
                resource.set_component_id(node.get('component_name').value)
                
            if node.has_key('services'):
                pass #Implement when needed
          
            slivers = element.getElementsByTagName("sliver_type")
            for sliver_elem in slivers:
                sliver = Sliver()
                attrs = sliver_elem.attributes
                if attrs.has_key('name'):
                    sliver.set_name(attrs.get('name').value)
                    
                sliver.set_resource(resource)
                resource.set_sliver(sliver)
            
            vms.append(resource)
        
        return vms
       
