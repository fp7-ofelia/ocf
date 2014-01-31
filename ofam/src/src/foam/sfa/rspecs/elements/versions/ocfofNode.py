from foam.sfa.util.xrn import Xrn
from foam.sfa.util.xml import XpathFilter

from foam.sfa.rspecs.elements.node import Node
from foam.sfa.rspecs.elements.sliver import Sliver
from foam.sfa.rspecs.elements.versions.pgv2Services import PGv2Services     
from foam.sfa.rspecs.elements.versions.pgv2SliverType import PGv2SliverType     
from foam.sfa.rspecs.elements.versions.pgv2Interface import PGv2Interface     

def xrn_to_hostname(a=None,b=None):
	return a

class OcfOfNode:
    @staticmethod
    def add_nodes(xml, of_xml):

	network_elems = xml.xpath('//network')
        if len(network_elems) > 0:
            network_elem = network_elems[0]
        else:
            network_urn = 'ocf.ofam' 
            network_elem = xml #xml.add_element('network', name = Xrn(network_urn).get_hrn())

	nodes = of_xml.xpath('//rspec/*')
        for node in nodes:
	    network_elem.append(node)
        return nodes
    
    @staticmethod
    def add_slivers(xml, of_xml):
        network_elems = xml.xpath('//network')
        if len(network_elems) > 0:
            network_elem = network_elems[0]
        else:
            network_urn = 'ocf.ofam'
            network_elem = xml.add_element('network', name = Xrn(network_urn).get_hrn())

        slivers = of_xml.xpath('//rspec/*')
        for sliver in slivers:
            network_elem.append(sliver)
        return slivers
    @staticmethod
    def get_nodes(xml, filter={}):
        xpath = '//rspec/network/node'
	node_elems = xml.xpath(xpath)
        return OcfOfNode.get_node_objs(node_elems)

    @staticmethod
    def get_nodes_with_slivers(xml, filter={}):
	xpath = '//default:rspec/openflow:sliver'
        sliver_elems = xml.xpath(xpath)
	if not sliver_elems:
		sliver_elems = xml.xpath('//RSpec/network/sliver')
        return OcfOfNode.get_sliver_elems(sliver_elems)

    @staticmethod
    def get_sliver_elems(sliver_elems):
	slivers = list()
	for sliver in sliver_elems:
	    sliver_dict = dict()
	    sliver_dict.update(OcfOfNode._get_attrib_dict(sliver))
	    sliver_dict['controller'] = OcfOfNode.getControllers(sliver.xpath('./openflow:controller'))
	    sliver_dict['group'] = OcfOfNode.getGroups(sliver.xpath('./openflow:group')) 
	    sliver_dict['match'] = OcfOfNode.getMatchs(sliver.xpath('./openflow:match'))
	    slivers.append(sliver_dict)
	return slivers

    @staticmethod
    def _get_attrib_dict(element):
	if isinstance(element,list):
	   if len(element)>0:
		element = element[0]
	   else:
		return {}
	element_dict = dict()
	for attr in element.attrib.keys():
                element_dict[attr] = element.attrib[attr]
	return element_dict
		
    @staticmethod
    def getControllers(controller_elems):
	controllers = list()
	for controller in controller_elems:
	    controller_dict = OcfOfNode._get_attrib_dict(controller)
	    controllers.append(controller_dict)
	return controllers

    @staticmethod
    def getGroups(group_elems):
	groups = list()
	group_dict = dict()
	for group in group_elems:
	    group_dict.update(OcfOfNode._get_attrib_dict(group))
	    group_dict['datapath'] = OcfOfNode.getDatapaths(group.xpath('./openflow:datapath'))
	    groups.append(group_dict)	
	return groups

    @staticmethod
    def getDatapaths(datapath_elems):
	datapaths = list()
        for dp in datapath_elems:
	    dp_dict = dict()
	    dp_dict.update(OcfOfNode._get_attrib_dict(dp))
	    dp_dict['ports'] = OcfOfNode.getPorts(dp.xpath('./openflow:port'))
	    datapaths.append(dp_dict)
	return datapaths
	    
    @staticmethod
    def getPorts(port_elems):
	ports = list()
	for port in port_elems:
	    port_dict = OcfOfNode._get_attrib_dict(port)
	    ports.append(port_dict)
	return ports
		
    @staticmethod
    def getMatchs(match_elems):
	matchs = list()
	match_dict = dict()
	for match in match_elems:
	    match_dict['use-group'] = OcfOfNode.getUseGroups(match.xpath('./openflow:use-group'))
	    match_dict['datapath'] = OcfOfNode.getDatapaths(match.xpath('./openflow:datapath')) 
	    match_dict['packet'] = OcfOfNode.getPackets(match.xpath('./openflow:packet'))
	    matchs.append(match_dict)
	return matchs

    @staticmethod
    def getUseGroups(use_elements):
	use_groups = list()
        for use_group in use_elements:
		use_dict = OcfOfNode._get_attrib_dict(use_group)
		use_groups.append(use_dict)
	return use_groups

    @staticmethod
    def getPackets(packet_elems):
	packets = list()
	for packet in packet_elems:
            packet_dict = dict()
	    packet_dict['dl_src'] = OcfOfNode._get_attrib_dict(packet.xpath('./openflow:dl_src'))
	    packet_dict['dl_dst'] = OcfOfNode._get_attrib_dict(packet.xpath('./openflow:dl_dst'))
	    packet_dict['dl_type'] = OcfOfNode._get_attrib_dict(packet.xpath('./openflow:dl_type'))
	    packet_dict['dl_vlan'] = OcfOfNode._get_attrib_dict(packet.xpath('./openflow:dl_vlan'))
	    packet_dict['nw_src'] = OcfOfNode._get_attrib_dict(packet.xpath('./openflow:nw_src'))
	    packet_dict['nw_dst'] = OcfOfNode._get_attrib_dict(packet.xpath('./openflow:nw_dst'))
	    packet_dict['nw_proto'] = OcfOfNode._get_attrib_dict(packet.xpath('./openflow:nw_proto'))
	    packet_dict['tp_src'] = OcfOfNode._get_attrib_dict(packet.xpath('./openflow:tp_src'))
	    packet_dict['tp_dst'] = OcfOfNode._get_attrib_dict(packet.xpath('./openflow:tp_dst'))
	    packets.append(packet_dict)
	return packets
	    
	
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
    def remove_slivers(xml, hostnames):
        for hostname in hostnames:
            nodes = OcfOfNode.get_nodes(xml, {'component_id': '*%s*' % hostname})
            for node in nodes:
                slivers = OcfOfSliverType.get_slivers(node.element)
                for sliver in slivers:
                    node.element.remove(sliver.element) 
if __name__ == '__main__':
    from foam.sfa.rspecs.rspec import RSpec
    #import pdb
    r = RSpec('/tmp/emulab.rspec')
    r2 = RSpec(version = 'OcfOf')
    nodes = OcfOfNode.get_nodes(r.xml)
    OcfOfNode.add_nodes(r2.xml.root, nodes)
    #pdb.set_trace()
        
                                    
