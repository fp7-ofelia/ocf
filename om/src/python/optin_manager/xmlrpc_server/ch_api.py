'''
Created on Apr 26, 2010

@author: jnaous
'''
from apps.rpc4django import rpcmethod
from django.contrib.auth.models import User
from pprint import pprint
from optin_manager.xmlrpc_server.models import CallBackServerProxy, FVServerProxy
from optin_manager.flowspace.models import Experiment, ExperimentFLowSpace, UserOpts, OptsFlowSpace
from optin_manager.flowspace.utils import dotted_ip_to_int, mac_to_int, int_to_dotted_ip, int_to_mac
from decorator import decorator

@decorator
def check_user(func, *args, **kwargs):
    """
    Check that the user is authenticated and known.
    """
    if "request" not in kwargs:
        raise Exception("Request not available for XML-RPC %s" % \
                        func.func_name)
    meta = kwargs["request"].META
    if "REMOTE_USER" not in meta:
        raise Exception(
            "Remote user not authenticated for XML-RPC %s." % (
                func.func_name,
            )
        )
    if User.objects.filter(username=meta["REMOTE_USER"]).count() == 0:
        raise Exception("Remote user %s is unknown for call %s." % (
            meta["REMOTE_USER"], func.func_name)
        )
    #Check that the user can actually make the xmlrpc call
    this_user = User.objects.get(username = meta["REMOTE_USER"])
    if (not this_user.get_profile().is_clearinghouse_user):
        raise Exception("Remote user %s is not a clearinghouse user"%
                       (meta["REMOTE_USER"])
        )
    kwargs['username'] = meta["REMOTE_USER"]
       
    return func(*args, **kwargs)

def _same(val):
        return "%s" % val
    
class om_ch_translate(object):
    attr_funcs = {
        # attr_name: (func to turn to str, width)
        "dl_src": (int_to_mac, mac_to_int, 48, "mac_src","dl_src"),
        "dl_dst": (int_to_mac, mac_to_int, 48, "mac_dst","dl_dst"),
        "dl_type": (_same, int, 16, "eth_type","dl_type"),
        "vlan_id": (_same, int, 12, "vlan_id","dl_vlan"),
        "nw_src": (int_to_dotted_ip, dotted_ip_to_int, 32, "ip_src","nw_src"),
        "nw_dst": (int_to_dotted_ip, dotted_ip_to_int, 32, "ip_dst","nw_dst"),
        "nw_proto": (_same, int, 8, "ip_proto","nw_proto"),
        "tp_src": (_same, int, 16, "tp_src","tp_src"),
        "tp_dst": (_same, int, 16, "tp_dst","tp_dst"),
        "port_num": (_same, int, 16, "port_number","in_port"),
    }
    
def convert_star(fs):
    temp = fs.copy()
    for ch_name, (to_str, from_str, width, om_name, of_name) in \
    om_ch_translate.attr_funcs.items():
        ch_start = "%s_start" % ch_name
        ch_end = "%s_end" % ch_name
        if ch_start not in fs or fs[ch_start] == "*":
            temp[ch_start] = to_str(0)
        if ch_end not in fs or fs[ch_end] == "*":
            temp[ch_end] = to_str(2**width - 1)
    return temp

def convert_star_int(fs):
    temp = fs.copy()
    for ch_name, (to_str, from_str, width, om_name, of_name) in \
    om_ch_translate.attr_funcs.items():
        ch_start = "%s_start" % ch_name
        ch_end = "%s_end" % ch_name
        
        if ch_start not in fs or fs[ch_start] == "*":
            temp[ch_start] = 0
        else:
            temp[ch_start] = from_str(fs[ch_start])
            
        if ch_end not in fs or fs[ch_end] == "*":
            temp[ch_end] = 2**width - 1
        else:
            temp[ch_end] = from_str(fs[ch_end])   
                    
    return temp


def get_direction(direction):
    if (direction == 'ingress'):
        return 0
    if (direction == 'egress'):
        return 1
    if (direction == 'bidirectional'):
        return 2
    return 2
               
