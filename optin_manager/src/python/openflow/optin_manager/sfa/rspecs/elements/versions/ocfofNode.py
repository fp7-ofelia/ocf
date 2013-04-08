from openflow.optin_manager.sfa.util.xrn import Xrn
from openflow.optin_manager.sfa.util.xml import XpathFilter

from openflow.optin_manager.sfa.rspecs.elements.node import Node
from openflow.optin_manager.sfa.rspecs.elements.sliver import Sliver
from openflow.optin_manager.sfa.rspecs.elements.location import Location
from openflow.optin_manager.sfa.rspecs.elements.ocf_vt_server import OcfVtServer
from openflow.optin_manager.sfa.rspecs.elements.hardware_type import HardwareType
from openflow.optin_manager.sfa.rspecs.elements.disk_image import DiskImage
from openflow.optin_manager.sfa.rspecs.elements.interface import Interface
from openflow.optin_manager.sfa.rspecs.elements.bwlimit import BWlimit
from openflow.optin_manager.sfa.rspecs.elements.pltag import PLTag
from openflow.optin_manager.sfa.rspecs.elements.versions.pgv2Services import PGv2Services     
from openflow.optin_manager.sfa.rspecs.elements.versions.pgv2SliverType import PGv2SliverType     
from openflow.optin_manager.sfa.rspecs.elements.versions.pgv2Interface import PGv2Interface     

def xrn_to_hostname(a=None,b=None):
	return a

class OcfOfNode:
    @staticmethod
    def add_nodes(xml, of_xml):

	network_elems = xml.xpath('//network')
        if len(network_elems) > 0:
            network_elem = network_elems[0]
        else:
            network_urn = 'ocf_of' 
            network_elem = xml.add_element('network', name = Xrn(network_urn).get_hrn())

	nodes = of_xml.xpath('//rspec/*')
        for node in nodes:
	    network_elem.append(node)
        return nodes

    @staticmethod
    def get_nodes(xml, filter={}):
        #xpath = '//node%s | //default:node%s' % (XpathFilter.xpath(filter), XpathFilter.xpath(filter))
        xpath = '//rspec/network/node'
	node_elems = xml.xpath(xpath)
        return OcfOfNode.get_node_objs(node_elems)

    @staticmethod
    def get_nodes_with_slivers(xml, filter={}):
        #xpath = '//node[count(sliver-type)>0] | //default:node[count(default:sliver-type) > 0]' 
	xpath = '//rspec/network/node'
        node_elems = xml.xpath(xpath)
	if not node_elems:
		node_elems = xml.xpath('//RSpec/network/node')
        return OcfOfNode.get_node_objs(node_elems)

    @staticmethod
    def get_node_objs(node_elems):
        nodes = []
        for node_elem in node_elems:
            node = Node(node_elem.attrib, node_elem)
            nodes.append(node)
	   
            if 'component_id' in node_elem.attrib:
                node['authority_id'] = Xrn(node_elem.attrib['component_id']).get_authority_urn()
            
            # get hardware types
            hardware_type_elems = node_elem.xpath('./hardware_type | ./default:hardware_type')
            node['hardware_types'] = [hw_type.get_instance(HardwareType) for hw_type in hardware_type_elems]
            
            # get location
            location_elems = node_elem.xpath('./location | ./default:location')
            locations = [location_elem.get_instance(Location) for location_elem in location_elems]
            if len(locations) > 0:
                node['location'] = locations[0]

            # get interfaces
            iface_elems = node_elem.xpath('./interface | ./default:interface')
            node['interfaces'] = [iface_elem.get_instance(Interface) for iface_elem in iface_elems]

            # get services
	    service_elems = node_elem.xpath('./services | ./default:service')
	    if service_elems:
            	node['services'] = PGv2Services.get_services(node_elem)
            
            # get slivers
	    sliver_elems = node_elem.xpath('./sliver | ./default:slivers')
	    if sliver_elems:
                node['slivers'] = OcfOfSlivers.get_slivers(sliver_elems)
	
            available_elems = node_elem.xpath('./available | ./default:available')
            if len(available_elems) > 0 and 'name' in available_elems[0].attrib:
                if available_elems[0].attrib.get('now', '').lower() == 'true': 
                    node['boot_state'] = 'boot'
                else: 
                    node['boot_state'] = 'disabled' 

        return nodes


    @staticmethod
    def add_slivers(xml, slivers):
        component_ids = []
        for sliver in slivers:
            filter = {}
            if isinstance(sliver, str):
                filter['component_id'] = '*%s*' % sliver
                sliver = {}
            elif 'component_id' in sliver and sliver['component_id']:
                filter['component_id'] = '*%s*' % sliver['component_id']
            if not filter: 
                continue
            nodes = OcfOfNode.get_nodes(xml, filter)
            if not nodes:
                continue
            node = nodes[0]
            PGv2SliverType.add_slivers(node, sliver)

    @staticmethod
    def remove_slivers(xml, hostnames):
        for hostname in hostnames:
            nodes = OcfOfNode.get_nodes(xml, {'component_id': '*%s*' % hostname})
            for node in nodes:
                slivers = OcfOfSliverType.get_slivers(node.element)
                for sliver in slivers:
                    node.element.remove(sliver.element) 
if __name__ == '__main__':
    from openflow.optin_manager.sfa.rspecs.rspec import RSpec
    #import pdb
    r = RSpec('/tmp/emulab.rspec')
    r2 = RSpec(version = 'OcfOf')
    nodes = OcfOfNode.get_nodes(r.xml)
    OcfOfNode.add_nodes(r2.xml.root, nodes)
    #pdb.set_trace()
        
                                    
