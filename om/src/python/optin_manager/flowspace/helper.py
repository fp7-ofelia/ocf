from optin_manager.flowspace.models import FlowSpace
from optin_manager.flowspace.utils import MACtoInt, DottedIPToInt
from optin_manager.xmlrpc_server.ch_api import om_ch_translate

def SingleFSIntersect(f1,f2,resultModel):
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



def MultiFSIntersect(FSs1, FSs2, resultModel):
    rFSs = []
    for FS1 in FSs1:
        for FS2 in FSs2:
            rFS = SingleFSIntersect(FS1,FS2, resultModel)
            if (rFS):
                rFSs.append(rFS)
                
    return rFSs

def makeFlowSpace(PostObject):
    f = FlowSpace()
    if (PostObject['mac_from'] == "*"):
        f.mac_src_s = 0
        f.mac_src_e = 0xffffffffffff
    else:
        f.mac_src_s = MACtoInt(PostObject['mac_from'])
        f.mac_src_e = MACtoInt(PostObject['mac_from'])
        
    if (PostObject['mac_to'] == "*"):
        f.mac_dst_s = 0
        f.mac_dst_e = 0xffffffffffff
    else:
        f.mac_dst_s = MACtoInt(PostObject['mac_to'])
        f.mac_dst_e = MACtoInt(PostObject['mac_to'])
    
    f.vlan_id_s = int(PostObject['vlan_id_s'])
    f.vlan_id_e = int(PostObject['vlan_id_e'])
    
    f.ip_src_s = DottedIPToInt(PostObject['ip_from_s'])
    f.ip_src_e= DottedIPToInt(PostObject['ip_from_e'])
    
    f.ip_dst_s = DottedIPToInt(PostObject['ip_to_s'])
    f.ip_dst_e= DottedIPToInt(PostObject['ip_to_e'])     
    
    f.ip_proto_s = int(PostObject['ip_proto_s'])
    f.ip_proto_e = int(PostObject['ip_proto_e'])

    f.tp_src_s = int(PostObject['tp_from_s'])
    f.tp_src_e = int(PostObject['tp_from_e'])

    f.tp_dst_s = int(PostObject['tp_to_s'])
    f.tp_dst_e = int(PostObject['tp_to_e'])
                
    return f
    
    
def RangeToMatchStruct(rangeFS):
    match = {}
    for attr_name, (to_str, from_str, width, om_name, of_name) in om_ch_translate.attr_funcs.items():
        om_start = "%s_s" % om_name
        om_end = "%s_e" % om_name
        if (getattr(rangeFS,om_start) > 0 or getattr(rangeFS,om_end) < 2**width-1):
            if (getattr(rangeFS,om_start) == getattr(rangeFS,om_end)):
                match[attr_name] = to_str(getattr(rangeFS,om_start))
            else:
                #TODO: fix it later: for now we just find the full x.x.x.x/y format that contain the interval
                if (attr_name == "nw_src" or attr_name == "nw_dst"):
                    ips = getattr(rangeFS,om_start)
                    ipe = getattr(rangeFS,om_end)
                    common = ips ^ ipe
                    #count numebr of common bits
                    leftmost_position = 0
                    for i in range(0,31):
                        if (common & 0x1<<i):
                            leftmost_position = i
                    match[attr_name] = "%s/%d"%(to_str(ips & (0xFFFFFFFF<<leftmost_position)),31-leftmost_position)
                    
                    
                else:
                    # TODO: If we expand this case, result will EXPLODE -- avoid it at any cost!
                    # we may prevent users from entering ranges
                    print "In Range to match function, a range replaced with full call"
    result = ""
    for key in match:
        result = "%s%s=%s , "%(result,key,match[key])
 
    return result
