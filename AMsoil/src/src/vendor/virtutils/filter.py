import amsoil.core.log
import lxml
import xmltodict
import json

logging=amsoil.core.log.getLogger('VirtUtils')

"""
        @author: SergioVidiella

        General filter to XML
"""

class Filter:

    @staticmethod
    def filter_xml_by_dict(dictionary, xml, tag="", namespace_dict=None):
        if namespace_dict:
            namespace = namespace_dict.keys()[0]
        else:
            namespace = ""
        for filtered_node in dictionary:
            for node in xml.xpath("//%s%s%s" % (namespace, ":" if namespace else "", filtered_node), namespaces=namespace_dict):
                if not tag:
                    node.getparent().remove(node)
                elif node.getparent().tag == "%s%s%s%s" %("{" if namespace else "", namespace_dict[namespace] if namespace_dict else "", "}" if namespace else "", tag):
                    node.getparent().remove(node)

