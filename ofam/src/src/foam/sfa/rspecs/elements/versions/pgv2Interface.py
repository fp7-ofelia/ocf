from foam.sfa.util.xrn import Xrn
from foam.sfa.util.xml import XpathFilter
from foam.sfa.rspecs.elements.interface import Interface

class PGv2Interface:

    @staticmethod
    def add_interfaces(xml, interfaces):
        if isinstance(interfaces, list):
            for interface in interfaces:
                if_elem = xml.add_instance('interface', interface, ['component_id', 'client_id', 'sliver_id'])
                ips = interface.get('ips', [])
                for ip in ips:
                    if_elem.add_instance('ip', {'address': ip.get('address'),
                                                'netmask': ip.get('netmask'),
                                                'type': ip.get('type')}) 
    
    @staticmethod
    def get_interfaces(xml):
        pass
