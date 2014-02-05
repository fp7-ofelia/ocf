from foam.sfa.util.xrn import Xrn
from foam.sfa.util.xml import XmlElement

from foam.sfa.rspecs.elements.element import Element
from foam.sfa.rspecs.elements.sliver import Sliver
from foam.sfa.rspecs.elements.versions.sfav1PLTag import SFAv1PLTag

from sfa.planetlab.plxrn import PlXrn

class SFAv1Sliver:

    @staticmethod
    def add_slivers(xml, slivers):
        if not slivers:
            return
        if not isinstance(slivers, list):
            slivers = [slivers]
        for sliver in slivers:
            sliver_elem = xml.add_instance('sliver', sliver, ['name'])
            tags = sliver.get('tags', [])
            if tags:
                for tag in tags:
                    SFAv1Sliver.add_sliver_attribute(sliver_elem, tag['tagname'], tag['value'])

    @staticmethod
    def add_sliver_attribute(xml, name, value):
        elem = xml.add_element(name)
        elem.set_text(value)
    
    @staticmethod
    def get_sliver_attributes(xml):
        attribs = []
        for elem in xml.iterchildren():
            if elem.tag not in Sliver.fields:
                xml_element = XmlElement(elem, xml.namespaces)
                instance = Element(fields=xml_element, element=elem)
                instance['name'] = elem.tag
                instance['value'] = elem.text
                attribs.append(instance)
        return attribs 
                
    @staticmethod
    def get_slivers(xml, filter={}):
        xpath = './default:sliver | ./sliver'
        sliver_elems = xml.xpath(xpath)
        slivers = []
        for sliver_elem in sliver_elems:
            sliver = Sliver(sliver_elem.attrib,sliver_elem)
            if 'component_id' in xml.attrib:     
                sliver['component_id'] = xml.attrib['component_id']
            sliver['tags'] = SFAv1Sliver.get_sliver_attributes(sliver_elem)
            slivers.append(sliver)
        return slivers           

