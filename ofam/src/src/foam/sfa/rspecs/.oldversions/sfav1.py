from copy import deepcopy
from lxml import etree

from foam.sfa.util.sfalogging import logger
from foam.sfa.util.xrn import hrn_to_urn, urn_to_hrn
from foam.sfa.rspecs.version import RSpecVersion
from foam.sfa.rspecs.elements.element import Element
from foam.sfa.rspecs.elements.versions.pgv2Link import PGv2Link
from foam.sfa.rspecs.elements.versions.sfav1Node import SFAv1Node
from foam.sfa.rspecs.elements.versions.sfav1Sliver import SFAv1Sliver
from foam.sfa.rspecs.elements.versions.sfav1Lease import SFAv1Lease

class SFAv1(RSpecVersion):
    enabled = True
    type = 'SFA'
    content_type = '*'
    version = '1'
    schema = None
    namespace = None
    extensions = {}
    namespaces = None
    template = '<RSpec type="%s"></RSpec>' % type

    # Network 
    def get_networks(self):
        network_elems = self.xml.xpath('//network')
        networks = [network_elem.get_instance(fields=['name', 'slice']) for \
                    network_elem in network_elems]
        return networks    


    def add_network(self, network):
        network_tags = self.xml.xpath('//network[@name="%s"]' % network)
        if not network_tags:
            network_tag = self.xml.add_element('network', name=network)
        else:
            network_tag = network_tags[0]
        return network_tag


    # Nodes
    
    def get_nodes(self, filter=None):
        return SFAv1Node.get_nodes(self.xml, filter)

    def get_nodes_with_slivers(self):
        return SFAv1Node.get_nodes_with_slivers(self.xml)

    def add_nodes(self, nodes, network = None, no_dupes=False):
        SFAv1Node.add_nodes(self.xml, nodes)

    def merge_node(self, source_node_tag, network, no_dupes=False):
        if no_dupes and self.get_node_element(node['hostname']):
            # node already exists
            return

        network_tag = self.add_network(network)
        network_tag.append(deepcopy(source_node_tag))

    # Slivers
   
    def add_slivers(self, hostnames, attributes=[], sliver_urn=None, append=False):
        # add slice name to network tag
        network_tags = self.xml.xpath('//network')
        if network_tags:
            network_tag = network_tags[0]
            network_tag.set('slice', urn_to_hrn(sliver_urn)[0])

        # add slivers
        sliver = {'name':sliver_urn,
                  'pl_tags': attributes}
        for hostname in hostnames:
            if sliver_urn:
                sliver['name'] = sliver_urn
            node_elems = self.get_nodes({'component_id': '*%s*' % hostname})
            if not node_elems:
                continue
            node_elem = node_elems[0]
            SFAv1Sliver.add_slivers(node_elem.element, sliver)

        # remove all nodes without slivers
        if not append:
            for node_elem in self.get_nodes():
                if not node_elem['slivers']:
                    parent = node_elem.element.getparent()
                    parent.remove(node_elem.element)


    def remove_slivers(self, slivers, network=None, no_dupes=False):
        SFAv1Node.remove_slivers(self.xml, slivers)
 
    def get_slice_attributes(self, network=None):
        attributes = []
        nodes_with_slivers = self.get_nodes_with_slivers()
        for default_attribute in self.get_default_sliver_attributes(network):
            attribute = default_attribute.copy()
            attribute['node_id'] = None
            attributes.append(attribute)
        for node in nodes_with_slivers:
            nodename=node['component_name']
            sliver_attributes = self.get_sliver_attributes(nodename, network)
            for sliver_attribute in sliver_attributes:
                sliver_attribute['node_id'] = nodename
                attributes.append(sliver_attribute)
        return attributes


    def add_sliver_attribute(self, component_id, name, value, network=None):
        nodes = self.get_nodes({'component_id': '*%s*' % component_id})
        if nodes is not None and isinstance(nodes, list) and len(nodes) > 0:
            node = nodes[0]
            slivers = SFAv1Sliver.get_slivers(node)
            if slivers:
                sliver = slivers[0]
                SFAv1Sliver.add_sliver_attribute(sliver, name, value)
        else:
            # should this be an assert / raise an exception?
            logger.error("WARNING: failed to find component_id %s" % component_id)

    def get_sliver_attributes(self, component_id, network=None):
        nodes = self.get_nodes({'component_id': '*%s*' % component_id})
        attribs = []
        if nodes is not None and isinstance(nodes, list) and len(nodes) > 0:
            node = nodes[0]
            slivers = SFAv1Sliver.get_slivers(node.element)
            if slivers is not None and isinstance(slivers, list) and len(slivers) > 0:
                sliver = slivers[0]
                attribs = SFAv1Sliver.get_sliver_attributes(sliver.element)
        return attribs

    def remove_sliver_attribute(self, component_id, name, value, network=None):
        attribs = self.get_sliver_attributes(component_id)
        for attrib in attribs:
            if attrib['name'] == name and attrib['value'] == value:
                #attrib.element.delete()
                parent = attrib.element.getparent()
                parent.remove(attrib.element)

    def add_default_sliver_attribute(self, name, value, network=None):
        if network:
            defaults = self.xml.xpath("//network[@name='%s']/sliver_defaults" % network)
        else:
            defaults = self.xml.xpath("//sliver_defaults")
        if not defaults:
            if network:
                network_tag = self.xml.xpath("//network[@name='%s']" % network)
            else:
                network_tag = self.xml.xpath("//network")    
            if isinstance(network_tag, list):
                network_tag = network_tag[0]
            defaults = network_tag.add_element('sliver_defaults')
        elif isinstance(defaults, list):
            defaults = defaults[0]
        SFAv1Sliver.add_sliver_attribute(defaults, name, value)

    def get_default_sliver_attributes(self, network=None):
        if network:
            defaults = self.xml.xpath("//network[@name='%s']/sliver_defaults" % network)
        else:
            defaults = self.xml.xpath("//sliver_defaults")
        if not defaults: return []
        return SFAv1Sliver.get_sliver_attributes(defaults[0])
    
    def remove_default_sliver_attribute(self, name, value, network=None):
        attribs = self.get_default_sliver_attributes(network)
        for attrib in attribs:
            if attrib['name'] == name and attrib['value'] == value:
                #attrib.element.delete()
                parent = attrib.element.getparent()
                parent.remove(attrib.element)

    # Links

    def get_links(self, network=None):
        return PGv2Link.get_links(self.xml)

    def get_link_requests(self):
        return PGv2Link.get_link_requests(self.xml) 

    def add_links(self, links):
        networks = self.get_networks()
        if len(networks) > 0:
            xml = networks[0].element
        else:
            xml = self.xml
        PGv2Link.add_links(xml, links)

    def add_link_requests(self, links):
        PGv2Link.add_link_requests(self.xml, links)

    # utility

    def merge(self, in_rspec):
        """
        Merge contents for specified rspec with current rspec
        """

        if not in_rspec:
            return

        from foam.sfa.rspecs.rspec import RSpec
        if isinstance(in_rspec, RSpec):
            rspec = in_rspec
        else:
            rspec = RSpec(in_rspec)
        if rspec.version.type.lower() == 'protogeni':
            from foam.sfa.rspecs.rspec_converter import RSpecConverter
            in_rspec = RSpecConverter.to_sfa_rspec(rspec.toxml())
            rspec = RSpec(in_rspec)

        # just copy over all networks
        current_networks = self.get_networks()
        networks = rspec.version.get_networks()
        for network in networks:
            current_network = network.get('name')
            if current_network and current_network not in current_networks:
                self.xml.append(network.element)
                current_networks.append(current_network)

    # Leases

    def get_leases(self, filter=None):
        return SFAv1Lease.get_leases(self.xml, filter)

    def add_leases(self, leases, network = None, no_dupes=False):
        SFAv1Lease.add_leases(self.xml, leases)

if __name__ == '__main__':
    from foam.sfa.rspecs.rspec import RSpec
    from foam.sfa.rspecs.rspec_elements import *
    r = RSpec('/tmp/resources.rspec')
    r.load_rspec_elements(SFAv1.elements)
    print r.get(RSpecElements.NODE)