@check_user
@rpcmethod(signature=['struct', # return value
                      'string', 'string', 'string',
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

    @param slice_id: a string that uniquely identifies the slice at the 
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

    print "create_slice got the following:"
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

    e = Experiment()
    e.slice_id = slice_id
    e.project_name = project_name
    e.project_desc = project_description
    e.slice_name = slice_name
    e.slice_desc = slice_description
    e.controller_url = controller_url
    e.owner_email = owner_email
    e.owner_password = owner_password
    e.save()

#    print "Experiment created"

    #inspired by Jad :)
    # Add switches to experiments
    for sliver in switch_slivers:
        if "datapath_id" in sliver:
            dpid = sliver['datapath_id']
        else:
            dpid = "00:" * 8
            dpid = dpid[:-1]
            
        for sfs in sliver['flowspace']:
            efs = ExperimentFLowSpace()
            efs.exp  = e
            efs.dpid = dpid
            if "direction" in sfs:
                efs.direction = get_direction(sfs['direction'])
            else:
                efs.direction = 2
                
            fs = convert_star(sfs)
            for attr_name,(to_str, from_str, width, om_name, of_name) in \
            om_ch_translate.attr_funcs.items():
                ch_start ="%s_start"%(attr_name)
                ch_end ="%s_end"%(attr_name)
                om_start ="%s_s"%(om_name)
                om_end ="%s_e"%(om_name)
                setattr(efs,om_start,from_str(fs[ch_start]))
                setattr(efs,om_end,from_str(fs[ch_end]))
            efs.save()
    
    error_msg = "" 
    # Inform FV of the changes
    fv = FVServerProxy.objects.all()[0]
    fv_success = fv.api.createSlice(
        "%s" % e.get_fv_slice_name(),
        "%s" % owner_password,
        "%s" % controller_url,
        "%s" % owner_email,
    )
    print "Created slice with %s %s %s %s" % (
        e.get_fv_slice_name(), owner_password, controller_url, owner_email)
    if not fv_success:
        print "Flowvisor create slice error"
        error_msg = "FlowVisor rejected this request"
    
    fv.api.getSliceInfo(e.get_fv_slice_name())
    
    # TODO: fix the return
    return {
        'error_msg': error_msg,
        'switches': [],
    }

@check_user
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
    
    single_exp = Experiment.objects.get(slice_id = sliceid)
    OptsFlowSpace.objects.filter(opt__experiment = single_exp).delete()
    UserOpts.objects.filter(experiment = single_exp)
    ExperimentFLowSpace.objects.filter(exp = single_exp).delete()
    single_exp.delete()
    
    error_msg = ""
    fv = FVServerProxy.objects.all()[0]
    success = fv.api.deleteSlice(single_exp.get_fv_slice_name())
    if not success:
        error_msg = "flowvisor sent an error"
        
    return error_msg

@check_user
@rpcmethod(signature=['array'])
def get_switches(**kwargs):
    '''
    Return what the FlowVisor gives.
    '''
    complete_list = []
    fv = FVServerProxy.objects.all()[0]
    switches = fv.get_switches()
    complete_list.extend(switches)
        
    return complete_list


@check_user
@rpcmethod(signature=['array'])
def get_links(**kwargs):
    '''
    Return what the FlowVisor gives.
    '''
    complete_list = []
    fv = FVServerProxy.objects.all()[0]
    links = fv.get_links()
    complete_list.extend(links)
        
    return complete_list


@check_user
@rpcmethod(signature=['string', 'string', 'string'])
def register_topology_callback(url, cookie, **kwargs):
    '''
    Store some information for the topology callback.
    '''
    from clearinghouse import utils

    attrs = {'url': url, 'cookie': cookie}
    filter_attrs = {'username': kwargs['username']}
    utils.create_or_update(CallBackServerProxy, filter_attrs, attrs)
    return ""

@check_user
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
    dummy = User.objects.get_or_create(username='xmlrpcdummy')
    
    try:
        user = User.objects.get(username=kwargs['username'])
    except User.DoesNotExist:
        # Do not return an error indicating the user does not
        # exist so we don't provide an easy way for probing for usernames.
        # We also do a set_password on the dummy user so we don't worry
        # about timing attacks.
        user = dummy
    
    user.set_password(new_password)
    user.save()
    
    return ""

@check_user
@rpcmethod(signature=['string', 'string'])
def ping(data, **kwargs):
    '''
    Test method to see that everything is up.
    return a string that is "PONG: %s" % data
    '''
    print "Pinged!"
    return "PONG: %s" % data
