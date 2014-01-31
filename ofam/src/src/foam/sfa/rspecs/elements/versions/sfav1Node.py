from foam.sfa.util.sfalogging import logger
from foam.sfa.util.xml import XpathFilter
from foam.sfa.util.xrn import Xrn

from foam.sfa.rspecs.elements.element import Element
from foam.sfa.rspecs.elements.node import Node
from foam.sfa.rspecs.elements.sliver import Sliver
from foam.sfa.rspecs.elements.location import Location
from foam.sfa.rspecs.elements.hardware_type import HardwareType
from foam.sfa.rspecs.elements.disk_image import DiskImage
from foam.sfa.rspecs.elements.interface import Interface
from foam.sfa.rspecs.elements.bwlimit import BWlimit
from foam.sfa.rspecs.elements.pltag import PLTag
from foam.sfa.rspecs.elements.versions.sfav1Sliver import SFAv1Sliver
from foam.sfa.rspecs.elements.versions.sfav1PLTag import SFAv1PLTag
from foam.sfa.rspecs.elements.versions.pgv2Services import PGv2Services

from sfa.planetlab.plxrn import xrn_to_hostname

class SFAv1Node:

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
            node_fields = ['component_manager_id', 'component_id', 'boot_state']
            node_elem = network_elem.add_instance('node', node, node_fields)
            node_elems.append(node_elem)

            # determine network hrn
            network_hrn = None 
            if 'component_manager_id' in node and node['component_manager_id']:
                network_hrn = Xrn(node['component_manager_id']).get_hrn()

            # set component_name attribute and  hostname element
            if 'component_id' in node and node['component_id']:
                component_name = xrn_to_hostname(node['component_id'])
                node_elem.set('component_name', component_name)
                hostname_elem = node_elem.add_element('hostname')
                hostname_elem.set_text(component_name)

            # set site id
            if 'authority_id' in node and node['authority_id']:
                node_elem.set('site_id', node['authority_id'])

            # add locaiton
            location = node.get('location')
            if location:
                node_elem.add_instance('location', location, Location.fields)

            # add exclusive tag to distinguish between Reservable and Shared nodes
            exclusive_elem = node_elem.add_element('exclusive')
            if node.get('exclusive') and node.get('exclusive') == 'true':
                exclusive_elem.set_text('TRUE')
                # add granularity of the reservation system
                granularity = node.get('granularity')
                if granularity:
                    node_elem.add_instance('granularity', granularity, granularity.fields)
            else:
                exclusive_elem.set_text('FALSE')


            if isinstance(node.get('interfaces'), list):
                for interface in node.get('interfaces', []):
                    node_elem.add_instance('interface', interface, ['component_id', 'client_id', 'ipv4']) 
            
            #if 'bw_unallocated' in node and node['bw_unallocated']:
            #    bw_unallocated = etree.SubElement(node_elem, 'bw_unallocated', units='kbps').text = str(int(node['bw_unallocated'])/1000)

            PGv2Services.add_services(node_elem, node.get('services', []))
            tags = node.get('tags', [])
            if tags:
                for tag in tags:
                    tag_elem = node_elem.add_element(tag['tagname'])
                    tag_elem.set_text(tag['value'])
            SFAv1Sliver.add_slivers(node_elem, node.get('slivers', []))

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
            nodes = SFAv1Node.get_nodes(xml, filter)
            if not nodes:
                continue
            node = nodes[0]
            SFAv1Sliver.add_slivers(node, sliver)

    @staticmethod
    def remove_slivers(xml, hostnames):
        for hostname in hostnames:
            nodes = SFAv1Node.get_nodes(xml, {'component_id': '*%s*' % hostname})
            for node in nodes:
                slivers = SFAv1Sliver.get_slivers(node.element)
                for sliver in slivers:
                    node.element.remove(sliver.element)
        
    @staticmethod
    def get_nodes(xml, filter={}):
        xpath = '//node%s | //default:node%s' % (XpathFilter.xpath(filter), XpathFilter.xpath(filter))
        node_elems = xml.xpath(xpath)
        return SFAv1Node.get_node_objs(node_elems)

    @staticmethod
    def get_nodes_with_slivers(xml):
        xpath = '//node[count(sliver)>0] | //default:node[count(default:sliver)>0]' 
        node_elems = xml.xpath(xpath)
        return SFAv1Node.get_node_objs(node_elems)


    @staticmethod
    def get_node_objs(node_elems):
        nodes = []    
        for node_elem in node_elems:
            node = Node(node_elem.attrib, node_elem)
            if 'site_id' in node_elem.attrib:
                node['authority_id'] = node_elem.attrib['site_id']
            # get location
            location_elems = node_elem.xpath('./default:location | ./location')
            locations = [loc_elem.get_instance(Location) for loc_elem in location_elems]  
            if len(locations) > 0:
                node['location'] = locations[0]
            # get bwlimit
            bwlimit_elems = node_elem.xpath('./default:bw_limit | ./bw_limit')
            bwlimits = [bwlimit_elem.get_instance(BWlimit) for bwlimit_elem in bwlimit_elems]
            if len(bwlimits) > 0:
                node['bwlimit'] = bwlimits[0]
            # get interfaces
            iface_elems = node_elem.xpath('./default:interface | ./interface')
            ifaces = [iface_elem.get_instance(Interface) for iface_elem in iface_elems]
            node['interfaces'] = ifaces
            # get services
            node['services'] = PGv2Services.get_services(node_elem) 
            # get slivers
            node['slivers'] = SFAv1Sliver.get_slivers(node_elem)
            # get tags
            node['tags'] =  SFAv1PLTag.get_pl_tags(node_elem, ignore=Node.fields+["hardware_type"])
            # get hardware types
            hardware_type_elems = node_elem.xpath('./default:hardware_type | ./hardware_type')
            node['hardware_types'] = [hw_type.get_instance(HardwareType) for hw_type in hardware_type_elems]

            # temporary... play nice with old slice manager rspec
            if not node['component_name']:
                hostname_elem = node_elem.find("hostname")
                if hostname_elem != None:
                    node['component_name'] = hostname_elem.text

            nodes.append(node)
        return nodes            

