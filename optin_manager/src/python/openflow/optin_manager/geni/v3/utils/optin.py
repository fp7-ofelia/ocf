import random

from openflow.optin_manager.flowspace.utils import mac_to_int
from openflow.optin_manager.flowspace.utils import int_to_mac
from openflow.optin_manager.flowspace.utils import dotted_ip_to_int
from openflow.optin_manager.flowspace.utils import int_to_dotted_ip

class OptinUtils:

    @staticmethod
    def format_flowspaces(fs, port):
        flowspaces = list()
        if fs.get_dl_src(): #Not Ranges, input in MAC Type
            dl_src_ranges = list()
            for dl_src_range in fs.get_dl_src():
                dl_src_ranges.extend(OptinUtils.parse_mac_not_ranged_types(dl_src_range))
        else:
            dl_src_ranges = [(None,None)]

        if fs.get_dl_dst(): #Not Ranges, input in MAC Type
            dl_dst_ranges = list()
            for dl_dst_range in fs.get_dl_dst():
                dl_dst_ranges.extend(OptinUtils.parse_mac_not_ranged_types(dl_dst_range))
        else:
            dl_dst_ranges = [(None,None)]

        if fs.get_dl_type(): #Not Ranges, input in HEX Type
            dl_type_ranges = list()
            for rang in fs.get_dl_type():
                dl_type_ranges.extend(OptinUtils.parse_hex_not_ranged_types(rang))
        else:
            dl_type_ranges = [(None,None)]

        if fs.get_dl_vlan(): #Ranges Supported Input in DEC Type
            dl_vlan_ranges = list()
            for rang in fs.get_dl_vlan():
                dl_vlan_ranges.extend(OptinUtils.parse_dec_ranged_types(rang))

        else:
            dl_vlan_ranges = [(None,None)]

        if fs.get_nw_src(): #Not Ranges,  CIDR Input Format 
            nw_src_ranges = list()
            for rang in fs.get_nw_src():
                nw_src_ranges.extend(OptinUtils.parse_cidr_not_ranged_types(rang))

        else:
            nw_src_ranges = [(None,None)]

        if fs.get_nw_dst(): #Not Ranges,  CIDR Input Format
            nw_dst_ranges = list()
            for rang in fs.get_nw_dst():
               nw_dst_ranges.extend(OptinUtils.parse_cidr_not_ranged_types(rang))

        else:
            nw_dst_ranges = [(None,None)]

        if fs.get_nw_proto():#Supports Ranges, Decimal Input
            nw_proto_ranges = list()
            for rang in fs.get_nw_proto():
                nw_proto_ranges.extend(OptinUtils.parse_dec_ranged_types(rang))

        else:
            nw_proto_ranges = [(None,None)]

        if fs.get_tp_src(): #Supports Ranges, Input in Decimal
            tp_src_ranges = list()
            for rang in fs.get_tp_src():
                for value in rang.split(","):
                    tp_src_ranges.extend(OptinUtils.parse_dec_ranged_types(value))

        else:
            tp_src_ranges = [(None,None)]

        if fs.get_tp_dst():  #Supports Ranges, Input in Decimal
            tp_dst_ranges = list()
            for rang in fs.get_tp_dst():
                for value in rang.split(","):
                    tp_dst_ranges.extend(OptinUtils.parse_dec_ranged_types(value))

        else:
            tp_dst_ranges = [(None,None)]

        for dl_src_range in dl_src_ranges:
            for dl_dst_range in dl_dst_ranges:
                for dl_type_range in dl_type_ranges:
                    for nw_proto_range in nw_proto_ranges:
                        for dl_vlan_range in dl_vlan_ranges:
                            for nw_src_range in nw_src_ranges:
                                for nw_dst_range in nw_dst_ranges:
                                    for tp_src_range in tp_src_ranges:
                                        for tp_dst_range in tp_dst_ranges:
                                        
                                            flowspace = {'dl_dst_end':dl_dst_range[1],
                                                         'dl_dst_start':dl_dst_range[0],
                                                         'dl_src_end': dl_src_range[1],
                                                         'dl_src_start': dl_src_range[0],
                                                         'dl_type_end': dl_type_range[1],
                                                         'dl_type_start': dl_type_range[0],
                                                         'id':random.randint(0, 10000),
                                                         'nw_dst_end': nw_dst_range[1],
                                                         'nw_dst_start': nw_dst_range[0],
                                                         'nw_src_end': nw_src_range[1],
                                                         'nw_src_start': nw_src_range[0],
                                                         'port_num_end': port,
                                                         'port_num_start': port,
                                                         'nw_proto_end': nw_proto_range[1],
                                                         'nw_proto_start': nw_proto_range[0],
                                                         'tp_dst_end': tp_dst_range[1],
                                                         'tp_dst_start': tp_dst_range[0],
                                                         'tp_src_end': tp_src_range[1],
                                                         'tp_src_start': tp_src_range[0],
                                                         'vlan_id_end': dl_vlan_range[1],
                                                         'vlan_id_start': dl_vlan_range[0]}
                                            flowspaces.append(flowspace)
        return flowspaces

    @staticmethod
    def get_values(str_range):

        to_return = str_range.split('-')
        if len(to_return) == 2:
            return to_return[0], to_return[1]
        elif len(to_return) == 1:
            return int(to_return[0],16), int(to_return[0],16)
    
    @staticmethod
    def get_ranges(packet_field, mac_dl=False, integer=False):
    
        ints = list()
        params = packet_field.split(',')
        if not type(params) == list:
            params = [params]
        if mac_dl == True:
            for param in params: 
                ints.append(mac_to_int(param))
        elif integer == True:
            for param in params:
                try:
                    ints.append(int(param))
                except Exception as e:
                    ints.append(int(param,16))
                    
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
    
    @staticmethod		
    def cidr_ip_to_range(cidr_ip):
        ip, mask = cidr_ip.split('/')
        ip_int = dotted_ip_to_int(ip)
        addresses = (2**(32-int(mask)))-1
        final_ip_int = ip_int + addresses
        dotted_ip = int_to_dotted_ip(final_ip_int)
        return ip_int,final_ip_int

    @staticmethod
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

    @staticmethod
    def parse_hex_not_ranged_types(in_strs):
        in_strs = in_strs.split(',')
        if not type(in_strs) == list:
            in_strs = [in_strs]
        output = list()
        for in_str in in_strs:
           hex_in = int(in_str,16)
           output.append((hex_in,hex_in))
        return output

    @staticmethod
    def parse_mac_not_ranged_types(in_strs):
        in_strs = in_strs.split(',')
        if not type(in_strs) == list:
            in_strs = [in_strs]
        output = list()
        for in_str in in_strs:
           mac_int = int_to_mac(in_str) 
           output.append((mac_int,mac_int))
        return output

    @staticmethod
    def parse_dec_ranged_types(in_strs):
        in_strs = in_strs.split(',')
        if not type(in_strs) == list:
            in_strs = [in_strs]
        output = list()
        for in_str in in_strs:
           if len(in_str) > 1:
               output.append((int(in_str[0]),int(in_str[1])))     
           else:
               output.append((int(in_str),int(in_str)))
        return output

    @staticmethod
    def parse_dec_ranged_types(in_strs):
        in_strs = in_strs.split(',')
        if not type(in_strs) == list:
            in_strs = [in_strs]
        output = list()
        for in_str in in_strs:
           in_str = in_str.split("-") 
           if len(in_str) > 1:
               output.append((int(in_str[0]),int(in_str[1])))
           else:
               output.append((int(in_str[0]),int(in_str[0])))
        return output         

    @staticmethod
    def parse_cidr_not_ranged_types(in_strs):
        in_strs = in_strs.split(',')
        if not type(in_strs) == list:
            in_strs = [in_strs]
        output = list()
        for in_str in in_strs:
           cidr = OptinUtils.cidr_ip_to_range(in_str) #int cidr tuple
           output.append(cidr)
        return output

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

