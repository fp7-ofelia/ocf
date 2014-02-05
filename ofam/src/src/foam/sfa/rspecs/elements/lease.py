from foam.sfa.rspecs.elements.element import Element
 
class Lease(Element):
    
    fields = [
        'lease_id',
        'component_id',
        'slice_id',
        'start_time',
        'duration',    
    ]
