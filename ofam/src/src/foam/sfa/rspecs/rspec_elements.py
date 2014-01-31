from foam.sfa.util.enumeration import Enum

# recognized top level rspec elements
RSpecElements = Enum(
    AVAILABLE='AVAILABLE',
    BWLIMIT='BWLIMIT',
    EXECUTE='EXECUTE',
    NETWORK='NETWORK', 
    COMPONENT_MANAGER='COMPONENT_MANAGER',
    HARDWARE_TYPE='HARDWARE_TYPE', 
    INSTALL='INSTALL', 
    INTERFACE='INTERFACE', 
    INTERFACE_REF='INTERFACE_REF',
    LOCATION='LOCATION', 
    LOGIN='LOGIN', 
    LINK='LINK', 
    LINK_TYPE='LINK_TYPE', 
    NODE='NODE', 
    PROPERTY='PROPERTY',
    SERVICES='SERVICES',
    SLIVER='SLIVER', 
    SLIVER_TYPE='SLIVER_TYPE', 
    LEASE='LEASE',
    GRANULARITY='GRANULARITY',
    SPECTRUM='SPECTRUM',
    CHANNEL='CHANNEL',
    POSITION_3D ='POSITION_3D', 
)

class RSpecElement:
    def __init__(self, element_type, path):
        if not element_type in RSpecElements:
            raise InvalidRSpecElement(element_type)
        self.type = element_type
        self.path = path
