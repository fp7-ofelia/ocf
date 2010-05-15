'''
Created on Apr 26, 2010

@author: jnaous
'''
from rpc4django import rpcmethod
from django.contrib.auth.models import User
from pprint import pprint
from optin_manager.xmlrpc_server.models import CallBackServerProxy, CallBackFVProxy
from optin_manager.flowspace.models import Experiment, Topology, ExperimentFLowSpace, UserOpts, OptsFlowSpace
from optin_manager.flowspace.utils import DottedIPToInt, MACtoInt

def convertStar(fs):
    if ( fs['dl_src_start'] =='*'):
        fs['dl_src_start'] = '00:00:00:00:00:00'
    if (fs['dl_src_end'] == '*' ):
        fs['dl_src_start'] = 'FF:FF:FF:FF:FF:FF'

    if ( fs['dl_dst_start'] =='*' ):
        fs['dl_dst_start'] = '00:00:00:00:00:00'
    if (fs['dl_dst_end'] == '*' ):
        fs['dl_dst_end'] = 'FF:FF:FF:FF:FF:FF'     
        
    if ( fs['nw_src_start'] =='*'):
        fs['nw_src_start'] = '0.0.0.0'
    if (fs['nw_src_end'] == '*' ):
        fs['nw_src_end'] = '255.255.255.255'
        
    if ( fs['nw_dst_start'] =='*'):
        fs['dl_dst_start'] = '00:00:00:00:00:00'
    if (fs['nw_dst_end'] == '*' ):
        fs['nw_dst_end'] = '255.255.255.255'   
              
    if ( fs['tp_src_start'] =='*'):
        fs['tp_src_start'] = '0'
    if (fs['tp_src_end'] == '*' ):
        fs['tp_src_end'] = '65535'
        
    if ( fs['tp_dst_start'] =='*'):
        fs['tp_dst_start'] = '0' 
    if (fs['tp_dst_end'] == '*' ):
        fs['tp_dst_end'] = '65535' 
        
    if ( fs['vlan_id_start'] =='*' ):
        fs['vlan_id_start'] = '0'
    if (fs['vlan_id_end'] == '*' ):
        fs['vlan_id_end'] = '2047' 
        
    if ( fs['nw_proto_start'] =='*'):
        fs['nw_proto_start'] = '0'
    if (fs['nw_proto_end'] == '*' ):
        fs['nw_proto_end'] = '255'
        
    return fs

               
@rpcmethod(signature=['struct', # return value
                      'int', 'string', 'string',
                      'string', 'string', 'string',
                      'array', 'array'])
