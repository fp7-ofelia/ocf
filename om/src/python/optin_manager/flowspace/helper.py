from flowspace.models import FlowSpace
from flowspace.utils import MACtoInt, DottedIPToInt

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
        
    f.eth_type_s = 0x0800
    f.eth_type_e = 0x0800
    
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
    
