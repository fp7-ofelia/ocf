from foam.sfa.rspecs.elements.element import Element

class FWRule(Element):
    fields = [ 
        'protocol',
        'cidr_ip',
        'port_range',
        'icmp_type_code',
    ]
        
