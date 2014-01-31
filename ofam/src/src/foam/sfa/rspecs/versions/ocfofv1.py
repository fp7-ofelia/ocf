from copy import deepcopy
from StringIO import StringIO
from foam.sfa.util.xrn import Xrn
from foam.sfa.rspecs.version import RSpecVersion
#from foam.sfa.rspecs.elements.versions.pgv2Link import PGv2Link

from  foam.sfa.rspecs.elements.versions.ocfofNode import OcfOfNode
 
class OcfOf(RSpecVersion):
    type = 'OcfOf'
    content_type = 'ad'
    version = '1'
    schema = 'https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/openflow/schemas/of-resv-3.xsd'  
    namespace = None
    content = '*'
    extensions = {}
    namespaces = None 

    # Networks
    def get_networks(self):
        network_elems = self.xml.xpath('//default:rspec/default:network')
        networks = [network_elem.get_instance(fields=['name', 'slice']) for \
                    network_elem in network_elems]
        return networks
    # Nodes

    def get_nodes(self, filter=None):
        return OcfOfNode.get_nodes(self.xml, filter)

    def get_nodes_with_slivers(self):
        return OcfOfNode.get_nodes_with_slivers(self.xml)

    def add_nodes(self,of_xml):
        return OcfOfNode.add_nodes(self.xml,of_xml)

    def add_slivers(self,of_xml):
        return OcfOfNode.add_slivers(self.xml, of_xml)
    
    def merge_node(self, source_node_tag):
        # this is untested
        self.xml.root.append(deepcopy(source_node_tag))

    # Slivers
    
    def get_sliver_attributes(self,node):
	#XXX:I will get node[slivers] and the node ids to get all the information to create a vm.
	attribs = dict()
	attribs.update({'slivers':node['slivers'],'component_id':node['component_id'],'component_name':node['component_name']})


        return attribs

    def get_slice_attributes(self, network=None):
	slice_attributes= list()
        nodes_with_slivers = self.get_nodes_with_slivers()
        return nodes_with_slivers

    def attributes_list(self, elem):
        opts = []
        if elem is not None:
            for e in elem:
                opts.append((e.tag, str(e.text).strip(), e.attrib))
        return opts

    def get_default_sliver_attributes(self, network=None):
        return []

    def add_default_sliver_attribute(self, name, value, network=None):
        pass

    def get_links(self, network=None):
	return []

    def get_link_requests(self):
        return []  

    def add_links(self, links):
	return []

    def add_link_requests(self, link_tuples, append=False):
	return []
    # Leases

    def get_leases(self, filter=None):
        return []

    def add_leases(self, leases, network = None, no_dupes=False):
        return []

    # Utility

    def merge(self, in_rspec):
        """
        Merge contents for specified rspec with current rspec
        """
        if not in_rspec:
           return None

        from sfa.rspecs.rspec import RSpec
        # just copy over all the child elements under the root element
        if isinstance(in_rspec, basestring):
            in_rspec = RSpec(in_rspec)
        if str(in_rspec.version) == 'OcfOf 1':
            networks = in_rspec.xml.xpath('//rspec/network')
            for network in networks:
                self.xml.xpath('//rspec')[0].append(network)
        else: 
            nodes = in_rspec.version.get_nodes()
            for node in nodes: 
                if not node.has_key('sliver') or not node['sliver']:
                    node['sliver'] = {'name': 'plab-vserver'}

            self.add_nodes(nodes) 
            self.add_links(in_rspec.version.get_links())
        
        #
        #rspec = RSpec(in_rspec)
        #for child in rspec.xml.iterchildren():
        #    self.xml.root.append(child)
        
        

    def cleanup(self):
        # remove unncecessary elements, attributes
        if self.type in ['request', 'manifest']:
            # remove 'available' element from remaining node elements
            self.xml.remove_element('//default:available | //available')

class OcfOfAd(OcfOf):
    enabled = True
    content_type = 'ad'
    schema ='https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/openflow/schemas/ad.xsd'
    template = '<rspec type="advertisement" xmlns="https://github.com/fp7-ofelia/ocf/tree/ocf.rspecs/openflow/schemas" xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xmlns:openflow="https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/openflow/schemas" xs:schemaLocation="https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/openflow/schemas/ https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/openflow/schemas/ad.xsd  http://www.geni.net/resources/rspec/3/ad.xsd https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/openflow/schemas/ad.xsd http://www.geni.net/resources/rspec/ext/openflow/3/of-ad.xsd https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/openflow/schemas/network_schema.xsd" />'

class OcfOfRequest(OcfOf):
    enabled = True
    content_type = 'request'
    schema = 'http://www.geni.net/resources/rspec/3/request.xsd'
    template = '<rspec xmlns="http://www.geni.net/resources/rspec/3" xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xmlns:openflow="http://www.geni.net/resources/rspec/ext/openflow/3" xs:schemaLocation="http://www.geni.net/resources/rspec/3 http://www.geni.net/resources/rspec/3/request.xsd http://www.geni.net/resources/rspec/ext/openflow/3 http://www.geni.net/resources/rspec/ext/openflow/3/of-resv.xsd https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/openflow/schemas/network_schema.xsd" type="request" />'

class OcfOfManifest(OcfOf):
    enabled = True
    content_type = 'manifest'
    schema = 'https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/openflow/schemas/manifest.xsd'
    template = '<rspec type="manifest" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.protogeni.net/resources/rspec/2 https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/openflow/schemas/manifest.xsd http://www.protogeni.net/resources/rspec/2/ad.xsd https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/openflow/schemas/network_schema.xsd"/>'
     


if __name__ == '__main__':
    from foam.sfa.rspecs.rspec import RSpec
    from foam.sfa.rspecs.rspec_elements import *
    r = RSpec('/tmp/ocf.rspec')
    r.load_rspec_elements(OcfOf.elements)
    print r.get(RSpecElements.NODE)
