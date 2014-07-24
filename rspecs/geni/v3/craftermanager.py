class CrafterRSpecManager:
    
    #TODO: Take into account extensions
    
    def __init__(self, resources=[], options={}):
        self.resources = resources
        self.options = options
        self._urn_authority = "urn:publicID:MYAUTHORITY"
    
    def advert_template(self):
        tmpl = '''<node component_manager_id="%s" component_name="%s" component_id="%s" exclusive="%s">
<available now="%s"/>
</node>
'''
        return tmpl
    
    def advert_resource(self, resource):
        resource_id = str(resource.get_id())
        resource_exclusive = str(resource.get_exclusive()).lower()
        resource_available = str(resource.get_available()).lower()
        resource_urn = resource.get_urn()
        return self.advert_template() % (self._urn_authority,
                       resource_id,
                       resource_urn,
                       resource_exclusive,
                       resource_available)
    
    def advert_header(self):
        header = '''<?xml version="1.0" encoding="UTF-8"?>
<rspec xmlns="http://www.geni.net/resources/rspec/3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/ad.xsd" type="advertisement">\n'''
        return header
    
    def advert_footer(self):
        return '</rspec>\n'
    
    def manifest_header(self):
        header = '''<?xml version="1.0" encoding="UTF-8"?>
<rspec xmlns="http://www.geni.net/resources/rspec/3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/manifest.xsd" type="manifest">\n'''
        return header
    
    def manifest_template(self):
        template ='''  <node client_id="%s" component_id="%s" component_manager_id="%s" sliver_id="%s"/>\n'''
        return template    
    
    def manifest_slice(self, slice):
        result = ""
        for sliver in slice.get_slivers(): 
            for resource in sliver.get_resources():
                result += self.manifest_template() % (slice.get_client_id(), slice.get_component_id(),slice.get_component_manager_id(), sliver.get_urn())
        return result
    
    def manifest_footer(self):
        return '</rspec>\n'