def create_slice(slice_id, project_name, project_description,
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
    
    @param switch_slivers: description of the topology and flowspace for slice
    @type switch_slivers: list of dicts
    
    @param kwargs: will contain additional useful information about the request.
        Of most use are the items in the C{kwargs['request'].META} dict. These
        include 'REMOTE_USER' which is the username of the user connecting or
        if using x509 certs then the domain name.
    
    @return: switches and links that have caused errors
    @rtype: dict
    '''
    # TODO: add security check
    
    e = Experiment()
    e.slice_id = slice_id
    e.project_name = project_name
    e.project_desc = project_description
    e.slice_name = slice_name
    e.slice_desc = slice_description
    e.controller_url = controller_url
    e.owner_email = owner_email
    e.owner_password = owner_password
    
    # Add switches to experiments
    for sliver in switch_slivers:
        sw = Topology.objects.filter(dpid = sliver.datapath_id)[0]
        e.topology.add(sw)
    e.save()
    
    # TODO: future feature: for now, each experiment has one flowspace across all the switches it has requested.
    # It doesn't have per switch granularity .
    
    # Add flowspace to experiment.
    for sfs in switch_slivers[0]:
        efs = ExperimentFLowSpace()
        efs.exp  = e
        fs = convertStar(sfs)
        efs.mac_src_s = MACtoInt(fs['dl_src_start'])
        efs.mac_src_e = MACtoInt(fs['dl_src_end'])
        efs.mac_dst_s = MACtoInt(fs['dl_dst_start'])
        efs.mac_dst_e = MACtoInt(fs['dl_dst_end'])
        efs.vlan_id_s = int(fs['vlan_id_start'])
        efs.vlan_id_e  = int(fs['vlan_id_end'])
        efs.ip_src_s = DottedIPToInt(fs['nw_src_start'])
        efs.ip_src_e = DottedIPToInt(fs['nw_src_end'])
        efs.ip_dst_s = DottedIPToInt(fs['nw_dst_start'])
        efs.ip_dst_e = DottedIPToInt(fs['nw_dst_end'])
        efs.ip_proto_s = int(fs['nw_proto_start'])
        efs.ip_proto_e = int(fs['nw_proto_end'])
        efs.tp_src_s = int(fs['tp_src_start'])
        efs.tp_src_e = int(fs['tp_src_end'])
        efs.tp_dst_s = int(fs['tp_dst_start'])
        efs.tp_dst_e = int(fs['tp_dst_end'])
        efs.save()
     
    # Inform FV(s) of the changes
    for fv in CallBackFVProxy.objects.all():
        fv_success = fv.addNewSlice(slice_id, owner_password, controller_url, owner_email)
        if (not fv_success):
            error_msg = "FlowVisor rejected this request"
    
    print "reserve_slice got the following:"
    print "    slice_id: %s" % slice_id
    print "    project_name: %s" % project_name
    print "    project_desc: %s" % project_description
    print "    slice_name: %s" % slice_name
    print "    slice_desc: %s" % slice_description
    print "    controller: %s" % controller_url
    print "    owner_email: %s" % owner_email
    print "    owner_pass: %s" % owner_password
    print "    switch_slivers"
    pprint(switch_slivers, indent=8)
    
    try:
        print "    REMOTE_USER: %s" % kwargs['request'].META['REMOTE_USER']
    except KeyError, e:
        print "%s" % e

    return {
        'error_msg': error_msg,
        'switches': [],
    }

@rpcmethod(signature=['string', 'int'])
def delete_slice(sliceid, **kwargs):
    '''
    Delete the slice with id sliceid.
    
    @param slice_id: an int that uniquely identifies the slice at the 
        Clearinghouseclearinghouse.
    @type sliceid: int
    @param kwargs: will contain additional useful information about the request.
        Of most use are the items in the C{kwargs['request'].META} dict. These
        include 'REMOTE_USER' which is the username of the user connecting or
        if using x509 certs then the domain name.
    @return error message if there are any errors or "" otherwise.
    '''
    exps = Experiment.objects.filter(slice_id = sliceid)
    for single_exp in exps:
        OptsFlowSpace.objects.filter(opt__experiment = single_exp).delete()
        UserOpts.objects.filter(experiment = single_exp)
        ExperimentFLowSpace.objects.filter(exp = single_exp).delete()
        single_exp.delete()
        
    for fv in CallBackFVProxy.objects.all():
        success = fv.deleteSlice(sliceid)
        if (not success):
            error_msg = "At least one flowvisor sent an error"
        
    return error_msg


@rpcmethod(signature=['array'])
def get_switches():
    '''
    Return what the FlowVisor gives.
    '''
    #TODO: security check
    complete_list = []
    for fv in CallBackFVProxy.objects.all():
        switches = fv.get_switches()
        complete_list.append(switches)
        
    return complete_list


@rpcmethod(signature=['array'])
def get_links():
    '''
    Return what the FlowVisor gives.
    '''
    #TODO: security check
    complete_list = []
    for fv in CallBackFVProxy.objects.all():
        links = fv.get_links()
        complete_list.append(links)
        
    return complete_list


@rpcmethod(signature=['string', 'string', 'string'])
def register_topology_callback(url, cookie, **kwargs):
    '''
    Store some information for the topology callback.
    '''
    #TODO: security check
    from clearinghouse import utils
    try:
        username = kwargs['request'].META['REMOTE_USER']
    except KeyError, e:
        return "ERROR: Anauthenticated user!"

    attrs = {'url': url, 'cookie': cookie}
    filter_attrs = {'username': username}
    utils.create_or_update(CallBackServerProxy, filter_attrs, attrs)
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
    
    print kwargs
    
    print"******** change_password started"
    
    try:
        username = kwargs['request'].META['REMOTE_USER']
    except KeyError, e:
        return "ERROR: Anauthenticated user!"
    
    print"******** change_password doing user"

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
    user.save()

    print "******** change_password Done to %s" % new_password
    
    return ""

@rpcmethod(signature=['string', 'string'])
def ping(data, **kwargs):
    '''
    Test method to see that everything is up.
    return a string that is "PONG: %s" % data
    '''
    try:
        username = kwargs['request'].META['REMOTE_USER']
    except KeyError, e:
        return "ERROR: Anauthenticated user!"
    print "Pinged!"
    return "PONG: %s" % data
