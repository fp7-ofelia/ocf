def parse_granted_flowspaces(gfs):
    gfs_list=[]
    for fs in gfs:
        fs_dict = dict(
            flowspace=dict(),
            openflow=dict()
        )
        fs_dict['flowspace']=dict(
                                 mac_src_s=fs.mac_src_s,
                                 mac_src_e=fs.mac_src_e,
                                 mac_dst_s=fs.mac_dst_s,
                                 mac_dst_e=fs.mac_dst_e,
                                 eth_type_s=fs.eth_type_s,
                                 eth_type_e=fs.eth_type_e,
                                 vlan_id_s=fs.vlan_id_s,
                                 vlan_id_e=fs.vlan_id_e,
                                 ip_src_s=fs.ip_src_s,
                                 ip_dst_s=fs.ip_dst_s,
                                 ip_src_e=fs.ip_src_e,
                                 ip_dst_e=fs.ip_dst_e,
                                 ip_proto_s=fs.ip_proto_s,
                                 ip_proto_e=fs.ip_proto_e,
                                 tp_src_s=fs.tp_src_s,
                                 tp_dst_s=fs.tp_dst_s,
                                 tp_src_e=fs.tp_src_e,
                                 tp_dst_e=fs.tp_dst_e,
                             )
        fs_dict['openflow']=dict(
                                dpid=fs.dpid,
                                direction=fs.direction,
                                port_number_s=fs.port_number_s,
                                port_number_e=fs.port_number_e,
                           )
        gfs_list.append(fs_dict)
        return gfs_list

