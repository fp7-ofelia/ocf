'''
Created on Apr 26, 2010

@author: jnaous
'''
from rpc4django import rpcmethod

@rpcmethod(signature=['struct', # return value
                      'int', 'string', 'string',
                      'string', 'string',
                      'array', 'array'])
def reserve_slice(slice_id, project_name, project_description,
                  slice_name, slice_description,
                  switch_sliver, link_sliver):
    '''
    Create an OpenFlow slice. 
    
    The C{switch_sliver} list contains a dict for each switch to be added to the
    slice's topology. Each such dict has the following items:
    
    - C{datapath_id}: the switch's datapath id
    - C{flowspace}: an array of dicts describing the switch's flowspace
    Each such dict has the following keys:
        - C{port_num}: string. the port for this flowspace
        - C{direction}: string. 'ingress', 'egress', or 'bidirectional'
        - C{policy}: int. 1 for 'allow', -1 for 'deny', 0 for read only
        - C{dl_src}: string. link layer address in "xx:xx:xx:xx:xx:xx"
        format or '*' for wildcard
        - C{dl_dst}: string. link layer address in "xx:xx:xx:xx:xx:xx"
        format or '*' for wildcard
        - C{vlan_id}: string. vlan id or "*" for wildcard
        - C{nw_src}: network address in "x.x.x.x" format
        or '*' for wildcard
        - C{nw_dst}: string. network address in "x.x.x.x" format
        or '*' for wildcard
        - C{nw_proto}: string. network protocol or "*" for wildcard
        - C{tp_src}: string. transport port or "*" for wildcard
        - C{tp_dst}: string. transport port or "*" for wildcard

    The C{link_sliver} list contains a dict for each link to be added to the
    slice's topology. Each such dict has the following items:
    
    - C{link_id}: an identifier for the link given to the clearinghouse by the
    aggregate manager.
        
    The call returns a dict with the following items:
    - C{error_msg}: a summary error message or "" if no errors occurred.
    - C{switches}: a list of dicts with the following items:
        - C{datapath_id}: id of the switch that caused the error
        - C{error}: optional error msg for the switch
        - all other fields of the C{switch_sliver} dicts mentioned above
        (port_num, direction, ...). The values for these items are the error
        messages associated with each field.
    - C{links}: a list of dicts with the following items:
        - C{link_id}: id of the link with the error
        - C{error}: optional error msg for the link
        - all other fields of C{link_sliver} dicts mentioned above (currently
        none other than link_id). The values are error messages associated
        with each field

    @param slice_id: an int that uniquely identifies the slice at the 
        clearinghouse.
    @type slice_id: int
    @param project_name: a name for the project under which this slice 
        is created
    @type project_name: string
    @param project_description: text describing the project
    @type project_description: string
    @param slice_name: Name for the slice
    @type slice_name: string
    @param slice_description: text describing the slice/experiment
    @type slice_description: string
    @param switch_sliver: description of the topology and flowspace for slice
    @type switch_sliver: list of dicts
    @param link_sliver: description of the links in the slice topology
    @type link_sliver: list of dicts
    @return: switches and links that have caused errors
    @rtype: dict
    '''

    return {
        'error_msg': "",
        'switches': [],
        'links': [],
    }

@rpcmethod(signature=['string', 'int'])
def delete_slice(slice_id):
    '''
    Delete the slice with id slice_id.
    
    @param slice_id: an int that uniquely identifies the slice at the 
        Clearinghouseclearinghouse.
    @type slice_id: int
    @return error message if there are any errors or "" otherwise.
    '''
    
    return ""
