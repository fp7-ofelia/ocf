from foam.sfa.util.xrn import Xrn
from foam.sfa.rspecs.elements.element import Element
from foam.sfa.rspecs.elements.link import Link
from foam.sfa.rspecs.elements.interface import Interface
from foam.sfa.rspecs.elements.property import Property    

class PGv2Link:
    @staticmethod
    def add_links(xml, links):
        for link in links:
            
            link_elem = xml.add_instance('link', link, ['component_name', 'component_id', 'client_id'])
            # set component manager element            
            if 'component_manager' in link and link['component_manager']:
                cm_element = link_elem.add_element('component_manager', name=link['component_manager'])
            # set interface_ref elements
            if link.get('interface1') and link.get('interface2'):
                for if_ref in [link['interface1'], link['interface2']]:
                    link_elem.add_instance('interface_ref', if_ref, Interface.fields)
                # set property elements
                prop1 = link_elem.add_element('property', source_id = link['interface1']['component_id'],
                    dest_id = link['interface2']['component_id'], capacity=link['capacity'], 
                    latency=link['latency'], packet_loss=link['packet_loss'])
                prop2 = link_elem.add_element('property', source_id = link['interface2']['component_id'],
                    dest_id = link['interface1']['component_id'], capacity=link['capacity'], 
                    latency=link['latency'], packet_loss=link['packet_loss'])
            if link.get('type'):
                type_elem = link_elem.add_element('link_type', name=link['type'])            
 
    @staticmethod 
    def get_links(xml):
        links = []
        link_elems = xml.xpath('//default:link | //link')
        for link_elem in link_elems:
            # set client_id, component_id, component_name
            link = Link(link_elem.attrib, link_elem)

            # set component manager
            component_managers = link_elem.xpath('./default:component_manager | ./component_manager')
            if len(component_managers) > 0 and 'name' in component_managers[0].attrib:
                link['component_manager'] = component_managers[0].attrib['name']

            # set link type
            link_types = link_elem.xpath('./default:link_type | ./link_type')
            if len(link_types) > 0 and 'name' in link_types[0].attrib:
                link['type'] = link_types[0].attrib['name']
          
            # get capacity, latency and packet_loss from first property  
            property_fields = ['capacity', 'latency', 'packet_loss']
            property_elems = link_elem.xpath('./default:property | ./property')
            if len(property_elems) > 0:
                prop = property_elems[0]
                for attrib in ['capacity', 'latency', 'packet_loss']:
                    if attrib in prop.attrib:
                        link[attrib] = prop.attrib[attrib]
                             
            # get interfaces
            iface_elems = link_elem.xpath('./default:interface_ref | ./interface_ref')
            interfaces = [iface_elem.get_instance(Interface) for iface_elem in iface_elems]
            if len(interfaces) > 1:
                link['interface1'] = interfaces[0]
                link['interface2'] = interfaces[1] 
            links.append(link)
        return links 

    @staticmethod
    def add_link_requests(xml, link_tuples, append=False):
        if not isinstance(link_tuples, set):
            link_tuples = set(link_tuples)

        available_links = PGv2Link.get_links(xml)
        recently_added = []
        for link in available_links:
            if_name1 =  Xrn(link['interface1']['component_id']).get_leaf()
            if_name2 =  Xrn(link['interface2']['component_id']).get_leaf()
             
            requested_link = None
            l_tup_1 = (if_name1, if_name2)
            l_tup_2 = (if_name2, if_name1)
            if link_tuples.issuperset([(if_name1, if_name2)]):
                requested_link = (if_name1, if_name2)        
            elif link_tuples.issuperset([(if_name2, if_name2)]):
                requested_link = (if_name2, if_name1)
            if requested_link:
                # add client id to link ane interface elements 
                link.element.set('client_id', link['component_name'])
                link['interface1'].element.set('client_id', Xrn(link['interface1']['component_id']).get_leaf()) 
                link['interface2'].element.set('client_id', Xrn(link['interface2']['component_id']).get_leaf()) 
                recently_added.append(link['component_name'])

        if not append:
            # remove all links that don't have a client id 
            for link in PGv2Link.get_links(xml):
                if not link['client_id'] or link['component_name'] not in recently_added:
                    parent = link.element.getparent()
                    parent.remove(link.element)                  
             
    @staticmethod
    def get_link_requests(xml):
        link_requests = []
        for link in PGv2Link.get_links(xml):
            if link['client_id'] != None:
                link_requests.append(link)
        return link_requests           
