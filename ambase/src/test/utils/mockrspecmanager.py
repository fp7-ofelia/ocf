from src.abstract.classes.rspecmanager import RSpecManager

class MockRSpecManager(RSpecManager):
    
    def advertise_resources(self, resources):
        return self.__get_add()
    
    def manifest_slivers(self, slivers):
        return self.__get_man()
    
    def parse_request(self, rspec):
        return None
    
    def __get_add(self):
        return '''<?xml version="1.0" encoding="UTF-8"?>
                    <rspec xmlns="http://www.geni.net/resources/rspec/3"
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                    xsi:schemaLocation="http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/ad.xsd"
                    type="advertisement">
<node component_manager_id="urn:publicID:MYAUTHORITY"
                  component_name="0"
                  component_id="urn:publicID:ThisisaURNof0"
                  exclusive="true">
                  <available now="none"/>
                  </node>
               <node component_manager_id="urn:publicID:MYAUTHORITY"
                  component_name="1"
                  component_id="urn:publicID:ThisisaURNof1"
                  exclusive="true">
                  <available now="none"/>
                  </node>
               <node component_manager_id="urn:publicID:MYAUTHORITY"
                  component_name="2"
                  component_id="urn:publicID:ThisisaURNof2"
                  exclusive="true">
                  <available now="none"/>
                  </node>
               <node component_manager_id="urn:publicID:MYAUTHORITY"
                  component_name="3"
                  component_id="urn:publicID:ThisisaURNof3"
                  exclusive="true">
                  <available now="none"/>
                  </node>
               </rspec>'''
        
    def __get_man(self):
        return '''<?xml version="1.0" encoding="UTF-8"?>
                    <rspec xmlns="http://www.geni.net/resources/rspec/3"
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                    xsi:schemaLocation="http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/manifest.xsd"
                    type="manifest">
  <node client_id="None"
        component_id="None"
        component_manager_id="urn:publicID:ComponentManagerID120"
        sliver_id="urn:publicID:Sliver0"/>
  <node client_id="None"
        component_id="None"
        component_manager_id="urn:publicID:ComponentManagerID120"
        sliver_id="urn:publicID:Sliver0"/>
  <node client_id="None"
        component_id="None"
        component_manager_id="urn:publicID:ComponentManagerID120"
        sliver_id="urn:publicID:Sliver0"/>
</rspec>'''
        
    