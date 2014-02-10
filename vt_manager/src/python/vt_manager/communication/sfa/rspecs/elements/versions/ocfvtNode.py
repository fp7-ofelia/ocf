from vt_manager.communication.sfa.util.xrn import Xrn
from vt_manager.communication.sfa.util.xml import XpathFilter

from vt_manager.communication.sfa.rspecs.elements.node import Node
from vt_manager.communication.sfa.rspecs.elements.sliver import Sliver
from vt_manager.communication.sfa.rspecs.elements.location import Location
from vt_manager.communication.sfa.rspecs.elements.ocf_vt_server import OcfVtServer
from vt_manager.communication.sfa.rspecs.elements.hardware_type import HardwareType
from vt_manager.communication.sfa.rspecs.elements.disk_image import DiskImage
from vt_manager.communication.sfa.rspecs.elements.interface import Interface
from vt_manager.communication.sfa.rspecs.elements.bwlimit import BWlimit
from vt_manager.communication.sfa.rspecs.elements.pltag import PLTag
from vt_manager.communication.sfa.rspecs.elements.versions.pgv2Services import PGv2Services     
from vt_manager.communication.sfa.rspecs.elements.versions.pgv2SliverType import PGv2SliverType     
from vt_manager.communication.sfa.rspecs.elements.versions.pgv2Interface import PGv2Interface     


from vt_manager.communication.sfa.rspecs.elements.range import Range
from vt_manager.communication.sfa.rspecs.elements.network_interface import NetworkInterface
from vt_manager.communication.sfa.rspecs.elements.versions.ocfvtSlivers import OcfVtSlivers

#from sfa.util.sfalogging import logger

#from sfa.planetlab.plxrn import xrn_to_hostname
def xrn_to_hostname(a=None,b=None):
	return a

class OcfVtNode:
    @staticmethod
    def add_nodes(xml, nodes):

	network_elems = xml.xpath('//network')
        if len(network_elems) > 0:
            network_elem = network_elems[0]
        elif len(nodes) > 0 and nodes[0].get('component_manager_id'):
            network_urn = nodes[0]['component_manager_id']
            network_elem = xml.add_element('network', name = Xrn(network_urn).get_hrn())
        else:
            network_elem = xml

	
        node_elems = []
        for node in nodes:
            node_fields = ['component_manager_id', 'component_id', 'client_id', 'sliver_id', 'exclusive']
            node_elem = network_elem.add_instance('node', node, node_fields)
            node_elems.append(node_elem)
            # set component name
            if node.get('component_id'):
                component_name = node['component_id']
                node_elem.set('component_name', component_name)
	    if node.get('hostname'):
                        simple_elem = node_elem.add_element('hostname')
                        simple_elem.set_text(node['hostname'])
            # set hardware types
	    
            if node.get('hardware_types'):
                for hardware_type in node.get('hardware_types', []):
		    for field in OcfVtServer.fields:	
		        #node_elem.add_instance(field,{field:hardware_type[field]},[])#XXX Ugly notation
			simple_elem = node_elem.add_element(field)
			simple_elem.set_text(hardware_type[field])
            # set location
            if node.get('location'):
                node_elem.add_instance('location', node['location'], Location.fields)       
            # set interfaces
            PGv2Interface.add_interfaces(node_elem, node.get('interfaces'))
            #if node.get('interfaces'):
            #    for interface in  node.get('interfaces', []):
            #        node_elem.add_instance('interface', interface, ['component_id', 'client_id'])
            # set available element
            if node.get('boot_state'):
                if node.get('boot_state').lower() == 'boot':
                    available_elem = node_elem.add_element('available', now='true')
                else:
                    available_elem = node_elem.add_element('available', now='false')
            # add services
	    if node.get('services'):
		for service in node.get('services',[]):
		   fields = service.fields
		   s = node_elem.add_element('service', type=str(service.__class__.__name__))
		   for field in fields:
			if service[field]:
				simple_elem = s.add_element(field)#node_elem.add_element(field)
                        	simple_elem.set_text(service[field])
            #PGv2Services.add_services(node_elem, node.get('services', [])) 
            # add slivers
            slivers = node.get('slivers', [])
            if slivers:
		for sliver in slivers:
			fields = sliver.fields
			s = node_elem.add_element('sliver', type=str(sliver.__class__.__name__))
			for field in fields:
				if sliver[field]:
					simple_elem = s.add_element(field)#node_elem.add_element(field)
                                	simple_elem.set_text(sliver[field])

                # we must still advertise the available sliver types
                #slivers = Sliver({'type': 'plab-vserver'})
                # we must also advertise the available initscripts
                #slivers['tags'] = []
                #if node.get('pl_initscripts'): 
                #    for initscript in node.get('pl_initscripts', []):
                #        slivers['tags'].append({'name': 'initscript', 'value': initscript['name']})
            #PGv2SliverType.add_slivers(node_elem, slivers)
        return node_elems

    @staticmethod
    def get_nodes(xml, filter={}):
        #xpath = '//node%s | //default:node%s' % (XpathFilter.xpath(filter), XpathFilter.xpath(filter))
        xpath = '//rspec/network/node'
	node_elems = xml.xpath(xpath)
        return OcfVtNode.get_node_objs(node_elems)

    @staticmethod
    def get_nodes_with_slivers(xml, filter={}):
        #xpath = '//node[count(sliver-type)>0] | //default:node[count(default:sliver-type) > 0]' 
	xpath = '//rspec/network/node'
        node_elems = xml.xpath(xpath)
	if not node_elems:
		node_elems = xml.xpath('//RSpec/network/node')
        return OcfVtNode.get_node_objs(node_elems)

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
                node['slivers'] = OcfVtSlivers.get_slivers(sliver_elems)
	
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
            nodes = OcfVtNode.get_nodes(xml, filter)
            if not nodes:
                continue
            node = nodes[0]
            PGv2SliverType.add_slivers(node, sliver)

    @staticmethod
    def remove_slivers(xml, hostnames):
        for hostname in hostnames:
            nodes = OcfVtNode.get_nodes(xml, {'component_id': '*%s*' % hostname})
            for node in nodes:
                slivers = OcfVtSliverType.get_slivers(node.element)
                for sliver in slivers:
                    node.element.remove(sliver.element) 
if __name__ == '__main__':
    from vt_manager.communication.sfa.rspecs.rspec import RSpec
    #import pdb
    r = RSpec('/tmp/emulab.rspec')
    r2 = RSpec(version = 'OcfVt')
    nodes = OcfVtNode.get_nodes(r.xml)
    OcfVtNode.add_nodes(r2.xml.root, nodes)
    #pdb.set_trace()
        
                                    
