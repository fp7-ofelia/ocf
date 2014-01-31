from foam.sfa.rspecs.elements.element import Element

class Property(Element):
    
    fields = [
        'source_id',
        'dest_id',
        'capacity',
        'latency',
        'packet_loss',
    ]
       
