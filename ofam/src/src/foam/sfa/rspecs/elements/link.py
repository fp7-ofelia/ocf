from foam.sfa.rspecs.elements.element import Element    

class Link(Element):
    fields = [
        'client_id', 
        'component_id',
        'component_name',
        'component_manager',
        'type',
        'interface1',
        'interface2',
        'capacity',
        'latency',
        'packet_loss',
        'description',
    ]
