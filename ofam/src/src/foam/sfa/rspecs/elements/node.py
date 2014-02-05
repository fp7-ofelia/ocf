from foam.sfa.rspecs.elements.element import Element
 
class Node(Element):
    
    fields = [
        'client_id',
        'component_id',
        'component_name',
        'component_manager_id',
        'client_id',
        'sliver_id',
        'authority_id',    
        'exclusive',
        'location',
        'bw_unallocated',
        'bw_limit',
        'boot_state',    
        'slivers',
        'hardware_types',
        'disk_images',
        'interfaces',
        'services',
        'tags',
        'pl_initscripts',
    ]
                
      
