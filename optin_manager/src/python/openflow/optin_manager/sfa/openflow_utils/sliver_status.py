from openflow.optin_manager.opts.models import Experiment
from openflow.optin_manager.flowspace.utils import int_to_mac, int_to_dotted_ip

''' Same get_granted_flowspace function from xmlrpc_srver without decorators'''

def get_sliver_status(slice_id, **kwargs):
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
                    prev_dict['openflow'].append(openflow_dict)
                    existing_fs = True
                    break
            if not existing_fs:
                fs_dict['openflow'].append(openflow_dict)
                gfs_list.append(fs_dict)

        return gfs_list

    try:
        exp = Experiment.objects.filter(slice_id = slice_id)
        if exp and len(exp) == 1:
            opts = exp[0].useropts_set.all()
            if opts:
                gfs = opts[0].optsflowspace_set.all()
                gfs = parse_granted_flowspaces(gfs)
            else:
                gfs = []
        else:
            gfs = []
    except Exception,e:
        raise e

    return gfs
