from xml.dom.minidom import parseString
from rspecs.src.geni.v3.container.resource import Resource
from rspecs.src.geni.v3.container.sliver import Sliver
from rspecs.src.geni.v3.container.link import Link

class ParserManager:
    
    def __init__(self):
        pass
    
    def parse_request_rspec(self,rspec):
        rspec_dom = parseString(rspec)
        resources = list()
        geni_nodes = rspec_dom.getElementsByTagName('node')
        geni_links = rspec_dom.getElementsByTagName('link')
        nodes = self.parse_nodes(geni_nodes)
        resources.extend(nodes)
        links = self.parse_links(geni_links)
        resources.extend(links)
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
       
    def parse_links(self, link_elems):
        links = list()
        for elem in link_elems:
            elem_attrs = elem.attributes
            link = Link()
            if elem_attrs.has_key("component_id"):
                link.set_component_id(elem_attrs.get("component_id").value)
            if elem_attrs.has_key("component_name"):
                link.set_component_id(elem_attrs.get("component_name").value)
            link_props = elem.getElementsByTagName("property")
            link_prop = link_props[0].attributes
            if link_prop.has_key("source_id"):
                link.set_source_id(link_prop.get("source_id").value)
            if link_prop.has_key("dest_id"):
                link.set_dest_id(link_prop.get("dest_id").value)
            if link_prop.has_key("capacity"):
                link.set_capacity(link_prop.get("capacity").value)
            link_type = elem.getElementsByTagName("link_type")[0].attributes
            if link_type.has_key("name"):
                link.set_type(link_type.get("name").value)
            links.append(link)
        return links        
