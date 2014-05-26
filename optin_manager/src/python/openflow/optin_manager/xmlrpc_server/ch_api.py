'''
Created on Apr 26, 2010

@author: jnaous
'''
from expedient.common.rpc4django import rpcmethod
from django.contrib.auth.models import User
from pprint import pprint
from models import CallBackServerProxy, FVServerProxy
from openflow.optin_manager.admin_manager.models import FlowSpaceAutoApproveScript
from openflow.optin_manager.opts.models import Experiment, ExperimentFLowSpace,\
    UserOpts, OptsFlowSpace, MatchStruct
from openflow.optin_manager.flowspace.utils import dotted_ip_to_int, mac_to_int,\
    int_to_dotted_ip, int_to_mac, parseFVexception
from decorator import decorator
from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail
from openflow.optin_manager.flowspace.utils import int_to_mac, int_to_dotted_ip
from django.contrib.sites.models import Site
from openflow.optin_manager.opts.autofsgranter import auto_fs_granter
import uuid

@decorator
def check_fv_set(func, *arg, **kwargs):
    fv = FVServerProxy.objects.all()
    if len(fv) == 0: 
        raise Exception("No flowvisor has been set. Please set Flowvisor\
URL first and then try again")
    elif (len(fv) > 1):
        raise Exception("More than one flowvisor is set in database. Make\
sure you just have one flowvisor")
    
    return func(*arg, **kwargs)


@decorator
def check_user(func, *args, **kwargs):
    """
    Check that the user is authenticated and known.
    """
    if "request" not in kwargs:
        raise Exception("Request not available for XML-RPC %s" % \
                        func.func_name)
    meta = kwargs["request"].META
    
    if not hasattr(kwargs["request"], "user"):
        raise Exception("Authentication Middleware not installed in settings.")
    
    if not kwargs['request'].user.is_authenticated():
        raise Exception("User not authenticated for XML-RPC %s." % func.func_name)
    else:
        kwargs['user'] = kwargs['request'].user

        # Check that the user can actually make the xmlrpc call
        this_user = kwargs['user']
        if not this_user.get_profile().is_clearinghouse_user:
            raise Exception("Remote user %s is not a clearinghouse user" % (
                this_user.username))
            
        return func(*args, **kwargs)

def _same(val):
        return "%s" % val

@check_user
@rpcmethod()
def checkFlowVisor( *arg, **kwargs):
    fv = FVServerProxy.objects.all()
    if len(fv) == 0:
        raise Exception("No flowvisor has been set. Please set Flowvisor\
URL first and then try again")
    elif (len(fv) > 1):
        Exception("More than one flowvisor is set in database. Make\
sure you just have one flowvisor")
    return "" 

    
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
@check_fv_set
@rpcmethod(signature=['struct', # return value
                      'string', 'string', 'string',
                      'string', 'string', 'string',
                      'array', 'array', 'struct'])
