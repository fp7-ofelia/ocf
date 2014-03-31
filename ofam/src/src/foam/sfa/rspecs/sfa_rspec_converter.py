#!/usr/bin/python

from foam.sfa.util.xrn import hrn_to_urn
from foam.sfa.rspecs.rspec import RSpec
from foam.sfa.rspecs.version_manager import VersionManager

class SfaRSpecConverter:

    @staticmethod
    def to_pg_rspec(rspec, content_type = None):
        if not isinstance(rspec, RSpec):
            sfa_rspec = RSpec(rspec)
        else:
            sfa_rspec = rspec
  
        if not content_type or content_type not in \
          ['ad', 'request', 'manifest']:
            content_type = sfa_rspec.version.content_type
     
 
        version_manager = VersionManager()
        pg_version = version_manager._get_version('protogeni', '2', 'request')
        pg_rspec = RSpec(version=pg_version)
 
        # get networks
        networks = sfa_rspec.version.get_networks()
        
        for network in networks:
            # get nodes
            sfa_node_elements = sfa_rspec.version.get_node_elements(network=network)
            for sfa_node_element in sfa_node_elements:
                # create node element
                node_attrs = {}
                node_attrs['exclusive'] = 'false'
                if 'component_manager_id' in sfa_node_element.attrib:
                    node_attrs['component_manager_id'] = sfa_node_element.attrib['component_manager_id']
                else:
                    node_attrs['component_manager_id'] = hrn_to_urn(network, 'authority+cm')

                if 'component_id' in sfa_node_element.attrib:
                    node_attrs['compoenent_id'] = sfa_node_element.attrib['component_id']

                if sfa_node_element.find('hostname') != None:
                    hostname = sfa_node_element.find('hostname').text
                    node_attrs['component_name'] = hostname
                    node_attrs['client_id'] = hostname
                node_element = pg_rspec.xml.add_element('node', node_attrs)    
            
                if content_type == 'request':
                    sliver_element = sfa_node_element.find('sliver')
                    sliver_type_elements = sfa_node_element.xpath('./sliver_type', namespaces=sfa_rspec.namespaces)
                    available_sliver_types = [element.attrib['name'] for element in sliver_type_elements]
                    valid_sliver_types = ['emulab-openvz', 'raw-pc']
                   
                    # determine sliver type 
                    requested_sliver_type = 'emulab-openvz'
                    for available_sliver_type in available_sliver_types:
                        if available_sliver_type in valid_sliver_types:
                            requested_sliver_type = available_sliver_type
                                
                    if sliver_element != None:
                        pg_rspec.xml.add_element('sliver_type', {'name': requested_sliver_type}, parent=node_element) 
                else:
                    # create node_type element
                    for hw_type in ['plab-pc', 'pc']:
                        hdware_type_element = pg_rspec.xml.add_element('hardware_type', {'name': hw_type}, parent=node_element)
                    # create available element
                    pg_rspec.xml.add_element('available', {'now': 'true'}, parent=node_element)
                    # create locaiton element
                    # We don't actually associate nodes with a country. 
                    # Set country to "unknown" until we figure out how to make
                    # sure this value is always accurate.
                    location = sfa_node_element.find('location')
                    if location != None:
                        location_attrs = {}      
                        location_attrs['country'] =  location.get('country', 'unknown')
                        location_attrs['latitude'] = location.get('latitude', 'None')
                        location_attrs['longitude'] = location.get('longitude', 'None')
                        pg_rspec.xml.add_element('location', location_attrs, parent=node_element)

        return pg_rspec.toxml()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:    
        print SfaRSpecConverter.to_pg_rspec(sys.argv[1])
