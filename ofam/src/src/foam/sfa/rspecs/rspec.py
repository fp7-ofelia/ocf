#!/usr/bin/python 
from datetime import datetime, timedelta

from foam.sfa.util.xml import XML, XpathFilter
from foam.sfa.util.faults import InvalidRSpecElement, InvalidRSpec

from foam.sfa.rspecs.rspec_elements import RSpecElement, RSpecElements 
from foam.sfa.rspecs.version_manager import VersionManager

class RSpec:
 
    def __init__(self, rspec="", version=None, user_options={}):
        self.header = '<?xml version="1.0"?>\n'
        self.template = """<RSpec></RSpec>"""
        self.version = None
        self.xml = XML()
        self.version_manager = VersionManager()
        self.user_options = user_options
        self.elements = {}
        if rspec:
            if version:
                self.version = self.version_manager.get_version(version)
                self.parse_xml(rspec, version)
            else:
                self.parse_xml(rspec)
        elif version:
            self.create(version)
        else:
            raise InvalidRSpec("No RSpec or version specified. Must specify a valid rspec string or a valid version") 
    def create(self, version=None):
        """
        Create root element
        """
        self.version = self.version_manager.get_version(version)
        self.namespaces = self.version.namespaces
        self.parse_xml(self.version.template, self.version) 
        # eg. 2011-03-23T19:53:28Z 
        date_format = '%Y-%m-%dT%H:%M:%SZ'
        now = datetime.utcnow()
        generated_ts = now.strftime(date_format)
        expires_ts = (now + timedelta(hours=1)).strftime(date_format) 
        self.xml.set('expires', expires_ts)
        self.xml.set('generated', generated_ts)


    def parse_xml(self, xml, version=None):
        self.xml.parse_xml(xml)
        if not version:
            if self.xml.schema:
                self.version = self.version_manager.get_version_by_schema(self.xml.schema)
            else:
                #raise InvalidRSpec('unknown rspec schema: %s' % schema)
                # TODO: Should start raising an exception once SFA defines a schema.
                # for now we just  default to sfa 
                self.version = self.version_manager.get_version({'type':'sfa','version': '1'})
        self.version.xml = self.xml    
        self.namespaces = self.xml.namespaces
    
    def load_rspec_elements(self, rspec_elements):
        self.elements = {}
        for rspec_element in rspec_elements:
            if isinstance(rspec_element, RSpecElement):
                self.elements[rspec_element.type] = rspec_element

    def register_rspec_element(self, element_type, element_name, element_path):
        if element_type not in RSpecElements:
            raise InvalidRSpecElement(element_type, extra="no such element type: %s. Must specify a valid RSpecElement" % element_type)
        self.elements[element_type] = RSpecElement(element_type, element_name, element_path)

    def get_rspec_element(self, element_type):
        if element_type not in self.elements:
            msg = "ElementType %s not registerd for this rspec" % element_type
            raise InvalidRSpecElement(element_type, extra=msg)
        return self.elements[element_type]

    def get(self, element_type, filter={}, depth=0):
        elements = self.get_elements(element_type, filter)
        elements = [self.xml.get_element_attributes(elem, depth=depth) for elem in elements]
        return elements

    def get_elements(self, element_type, filter={}):
        """
        search for a registered element
        """
        if element_type not in self.elements:
            msg = "Unable to search for element %s in rspec, expath expression not found." % \
                   element_type
            raise InvalidRSpecElement(element_type, extra=msg)
        rspec_element = self.get_rspec_element(element_type)
        xpath = rspec_element.path + XpathFilter.xpath(filter)
        return self.xml.xpath(xpath)

    def merge(self, in_rspec):
        self.version.merge(in_rspec)

    def filter(self, filter):
        if 'component_manager_id' in filter:    
            nodes = self.version.get_node_elements()
            for node in nodes:
                if 'component_manager_id' not in node.attrib or \
                  node.attrib['component_manager_id'] != filter['component_manager_id']:
                    parent = node.getparent()
                    parent.remove(node) 
        

    def toxml(self, header=True):
        if header:
            return self.header + self.xml.toxml()
        else:
            return self.xml.toxml()
    

    def save(self, filename):
        return self.xml.save(filename)
         
if __name__ == '__main__':
    rspec = RSpec('/tmp/resources.rspec')
    print rspec
    rspec.register_rspec_element(RSpecElements.NETWORK, 'network', '//network')
    rspec.register_rspec_element(RSpecElements.NODE, 'node', '//node')
    print rspec.get(RSpecElements.NODE)[0]
    print rspec.get(RSpecElements.NODE, depth=1)[0]

