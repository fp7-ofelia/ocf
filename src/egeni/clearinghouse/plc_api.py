'''
Created on Oct 17, 2009

@author: jnaous
'''

def reserve_slice(am_url, rspec, slice_id):
    '''
    Reserves the slice identified by slice_id or
    updates the slice if already reserved on the AM.
    
    On success, returns the empty string.
    On error, returns an rspec that has the failing nodes with their
    failing interfaces if the AM failed to reserve the interface.
    If reserving the node failed but not due to the interface, the
    rspec contains only the failing node without its interfaces.
    '''
    
    return ""    

def delete_slice(am_url, slice_id):
    '''
    Delete the slice.
    '''
    pass

def get_rspec(am_url):
    '''
    Returns the RSpec of available resources.
    '''    
    pass

def update_rspec(self_am):
    pass
