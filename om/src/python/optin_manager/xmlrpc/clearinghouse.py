'''
Created on Apr 26, 2010

@author: jnaous
'''
from rpc4django import rpcmethod
from django.contrib.auth.models import User

@rpcmethod(signature=['struct', # return value
                      'int', 'string', 'string',
                      'string', 'string', 'string',
                      'array', 'array'])
def reserve_slice(slice_id, project_name, project_description,
                  slice_name, slice_description, controller_url,
                  owner_email, owner_password,
                  switch_slivers, **kwargs):
    '''
    Create an OpenFlow slice. 
    
    The C{switch_sliver} list contains a dict for each switch to be added to the
    slice's topology. Each such dict has the following items:
    
    - C{datapath_id}: the switch's datapath id
    - C{flowspace}: an array of dicts describing the switch's flowspace
    Each such dict has the following keys:
        - C{id}: integer. Per clearinghouse unique identifier for the rule.
        - C{direction}: string. 'ingress', 'egress', or 'bidirectional'
        - C{policy}: int. 1 for 'allow', -1 for 'deny', 0 for read only
        - C{port_num_start}, C{port_num_end}: string. the port range for this 
        flowspace
        - C{dl_src_start}, C{dl_src_end}: string. link layer address range in
        "xx:xx:xx:xx:xx:xx" format or '*' for wildcard
        - C{dl_dst_start}, C{dl_dst_end}: string. link layer address range in
        "xx:xx:xx:xx:xx:xx" format or '*' for wildcard
        - C{vlan_id_start}, C{vlan_id_end}: string. vlan id range or
        "*" for wildcard
        - C{nw_src_start}, C{nw_src_end}: string. network address range in 
        "x.x.x.x" format or '*' for wildcard
        - C{nw_dst_start}, C{nw_dst_end}: string. network address range in
        "x.x.x.x" format or '*' for wildcard
        - C{nw_proto_start}, C{nw_proto_end}: string. network protocol range or
        "*" for wildcard
        - C{tp_src_start}, C{tp_src_end}: string. transport port range or "*"
        for wildcard
        - C{tp_dst_start}, C{tp_dst_end}: string. transport port range or "*"
        for wildcard

    The call returns a dict with the following items:
    - C{error_msg}: a summary error message or "" if no errors occurred.
    - C{switches}: a list of dicts with the following items:
        - C{datapath_id}: id of the switch that caused the error
        - C{error}: optional error msg for the switch
        - all other fields of the C{switch_sliver} dicts mentioned above
        (port_num, direction, ...). The values for these items are the error
        messages associated with each field.

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
    
    @param controller_url: The URL for the slice's OpenFlow controller specified
        as <transport>:<hostname>[:<port>], where:
            - tranport is 'tcp' ('ssl' will be added later)
            - hostname is the controller's hostname
            - port is the port on which the controller listens to openflow
            messages (defaults to 6633).
    @type controller_url: string
    
    @param owner_email: email of the person responsible for the slice
    @type owner_email: string
    
    @param owner_password: initial password the user can use to login to the
        FlowVisor Web interface. Will need to be changed on initial login.
    @type owner_password: string
    
    @param switch_sliver: description of the topology and flowspace for slice
    @type switch_sliver: list of dicts
    
    @param kwargs: will contain additional useful information about the request.
        Of most use are the items in the C{kwargs['request'].META} dict. These
        include 'REMOTE_USER' which is the username of the user connecting or
        if using x509 certs then the domain name.
    
    @return: switches and links that have caused errors
    @rtype: dict
    '''

    return {
        'error_msg': "",
        'switches': [],
    }

@rpcmethod(signature=['string', 'int'])
def delete_slice(slice_id, **kwargs):
    '''
    Delete the slice with id slice_id.
    
    @param slice_id: an int that uniquely identifies the slice at the 
        Clearinghouseclearinghouse.
    @type slice_id: int
    @param kwargs: will contain additional useful information about the request.
        Of most use are the items in the C{kwargs['request'].META} dict. These
        include 'REMOTE_USER' which is the username of the user connecting or
        if using x509 certs then the domain name.
    @return error message if there are any errors or "" otherwise.
    '''
    
    return ""

@rpcmethod(signature=['string', 'string'])
def change_password(new_password, **kwargs):
    '''
    Change the current password used for the clearinghouse to 'new_password'.
    
    @param new_password: the new password to use for authentication.
    @type new_password: random string of 1024 characters
    @param kwargs: will contain additional useful information about the request.
        Of most use are the items in the C{kwargs['request'].META} dict. These
        include 'REMOTE_USER' which is the username of the user connecting or
        if using x509 certs then the domain name.
    @return: Error message if there is any.
    @rtype: string
    '''
    
    username = kwargs['request'].META['REMOTE_USER']
    
    dummy = User.objects.get_or_create(username='xmlrpcdummy')
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExistError:
        # Do not return an error indicating the user does not
        # exist so we don't provide an easy way for probing for usernames.
        # We also do a set_password on the dummy user so we don't worry
        # about timing attacks.
        user = dummy
    
    user.set_password(new_password)
    
    return ""

@rpcmethod(signature=['string', 'string'])
def ping(data):
    '''
    Test method to see that everything is up.
    return a string that is "%s: PONG" % data
    '''
    
    return "%s: PONG" % data