# XXX: **kwargs not allowed on XMLRPC methods
def create_slice(slice_id, project_name, project_description,
                  slice_name, slice_description, controller_url,
                  owner_email, owner_password,
                  switch_slivers, options={}, **kwargs):
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
    
    @param options:  will contain additional useful information for the operation
    @type options: dict

    @param kwargs: will contain additional useful information about the request.
        Of most use are the items in the C{kwargs['request'].META} dict. These
        include 'REMOTE_USER' which is the username of the user connecting or
        if using x509 certs then the domain name. Additionally, kwargs has the
        user using the 'user' key.
    
    @return: switches and links that have caused errors
    @rtype: dict
    '''

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
    print "    options: "
    pprint(options, indent=8)
#    print "    kwargs: "
#    pprint(kwargs, indent=8)
    
    # Determine slice style naming: legacy (Opt-in <= 0.7) or newer (FlowVisor >= 1.0)
    is_legacy_slice = True
    remotely_created = False
    
    # Retrieve information for current Experiment first
    try:
        # Legacy slices with older slice naming (Opt-in <= 0.7)
        e = Experiment.objects.filter(slice_id = options["legacy_slice_id"])
        if not e:
            raise Exception
    except:
        # New slice naming style (for FlowVisor >= 1.0) -> No legacy slice
        try:
            uuid.UUID('{%s}' % str(slice_id))
            is_legacy_slice = False 
        except:
            remotely_created = True
            is_legacy_slice = True
    e = Experiment.objects.filter(slice_id = slice_id)

    # If Experiment already existing => this is an update
    if (e.count()>0):
        old_e = e[0]
        # Legacy slices: use combination of name and ID
        if is_legacy_slice:
            old_fv_name = old_e.get_fv_slice_name()
        # Otherwise, use UUID
        else:
            old_fv_name = old_e.slice_id
        update_exp = True
        old_exp_fs = ExperimentFLowSpace.objects.filter(exp=old_e)
    else:
        update_exp = False
        
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
       
    all_efs = [] 
    for sliver in switch_slivers:
        if "datapath_id" in sliver:
            dpid = sliver['datapath_id']
        else:
            dpid = "00:" * 8
            dpid = dpid[:-1]
            
        if len(sliver['flowspace'])==0:
            # HACK:
            efs = ExperimentFLowSpace()
            efs.exp  = e
            efs.dpid = dpid
            efs.direction = 2
            all_efs.append(efs)
        else:
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
                all_efs.append(efs)
    
    fv = FVServerProxy.objects.all()[0]  
    if (update_exp):
        # Delete previous experiment from FV
        try:
            fv_success = fv.proxy.api.deleteSlice(old_fv_name)
            old_exp_fs.delete()
            old_e.delete()
        except Exception, exc:
            import traceback
            traceback.print_exc()
            if "slice does not exist" in str(exc):
                fv_success = True
                old_exp_fs.delete()
                old_e.delete()
            else:
                e.delete()
                print exc
                raise Exception(parseFVexception(exc,"While trying to update experiment, FV raised exception on the delete previous experiment step: "))
                
        if (not fv_success):
            e.delete()
            raise Exception("While trying to update experiment, FV returned False on the delete previous experiment step")
            
    # Create the new experiment on FV
    try:
#        # Legacy slices: use combination of name and ID
        if remotely_created:
            new_fv_name = e.get_fv_slice_name()
#        # Otherwise, use UUID
        else:
            new_fv_name = slice_id
        #new_fv_name = slice_id
        fv_success = fv.proxy.api.createSlice(
            "%s" % new_fv_name,
            "%s" % owner_password,
            "%s" % controller_url,
            "%s" % owner_email,
        )
        for fs in all_efs:
            fs.save()
        print "Created slice with %s %s %s %s" % (
        new_fv_name, owner_password, controller_url, owner_email)
    except Exception,exc:
        import traceback
        traceback.print_exc()
        e.delete()
        print exc
        if (update_exp):
            raise Exception(parseFVexception(exc,"Could not create slice at the Flowvisor, after deleting old slice. Error was: "))
        else:
            raise Exception(parseFVexception(exc,"Could not create slice at the Flowvisor. Error was: "))
            
    if not fv_success:
        e.delete()
        if (update_exp):
            raise Exception(
            "Could not create slice at the Flowvisor, after deleting old slice. FV Returned False in createSlice call")
        else:
            raise Exception(
            "Could not create slice at the Flowvisor. FV Returned False in createSlice call")

    if (update_exp):
        from openflow.optin_manager.opts.helper import update_opts_into_exp
        [fv_args,match_list] = update_opts_into_exp(e)
        if len(fv_args) > 0:
            # update previous opt-ins into this updated experiment
            try:
                returned_ids = fv.proxy.api.changeFlowSpace(fv_args)
                for i in range(len(match_list)):
                    match_list[i].fv_id = returned_ids[i]
                    match_list[i].save()
            except Exception, exc:
                from openflow.optin_manager.opts.helper import opt_fses_outof_exp
                import traceback
                traceback.print_exc()
                all_opts = UserOpts.objects.filter(experiment=e)
                for opt in all_opts:
                    optfses = OptsFlowSpace.objects.filter(opt = opt)
                    opt_fses_outof_exp(optfses)
                all_opts.delete()
                print exc
                raise Exception(parseFVexception(exc,"Couldn't re-opt into updated experiment. Lost all the opt-ins: "))
    
    flowspace_correctly_granted = True
    automatic_settings = get_automatic_settings()
    try:
        if automatic_settings["flowspace_auto_approval"]:
            auto_fs_granter(e)
    # FIXME An exception is being raised. Investigate.
    except Exception as exc:
        print "Exception happened when granting flowspace automatically: %s" % str(exc)
        flowspace_correctly_granted = False
    
    try:
        # Get project detail URL to send via e-mail
        from openflow.optin_manager.opts import urls
        from django.core.urlresolvers import reverse
        project_detail_url = reverse("opt_in_experiment") or "/"
        # No "https://" check should be needed if settings are OK
        site_domain_url = "https://" + Site.objects.get_current().domain + project_detail_url
        # Tuple with the requested VLAN range
        vlan_range = ""
        try:
            if not isinstance(all_efs,list):
                all_efs = [all_efs]
            # Obtain unique ranges of VLANs
            vlan_range_all_efs = set([ (efs.vlan_id_s, efs.vlan_id_e) for efs in all_efs ])
            # Create list for e-mail
#            add_vlan_range_email = lambda x: "VLAN range: %s" % str(x)
#            vlan_range += map("\n".join, [map(add_vlan_range_email, vlan_range_all_efs)])[0]
            vlan_range += "VLAN ranges: %s" % str(list(vlan_range_all_efs))
        except:
            pass
        
        if all_efs:
            # Default message: either for manual granting or any failure in automatic granting
            flowspace_subject = settings.EMAIL_SUBJECT_PREFIX + " Flowspace Request: OptinManager '" + str(project_name) + "'"
            flowspace_email = "Hi, Island Manager\n\nA new flowspace was requested:\n\nProject: " + str(project_name) + "\nSlice: " + str(slice_name) + "\n" + str(vlan_range) + "\n\nYou may add a new rule for this request at: %s" % site_domain_url
            if automatic_settings["flowspace_auto_approval"]:
                if flowspace_correctly_granted:
                    flowspace_subject = settings.EMAIL_SUBJECT_PREFIX + " Flowspace Approved: OptinManager '" + str(project_name) + "'"
                    flowspace_email = "Hi, Island Manager\n\nA new flowspace was automatically granted:\n\nProject: " + str(project_name) + "\nSlice: " + str(slice_name) + str(vlan_range) + "\n\nYou may check the rule for this request at: %s" % site_domain_url

            send_mail(flowspace_subject, flowspace_email, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[settings.ROOT_EMAIL],)
    except:
        pass
    
    transaction.commit()
    
    return {
        'error_msg': "",
        'switches': [],
    }     
             
@check_user
@check_fv_set
@rpcmethod(signature=['string', # return value
                      'int', 'struct'])
# XXX: **kwargs not allowed on XMLRPC methods
def delete_slice(slice_id, options={}, **kwargs):
    '''
    Delete the slice with id sliceid.
    
    @param slice_id: an int that uniquely identifies the slice at the 
        Clearinghouseclearinghouse.
    @type slice_id: int
    @param options: will contain additional useful information for this operation.
    @type options: dict
    @param kwargs: will contain additional useful information about the request.
        Of most use are the items in the C{kwargs['request'].META} dict. These
        include 'REMOTE_USER' which is the username of the user connecting or
        if using x509 certs then the domain name.
    @return error message if there are any errors or "" otherwise.
    '''
    
    # Determine slice style naming: legacy (Opt-in <= 0.7) or newer (FlowVisor >= 1.0)
    is_legacy_slice = True
    # Retrieve information for current Experiment first
    try:
        # Legacy slices with older slice naming (Opt-in <= 0.7)
        single_exp = Experiment.objects.get(slice_id = options["legacy_slice_id"])
        if not single_exp:
            raise Exception
    except:
        try:
            try:
                uuid.UUID('{%s}' % str(slice_id))
                is_legacy_slice = False
                single_exp = Experiment.objects.get(slice_id = slice_id)
            except:
                is_legacy_slice = True
                single_exp = Experiment.objects.get(slice_id = slice_id)
            # New slice naming style (for FlowVisor >= 1.0) -> No legacy slice
            single_exp = Experiment.objects.get(slice_id = slice_id)
        except Experiment.DoesNotExist:
            return "Experiment does not exist"
    
    fv = FVServerProxy.objects.all()[0]
    try:
        # Legacy slices: use combination of name and ID
        if is_legacy_slice:
            old_fv_name = single_exp.get_fv_slice_name()
        # Otherwise, use UUID
        else:
            old_fv_name = single_exp.slice_id
        success = fv.proxy.api.deleteSlice(old_fv_name)
    except Exception,e:
        import traceback
        traceback.print_exc()
        if "slice does not exist" in str(e):
            success = True
        else:
            return "Could not delete slice on Flowvisor: %s" % parseFVexception(e)
     
    # get all flowspaces opted into this exp
    ofs = OptsFlowSpace.objects.filter(opt__experiment = single_exp)
    
    # delete all match structs for each flowspace
    for fs in ofs:
        MatchStruct.objects.filter(optfs = fs).delete()
        
    # delete all flowspaces opted into this exp
    ofs.delete()
    UserOpts.objects.filter(experiment = single_exp).delete()
    ExperimentFLowSpace.objects.filter(exp = single_exp).delete()
    
    single_exp.delete()
    
    return ""

@check_user
@rpcmethod(signature=['string', 'string', 'array'])
def change_slice_controller(slice_id, controller_url, **kwargs):
    '''
    Changes the slice controller url.
    '''
    complete_list = []
    fv = FVServerProxy.objects.all()[0]
    try:
        params = controller_url.split(':') 
        experiment = Experiment.objects.get(slice_id = slice_id)
        slice_name= experiment.get_fv_slice_name()
        fv.proxy.api.changeSlice(slice_name,'controller_hostname', params[1])
        fv.proxy.api.changeSlice(slice_name,'controller_port', params[2])
        experiment.controller_url = controller_url
    except Exception, exc:
        import traceback
        traceback.print_exc()
        raise Exception(parseFVexception(exc,"FV could not update slice controller URL:"))
    return ""

@check_user
@check_fv_set
@rpcmethod(signature=['array'])
def get_switches(**kwargs):
    '''
    Return what the FlowVisor gives.
    '''
    complete_list = []
    fv = FVServerProxy.objects.all()[0]
    try:
        switches = fv.get_switches()
    except Exception,e:
        import traceback
        traceback.print_exc()
        raise Exception(parseFVexception(e))        
    complete_list.extend(switches)
        
    return complete_list


@check_user
@check_fv_set
@rpcmethod(signature=['array'])
def get_links(**kwargs):
    '''
    Return what the FlowVisor gives.
    '''
    complete_list = []
    fv = FVServerProxy.objects.all()[0]
    try:
        links = fv.get_links()
    except Exception,e:
        import traceback
        traceback.print_exc()
        raise Exception(parseFVexception(e))
    
    complete_list.extend(links)
        
    return complete_list


@check_user
@rpcmethod(signature=['string', 'string', 'string'])
def register_topology_callback(url, cookie, **kwargs):
    '''
    Store some information for the topology callback.
    '''
    from expedient.common import utils

    attrs = {'url': url, 'cookie': cookie}
    filter_attrs = {'username': kwargs['user'].username}
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
    user = kwargs['user']
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
    return "PONG: %s" % data

@check_user
@check_fv_set
@rpcmethod()
def get_granted_flowspace(slice_id, **kwargs):
    '''
    Return FlowVisor Rules for the slice.
    '''
    
    def parse_granted_flowspaces(gfs):
        gfs_list=[] 
        for fs in gfs:
            fs_dict = dict(
                flowspace=dict(),
                openflow=dict()
            )
            fs_dict['openflow']=[]
            fs_dict['flowspace']=dict(
                                     mac_src_s=int_to_mac(fs.mac_src_s),
                                     mac_src_e=int_to_mac(fs.mac_src_e),
                                     mac_dst_s=int_to_mac(fs.mac_dst_s),
                                     mac_dst_e=int_to_mac(fs.mac_dst_e),
                                     eth_type_s=fs.eth_type_s,
                                     eth_type_e=fs.eth_type_e,
                                     vlan_id_s=fs.vlan_id_s,
                                     vlan_id_e=fs.vlan_id_e,
                                     ip_src_s=int_to_dotted_ip(fs.ip_src_s),
                                     ip_dst_s=int_to_dotted_ip(fs.ip_dst_s),
                                     ip_src_e=int_to_dotted_ip(fs.ip_src_e),
                                     ip_dst_e=int_to_dotted_ip(fs.ip_dst_e),
                                     ip_proto_s=fs.ip_proto_s,
                                     ip_proto_e=fs.ip_proto_e,
                                     tp_src_s=fs.tp_src_s,
                                     tp_dst_s=fs.tp_dst_s,
                                     tp_src_e=fs.tp_src_e,
                                     tp_dst_e=fs.tp_dst_e,
                                 )
            openflow_dict=dict(
                                    dpid=fs.dpid, 
                                    direction=fs.direction, 
                                    port_number_s=fs.port_number_s, 
                                    port_number_e=fs.port_number_e, 
                               )
            existing_fs = False
            for prev_dict in gfs_list:
                if fs_dict['flowspace'] == prev_dict['flowspace']:
                    if openflow_dict not in prev_dict['openflow']:
                        prev_dict['openflow'].append(openflow_dict)                        
                    existing_fs = True
                    break
            if not existing_fs:
                fs_dict['openflow'].append(openflow_dict) 
                gfs_list.append(fs_dict)
        
        return gfs_list

    try:
        #TODO: Check 100% that only with slice_id (domain+slice.id) is enough not to crash with some other clearinghouse connected to the optin
        exp = Experiment.objects.filter(slice_id = slice_id)
        gfs = []			
        if exp and len(exp) == 1:
            opts = exp[0].useropts_set.all()
            if opts:
                for opt in opts:
                    gfs_temp = opt.optsflowspace_set.all()
                    gfs.append(parse_granted_flowspaces(gfs_temp))
    except Exception,e:
        import traceback
        traceback.print_exc()
        raise Exception(parseFVexception(e))

    return gfs 

#@check_user
@check_fv_set
@rpcmethod()
def get_offered_vlans(set=None):
    from openflow.optin_manager.opts.vlans.vlanController import vlanController
    vlans =  vlanController.offer_vlan_tags(set)
    return vlans

@check_fv_set
@rpcmethod()
def get_automatic_settings(args=None):
    """
    Get status of the automatic granting of VLANs and approval of Flowspaces
    """
    info = dict()
    auto_approve_settings = FlowSpaceAutoApproveScript.objects.filter(admin=User.objects.filter(is_superuser=True))[0]
    info["vlan_auto_assignment"] = getattr(auto_approve_settings, "vlan_auto_grant", False)
#    info["vlan_auto_assignment"] = getattr(settings, "VLAN_AUTO_ASSIGNMENT", False)
    info["flowspace_auto_approval"] = getattr(auto_approve_settings, "flowspace_auto_approval", False)
#    info["flowspace_auto_approval"] = getattr(settings, "FLOWSPACE_AUTO_APPROVAL", False)
    return info

@check_fv_set
@rpcmethod()
def get_used_vlans(range_len=1, direct_output=False):
    """
    Returns a list with the VLANs used within this OpenFlow aggregate
    @param direct_output defines if only one aggregate is present (True) or more (False)
    """
    range_len = None
    from openflow.optin_manager.opts.vlans.vlanController import vlanController
    import random
    vlans =  vlanController.offer_vlan_tags(range_len)
    if not direct_output or range_len > 1:
        return list(set(range(4096)) - set(vlans))
    else:
        rnd = random.randrange(0, len(vlans))
        # Return random VLAN [from 0 to len(vlans)-1] for all the available to minimise collisions
        return [vlans[rnd]]
          
@check_fv_set
@rpcmethod()
def get_ocf_am_version(args=None):
    """
    Returns the version for the current aggregate
    """
#    sv = open('../../../../../.currentVersion','r')
    import os
    sv = open(os.path.join(settings.SRC_DIR, "..", ".currentVersion"),"r")
    software_version = sv.read().strip()
    sv.close()
    return software_version

@check_fv_set
@rpcmethod()
def get_am_info(args=None):
    """
    Returns a set of information about the aggregate
    """
    # INFO: add as many keys as you wish
    info = dict()
    auto_approve_settings = FlowSpaceAutoApproveScript.objects.filter(admin=User.objects.filter(is_superuser=True))[0]
    info["version"] = get_ocf_am_version()
    info.update(get_automatic_settings())
    return info

