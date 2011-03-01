from XMLRPCServerProxy import PasswordXMLRPCServerProxy
from expedient.common.tests.utils import wrap_xmlrpc_call
import xmlrpclib
from expedient.common.tests.client import Browser


def help_msg(command=None):
    ping_msg = "ping <CH username in OM> <CH password in OM> <OM URL> <ping data> \n"
    create_slice_msg = "create_slice <CH username in OM> <CH password in OM> <OM URL> <slice info> \n"
    slice_info_msg="<slice info>: \n\
        (required)slice_id=<slice id>\n\
        (optional)project_name=<project name> (default:my_project_name)\n\
        (optional)slice_name=<slice name> (default:my_slice_name)\n\
        (optional)project_description=<project description> (default:blah)\n\
        (optional)slice_description=<slice description> (default:blah)\n\
        (required)controller_url=<controller url> \n\
        (optional)owner_email=<owner email> (default:owner@expedient.com)\n\
        (required)owner_password=<owner password> \n\
        (required)switch_slivers=<list of switches and flowspaces> \n\
<switch_slivers> \n\
    list of datapath_id and flowspaces. use the following format:\n\
    '[{\"datapath_id\":\"00:00:00:00:00:00:01\",\"flowspace\":[{\"id\":1,\n\
    \"nw_src_start\":\"192.168.1.1\",\"nw_src_end\":\"192.168.1.255\"}]},{\"datapath_id\"\n\
    :\"00:00:00:00:00:00:02\",\"flowspace\":[{\"id\":2,\"port_number_start\":\"1\",\n\
    \"port_number_end\":\"4\"}]}]'\n\
flowspace fields:\n\
    (required)id: an id used for this flowspace\n\
    (optional)port_number_star, port_number_end (default:0,65535)\n\
    (optional)dl_src_start,dl_src_end (default: MAC address range)\n\
    (optional)dl_dst_start,dl_dst_end (default: MAC address range)\n\
    (optional)vlan_id_start,vlan_id_end (default: whole vlan id range)\n\
    (optional)nw_src_start,nw_src_end (default: IP address range)\n\
    (optional)nw_dst_start,nw_dst_end (default: IP address range)\n\
    (optional)nw_proto_start,nw_proto_end (default: 0,255)\n\
    (optional)tp_src_start,tp_src_end (default: transport layer port range)\n\
    (optional)tp_dst_start,tp_dst_end (default: transport layer port range)\n\
        "
    delete_slice_msg = "delete_slice <CH username in OM> <CH password in OM> <OM URL> <slice id> \n"
    get_switches_msg = "get_switches <CH username in OM> <CH password in OM> <OM URL> \n"
    get_links_msg = "get_links <CH username in OM> <CH password in OM> <OM URL> \n"
    change_password_msg = "change_password <CH username in OM> <CH password in OM> <OM URL> <new password>\n"
    register_topology_callback_msg = "register_topology_callback <CH username in OM> <CH password in OM> <OM URL> <url> <cookie>\n"
    opt_in_msg = "opt_in <username in OM> <password in OM> <OM URL> <project name> <slice name> <priority (e.g.100)>\n"
    opt_out_msg = "opt_out <username in OM> <password in OM> <OM URL> <project name> <slice name> \n"

    if (command == "ping"):
        return "python omctl.py %s"%ping_msg
    elif (command == "create_slice"):
        return "python omctl.py %s %s"%(create_slice_msg,slice_info_msg)
    elif (command == "delete_slice"):
        return "python omctl.py %s"%(delete_slice_msg)
    elif (command == "get_switches"):
        return "python omctl.py %s"%(get_switches_msg)
    elif (command == "get_links"):
        return "python omctl.py %s"%(get_links_msg)
    elif (command == "change_password"):
        return "python omctl.py %s"%(change_password_msg)
    elif (command == "register_topology_callback"):
        return "python omctl.py %s"%(register_topology_callback_msg)
    elif (command == "opt_in"):
        return "python omctl.py %s"%(opt_in_msg)
    elif (command == "opt_out"):
        return "python omctl.py %s"%(opt_out_msg)
    else:    
        return "python omctl.py <command> <inputs> \n %s %s %s %s %s %s %s %s"%\
            (ping_msg,create_slice_msg,delete_slice_msg,get_switches_msg,
             get_links_msg, change_password_msg,register_topology_callback_msg,
             opt_in_msg)
    
    
def xmlrpc_wrap_ping(username,password,url,ping_data):
    xmlrpc_proxy = PasswordXMLRPCServerProxy()
    xmlrpc_proxy.setup(username, password, url, False)
    try:
        data = wrap_xmlrpc_call(xmlrpc_proxy.ping,[ping_data],{},10)
        return data
    except Exception,e:
        return str(e)
    
