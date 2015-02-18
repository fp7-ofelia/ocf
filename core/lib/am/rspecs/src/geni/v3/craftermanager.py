from rspecs.src.geni.v3.container.resource import Resource
from rspecs.src.geni.v3.container.link import Link
class CrafterManager:
    
    #TODO: Take into account extensions
    
    def __init__(self, resources=[], options={}):
        self.resources = resources
        self.options = options
        self._urn_authority = "urn:publicID:MYAUTHORITY"
        
    def get_advertisement(self, resources):
        """
        Return advertisement with information of resources.
        """
        output = self.advert_header()
        for resource in resources: 
            output += self.advert_resource(resource)
        output += self.advert_footer()
        return output    
    
    def advert_node_template(self):
        tmpl = """<node component_manager_id="%s" component_name="%s" component_id="%s" exclusive="%s">
<available now="%s"/>
</node>
"""
        return tmpl
    
    def advert_link_template(self):
        tmpl = '''<link component_id="%s" component_name="%s">
<property source_id="%s" dest_id="%s" capacity="%s"/>
<link_type name="%s"/>
</link> '''
        return tmpl
    
    def advert_resource(self,resource):
        resource_dir = dir(resource)
        if resource_dir == dir(Link()):
            return self.advert_link(resource)
        elif resource_dir == dir(Resource()):
            return self.advert_node(resource)
        else:
            return ""
        
        
    def advert_node(self, resource):
        resource_component_manager_id = str(resource.get_component_manager_id())
        resource_exclusive = str(resource.get_exclusive()).lower()
        resource_available = str(resource.get_available()).lower()
        resource_component_name = resource.get_component_name()
        resource_component_id = resource.get_component_id()
        return self.advert_node_template() % (resource_component_manager_id,
                       resource_component_name,
                       resource_component_id,
                       resource_exclusive,
                       resource_available)
    
    def advert_link(self, link):
        resource_component_name = link.get_component_name()
        resource_component_id = link.get_component_id()
        resource_source_id = link.get_source_id()
        resource_dest_id = link.get_dest_id()
        resource_capacity = link.get_capacity()
        resource_type = link.get_type()
        return self.advert_link_template() % (resource_component_id, 
                                              resource_component_name, 
                                              resource_source_id, 
                                              resource_dest_id,
                                              str(resource_capacity),
                                              resource_type)
        
    
    def advert_header(self):
        header = """<?xml version="1.0" encoding="UTF-8"?>
<rspec xmlns="http://www.geni.net/resources/rspec/3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/ad.xsd" type="advertisement">\n"""
        return header
    
    def advert_footer(self):
        return "</rspec>\n"
    
    def manifest_header(self):
        header = """<?xml version="1.0" encoding="UTF-8"?>
<rspec xmlns="http://www.geni.net/resources/rspec/3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/manifest.xsd" type="manifest">\n"""
        return header
    
    def manifest_template(self):
        template ="""<node client_id="%s" component_id="%s" component_manager_id="%s" sliver_id="%s">\n"""
        return template    
    
    def manifest_node_close_template(self):
        template ="""</node>\n"""
        return template
    
    def manifest_sliver_type_template(self):
        template = """<sliver_type name="%s"/>\n"""
        return template
    
    def manifest_services_template(self):
        template = """<services>\n<login authentication="ssh-keys" hostname="%s" port="22" username="%s"/>\n</services>\n"""
        return template
    
    def manifest_services_template_root(self):
        # BasicAuth for root; PKI for others
        template = """<services>\n<login authentication="ssh" hostname="%s" port="22" username="root:openflow"/>\n</services>\n"""
        return template
        
    def manifest_slivers(self, resources):
        """
        Return manifest with information of slivers.
        """
        result = self.manifest_header()
        for resource in resources:
            sliver = resource.get_sliver() 
            result += self.manifest_template() % (sliver.get_client_id(), resource.get_component_id(), resource.get_component_manager_id(), sliver.get_urn())
            if sliver.get_type():
                result += self.manifest_sliver_type_template() % (sliver.get_type())
            if sliver.get_services():
                services = sliver.get_services()
                for service in services:
                    if service["login"]["username"].startswith("root:"):
                        result += self.manifest_services_template_root() % service["login"]["hostname"]
                    else:
                        result += self.manifest_services_template() % (service["login"]["hostname"], service["login"]["username"])
            result += self.manifest_node_close_template()
        result += self.manifest_footer()
        return result
    
    def manifest_footer(self):
        return "</rspec>\n"

