from openflow.optin_manager.flowspace.utils import mac_to_int, int_to_mac, dotted_ip_to_int, int_to_dotted_ip

def get_fs_from_group(match_rspec, groups={}):
    flowspaces = list()
    for rspec in match_rspec:
        fs = dict()
        datapaths = get_datapaths(rspec['datapath'],rspec['use-group'],groups) #get used-groups and match datapaths 
        for datapath in datapaths:
            flowspaces.append({'datapath_id':datapath['dpid'], 'flowspace': get_flowspaces(rspec['packet'][0],datapath['ports'])}) 
	return flowspaces

def get_datapaths(datapaths, used_groups, groups):
    dps = list()
    group_names = get_group_names(used_groups)
    for group_name in group_names:
        for group in groups:
            if group['name'] == group_name:
		dps.extend(group['datapath'])
    dps.extend(datapaths)
    return dps

def get_flowspaces(packet, ports):
    port_list = [port['num'] for port in ports]
    flowspaces = list()
    if packet['dl_src']:
        dl_src_ranges = get_ranges(packet['dl_src'], mac_dl=True, integer=False)
    else:
	dl_src_ranges = [('*','*')]
    if packet['dl_dst']:
        dl_dst_ranges = get_ranges(packet['dl_dst'], mac_dl=True, integer=False)
    else:
        dl_dst_ranges = [('*','*')]
    if packet['dl_type']:
        dl_type_ranges = get_ranges(packet['dl_type'],mac_dl=False)
    else:
        dl_type_ranges = [('*','*')]
    if packet['dl_vlan']:
        dl_vlan_ranges = get_values(packet['dl_vlan'])
    else:
        dl_vlan_ranges = ['*','*']
    if packet['nw_src']:
        nw_src_ranges = cidr_ip_to_range(packet['nw_src'])
    else:
        nw_src_ranges = ('*','*')
    if packet['nw_dst']:
        nw_dst_ranges = cidr_ip_to_range(packet['nw_dst'])
    else:
        nw_dst_ranges = ('*','*')
    if packet['nw_proto']:
        nw_proto_ranges = get_ranges(packet['nw_proto'], integer=True)
    else: 
        nw_proto_ranges = [('*','*')]
    if packet['tp_src']:
	tp_src_ranges = get_values(packet['tp_src'])
    else:
        tp_src_ranges = ['*','*']
    if packet['tp_dst']:
        tp_dst_ranges = get_values(packet['tp_dst'])
    else:
        tp_dst_ranges = ['*','*']

    for port in port_list:
        for dl_src_range in dl_src_ranges:
            for dl_dst_range in dl_dst_ranges:
                for dl_type_range in dl_type_ranges:
                    for nw_proto_range in nw_proto_ranges:
                        flowspace = {'dl_dst_end':dl_dst_range[1],
                                     'dl_dst_start':dl_dst_range[0],
                                     'dl_src_end': dl_src_range[1],
                                     'dl_src_start': dl_src_range[0],
                                     'dl_type_end': dl_type_range[1],
                                     'dl_type_start': dl_type_range[0],
                                     'id': 37,
                                     'nw_dst_end': nw_dst_ranges[1],
                                     'nw_dst_start': nw_dst_ranges[0],
                                     'nw_src_end': nw_src_ranges[1],
                                     'nw_src_start': nw_src_ranges[0],
                                     'port_num_end': port,
                                     'port_num_start': port,
                                     'nw_proto_end': nw_proto_range[1],
                                     'nw_proto_start': nw_proto_range[0],
                                     'tp_dst_end': tp_dst_ranges[1],
                                     'tp_dst_start': tp_dst_ranges[0],
                                     'tp_src_end': tp_src_ranges[1],
                                     'tp_src_start': tp_src_ranges[0],
                                     'vlan_id_end': dl_vlan_ranges[1],
                                     'vlan_id_start': dl_vlan_ranges[0]}
                        flowspaces.append(flowspace)

    return flowspaces	
	
def get_values(str_range):

    to_return = str_range['value'].split('-')
    if len(to_return) == 2:
        return to_return[0], to_return[1]
    elif len(to_return) == 1:
        return to_return[0], to_return[0]

def get_ranges(packet_field, mac_dl=False, integer=False):

    ints = list()
    params = packet_field['value'].split(',')
    if mac_dl == True:
        for param in params: 
            ints.append(mac_to_int(param))
    elif integer == True:
        for param in params:
            ints.append(int(param))
    else:
	for param in params:
	    ints.append(int(param,16)) # all params should be in hexadecimal format
             
    ints.sort()
    ranges = list()
    current_range = list()
    for i,intn in enumerate(ints):
	if not len(current_range) > 0 or current_range[-1] == (intn -1):
	    current_range.append(intn)
        if not (current_range[-1] == (intn -1)) or i == len(ints)-1:
            if mac_dl == True:
                ranges.append((int_to_mac(current_range[0]),int_to_mac(current_range[-1])))
            elif integer == False:
                ranges.append((hex(current_range[0]),hex(current_range[-1])))
	    else:
		ranges.append((current_range[0],current_range[-1]))
	    current_range = []
    return ranges
		
def cidr_ip_to_range(cidr_ip): 
    ip, mask = cidr_ip['value'].split('/')
    ip_int = dotted_ip_to_int(ip)
    addresses = (2**(32-int(mask)))-1
    final_ip_int = ip_int + addresses
    dotted_ip = int_to_dotted_ip(final_ip_int)
    return ip,dotted_ip

def get_group_names(used_groups):
    group_names = list()
    for used_group in used_groups:
        group_names.append(used_group['name'])
    return group_names
	