def xmlrpc_wrap_create_slice(username, password, url, args):
    import ast

    slice_id = None
    project_name = "my_project_name"
    slice_name = "my_slice_name"
    project_description = "blah"
    slice_description = "blah"
    controller_url = None
    owner_email = "owner@expedient.com"
    owner_password = None
    switch_slivers = None
    for arg in args:
        if arg.startswith("slice_id="):
            parts = arg.split('=')
            slice_id = int(parts[1])
        elif arg.startswith("project_name="):
            parts = arg.split('=')
            project_name = parts[1]
        elif arg.startswith("slice_name="):
            parts = arg.split('=')
            slice_name = parts[1]
        elif arg.startswith("project_description="):
            parts = arg.split('=')
            project_description = parts[1]
        elif arg.startswith("slice_description="):
            parts = arg.split('=')
            slice_description = parts[1]
        elif arg.startswith("controller_url="):
            parts = arg.split('=')
            controller_url = parts[1]
        elif arg.startswith("owner_email="):
            parts = arg.split('=')
            owner_email = parts[1]
        elif arg.startswith("owner_password="):
            parts = arg.split('=')
            owner_password = parts[1]
        elif arg.startswith("switch_slivers="):
            parts = arg.split('=')
            try:
                switch_slivers = ast.literal_eval(parts[1])
            except Exception,e:
                return str(e)  
    if not (slice_id and controller_url and owner_password and switch_slivers):
        return "Invalid syntax: %s"%help_msg("create_slice")
    xmlrpc_proxy = PasswordXMLRPCServerProxy()
    xmlrpc_proxy.setup(username, password, url, False)
    try:
        returned = wrap_xmlrpc_call(xmlrpc_proxy.create_slice,[slice_id,project_name, 
                project_description,slice_name, slice_description, controller_url,
                owner_email, owner_password,switch_slivers],{},10)
        return returned
    except Exception,e:
        return str(e)
    
def xmlrpc_wrap_delete_slice(username, password, url, slice_id):
    xmlrpc_proxy = PasswordXMLRPCServerProxy()
    xmlrpc_proxy.setup(username, password, url, False)
    try:
        returned_data = wrap_xmlrpc_call(xmlrpc_proxy.delete_slice,[slice_id],{},10)
        return returned_data
    except Exception,e:
        return str(e)   
   
def xmlrpc_wrap_get_switches(username, password, url):
    xmlrpc_proxy = PasswordXMLRPCServerProxy()
    xmlrpc_proxy.setup(username, password, url, False)
    try:
        returned_data = wrap_xmlrpc_call(xmlrpc_proxy.get_switches,[],{},10)
        return returned_data
    except Exception,e:
        return str(e)
    
def xmlrpc_wrap_get_links(username, password, url):
    xmlrpc_proxy = PasswordXMLRPCServerProxy()
    xmlrpc_proxy.setup(username, password, url, False)
    try:
        returned_data = wrap_xmlrpc_call(xmlrpc_proxy.get_links,[],{},10)
        return returned_data
    except Exception,e:
        return str(e)
    
def xmlrpc_wrap_change_password(username, password, url,new_password):
    xmlrpc_proxy = PasswordXMLRPCServerProxy()
    xmlrpc_proxy.setup(username, password, url, False)
    try:
        returned_data = wrap_xmlrpc_call(xmlrpc_proxy.change_password,[new_password],{},10)
        return returned_data
    except Exception,e:
        return str(e)
    
def xmlrpc_wrap_register_topology_callback(username, password, om_url,url,cookie):
    xmlrpc_proxy = PasswordXMLRPCServerProxy()
    xmlrpc_proxy.setup(username, password, om_url, False)
    try:
        returned_data = wrap_xmlrpc_call(xmlrpc_proxy.register_topology_callback,[url,cookie],{},10)
        return returned_data
    except Exception,e:
        return str(e)
    
def http_wrap_opt_in(username, password, url, project_name, slice_name, priority):
    b = Browser()
    
    #log in first
    log_in_url = "%s/accounts/login/"%url
    logged_in = b.login(log_in_url, "user", "password")
    if not logged_in:
        return "Log in unsuccessful. Please check username and password"
    
    #get experiment id:
    opt_in_url = "%s/opts/opt_in"%url
    f = b.get_form(opt_in_url)
    options = b.get_select_choices(f.read(),"experiment")
    try:
        id = options["%s:%s"%(project_name,slice_name)]
    except Exception,e:
        return "Experiment %s:%s doesn't exist"%(project_name,slice_name)
    
    #opt in request
    f = b.get_and_post_form(opt_in_url, dict(experiment=id,priority=priority))
    if ("success" in f.read()):
        return "Opt in was successful"
    else:
        return f.read()
    
def http_wrap_opt_out(username, password, url, project_name, slice_name):
    b = Browser()
    
    #log in first
    log_in_url = "%s/accounts/login/"%url
    logged_in = b.login(log_in_url, "user", "password")
    if not logged_in:
        return "Log in unsuccessful. Please check username and password"
    
    #get experiment id:
    opt_out_url = "%s/opts/opt_out"%url
    f = b.get_form(opt_out_url)
    options = b.get_checkbox_choices(f.read())

    try:
        id = options["%s:%s"%(project_name,slice_name)]
    except Exception,e:
        return "%s has not opted into experiment %s:%s"%(username,project_name,slice_name)
    
    #opt in request
    data = {}
    data[id] = "checked"
    f = b.get_and_post_form(opt_out_url, data)
    if ("Successful" in f.read()):
        return "Opt out was successful"
    else:
        return f.read()
    
    