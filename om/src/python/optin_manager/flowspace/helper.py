from optin_manager.flowspace.models import FlowSpace
from optin_manager.flowspace.utils import mac_to_int, dotted_ip_to_int
from optin_manager.xmlrpc_server.ch_api import om_ch_translate

def single_fs_intersect(f1,f2,resultModel):
    fr = resultModel()
    
    fr.mac_src_s = max(f1.mac_src_s, f2.mac_src_s)
    fr.mac_src_e = min(f1.mac_src_e, f2.mac_src_e)
    
    if (fr.mac_src_s > fr.mac_src_e):
        return None

    fr.mac_dst_s = max(f1.mac_dst_s, f2.mac_dst_s)
    fr.mac_dst_e = min(f1.mac_dst_e, f2.mac_dst_e)
    #print fr
    if (fr.mac_dst_s > fr.mac_dst_e):
        return None  
    
    fr.eth_type_s = max(f1.eth_type_s, f2.eth_type_s)
    fr.eth_type_e = min(f1.eth_type_e, f2.eth_type_e)
    #print fr
    if (fr.eth_type_s > fr.eth_type_e):
        return None 

    fr.vlan_id_s = max(f1.vlan_id_s , f2.vlan_id_s )
    fr.vlan_id_e  = min(f1.vlan_id_e , f2.vlan_id_e )
    #print fr
    if (fr.vlan_id_s  > fr.vlan_id_e ):
        return None
    
    fr.ip_src_s = max(f1.ip_src_s , f2.ip_src_s )
    fr.ip_src_e  = min(f1.ip_src_e , f2.ip_src_e )
    #print fr
    if (fr.ip_src_s  > fr.ip_src_e ):
        return None

    fr.ip_dst_s = max(f1.ip_dst_s , f2.ip_dst_s )
    fr.ip_dst_e  = min(f1.ip_dst_e , f2.ip_dst_e )
    #print fr
    if (fr.ip_dst_s  > fr.ip_dst_e ):
        return None

    fr.ip_proto_s = max(f1.ip_proto_s , f2.ip_proto_s )
    fr.ip_proto_e  = min(f1.ip_proto_e , f2.ip_proto_e )
    #print fr
    if (fr.ip_proto_s  > fr.ip_proto_e ):
        return None

    fr.tp_src_s = max(f1.tp_src_s , f2.tp_src_s )
    fr.tp_src_e  = min(f1.tp_src_e , f2.tp_src_e )
    #print fr
    if (fr.tp_src_s  > fr.tp_src_e ):
        return None

    fr.tp_dst_s = max(f1.tp_dst_s , f2.tp_dst_s )
    fr.tp_dst_e  = min(f1.tp_dst_e , f2.tp_dst_e )
    #print fr
    if (fr.tp_dst_s  > fr.tp_dst_e ):
        return None
    
    return fr



def multi_fs_intersect(FSs1, FSs2, resultModel):
    rFSs = []
    for FS1 in FSs1:
        for FS2 in FSs2:
            rFS = single_fs_intersect(FS1,FS2, resultModel)
            if (rFS):
                rFSs.append(rFS)
                
    return rFSs

def make_flowspace(PostObject):
    f = FlowSpace()
    if (PostObject['mac_from'] == "*"):
        f.mac_src_s = 0
        f.mac_src_e = 0xffffffffffff
    else:
        f.mac_src_s = mac_to_int(PostObject['mac_from'])
        f.mac_src_e = mac_to_int(PostObject['mac_from'])
        
    if (PostObject['mac_to'] == "*"):
        f.mac_dst_s = 0
        f.mac_dst_e = 0xffffffffffff
    else:
        f.mac_dst_s = mac_to_int(PostObject['mac_to'])
        f.mac_dst_e = mac_to_int(PostObject['mac_to'])
    
    f.vlan_id_s = int(PostObject['vlan_id_s'])
    f.vlan_id_e = int(PostObject['vlan_id_e'])
    
    f.ip_src_s = dotted_ip_to_int(PostObject['ip_from_s'])
    f.ip_src_e= dotted_ip_to_int(PostObject['ip_from_e'])
    
    f.ip_dst_s = dotted_ip_to_int(PostObject['ip_to_s'])
    f.ip_dst_e= dotted_ip_to_int(PostObject['ip_to_e'])     
    
    f.ip_proto_s = int(PostObject['ip_proto_s'])
    f.ip_proto_e = int(PostObject['ip_proto_e'])

    f.tp_src_s = int(PostObject['tp_from_s'])
    f.tp_src_e = int(PostObject['tp_from_e'])

    f.tp_dst_s = int(PostObject['tp_to_s'])
    f.tp_dst_e = int(PostObject['tp_to_e'])
                
    return f
    
    
def range_to_match_struct(rangeFS):
    match = {}
    for attr_name, (to_str, from_str, width, om_name, of_name) in om_ch_translate.attr_funcs.items():
        om_start = "%s_s" % om_name
        om_end = "%s_e" % om_name
        match[of_name] = []
        if (getattr(rangeFS,om_start) > 0 or getattr(rangeFS,om_end) < 2**width-1):
            if (getattr(rangeFS,om_start) == getattr(rangeFS,om_end)):
                match[of_name].append(to_str(getattr(rangeFS,om_start)))
            else:
                if (attr_name == "nw_src" or attr_name == "nw_dst"):
                    ips = getattr(rangeFS,om_start)
                    ipe = getattr(rangeFS,om_end)
                    while (ips <= ipe):
                        for i in range(1,32):
                            if not ((ips | (2**i - 1 )) < ipe and (ips % 2**i)==0) :
                                obtained_match = "%s/%d"%(to_str(ips),33-i)
                                match[of_name].append(obtained_match)
                                ips = (ips| (2**(i-1) - 1 )) + 1
                                break
                else:
                    for value in range(getattr(rangeFS,om_start), getattr(rangeFS, om_end)):
                        match[of_name].append(to_str(value))
                        
    #Now try to combine different of_name(s) together:
    all_match = [""]
    for key in match.keys():
        new_match = []
        for value in match[key]:
            for elem in all_match:
                new_match.append("%s%s=%s , "%(elem,key,value))
        if len(match[key]) > 0:
            all_match = new_match
 
    return all_match
