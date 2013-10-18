from openflow.optin_manager.opts.models import *
from openflow.optin_manager.xmlrpc_server.ch_api import convert_star
from openflow.optin_manager.xmlrpc_server.ch_api import om_ch_translate

def l(switch_slivers):
     
    e = Experiment()   

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
    return all_efs

svrs = [{'flowspace': [{'vlan_id_end': 2L, 'nw_src_start': '*', 'nw_dst_start': '*', 'dl_src_end': '*', 'port_num_end': 1L, 'tp_dst_start': '*', 'dl_dst_end': '*', 'tp_dst_end': '*', 'nw_src_end': '*', 'port_num_start': 1L, 'nw_proto_end': '*', 'dl_dst_start': '*', 'tp_src_start': '*', 'vlan_id_start': 2L, 'dl_type_end': '*', 'nw_proto_start': '*', 'dl_type_start': '*', 'nw_dst_end': '*', 'dl_src_start': '*', 'tp_src_end': '*', 'id': 88L}, {'vlan_id_end': 2L, 'nw_src_start': '*', 'nw_dst_start': '*', 'dl_src_end': '*', 'port_num_end': 2L, 'tp_dst_start': '*', 'dl_dst_end': '*', 'tp_dst_end': '*', 'nw_src_end': '*', 'port_num_start': 2L, 'nw_proto_end': '*', 'dl_dst_start': '*', 'tp_src_start': '*', 'vlan_id_start': 2L, 'dl_type_end': '*', 'nw_proto_start': '*', 'dl_type_start': '*', 'nw_dst_end': '*', 'dl_src_start': '*', 'tp_src_end': '*', 'id': 88L}, {'vlan_id_end': 2L, 'nw_src_start': '*', 'nw_dst_start': '*', 'dl_src_end': '*', 'port_num_end': 65534L, 'tp_dst_start': '*', 'dl_dst_end': '*', 'tp_dst_end': '*', 'nw_src_end': '*', 'port_num_start': 65534L, 'nw_proto_end': '*', 'dl_dst_start': '*', 'tp_src_start': '*', 'vlan_id_start': 2L, 'dl_type_end': '*', 'nw_proto_start': '*', 'dl_type_start': '*', 'nw_dst_end': '*', 'dl_src_start': '*', 'tp_src_end': '*', 'id': 88L}], 'datapath_id': u'00:00:00:00:00:00:00:09'}, {'flowspace': [{'vlan_id_end': 2L, 'nw_src_start': '*', 'nw_dst_start': '*', 'dl_src_end': '*', 'port_num_end': 1L, 'tp_dst_start': '*', 'dl_dst_end': '*', 'tp_dst_end': '*', 'nw_src_end': '*', 'port_num_start': 1L, 'nw_proto_end': '*', 'dl_dst_start': '*', 'tp_src_start': '*', 'vlan_id_start': 2L, 'dl_type_end': '*', 'nw_proto_start': '*', 'dl_type_start': '*', 'nw_dst_end': '*', 'dl_src_start': '*', 'tp_src_end': '*', 'id': 90L}], 'datapath_id': u'00:00:00:00:00:00:00:0a'}]

z = l(svrs)
print z

