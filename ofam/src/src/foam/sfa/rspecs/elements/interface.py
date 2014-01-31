from foam.sfa.rspecs.elements.element import Element

class Interface(Element):
    fields = ['component_id',
              'role',
              'client_id',
              'ipv4',
              'bwlimit',
              'node_id',
              'interface_id',
              'mac_address',  
    ]    
