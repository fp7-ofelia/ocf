

switch_slivers = [{'flowspace': [{'vlan_id_end': 2, 'tp_dst_start': '*', 'nw_dst_start': '*', 'port_num_end': 3, 'dl_dst_end': '*', 'nw_proto_end': '*', 'nw_src_end': '*', 'nw_src_start': '*', 'tp_dst_end': '*', 'dl_dst_start': '*', 'tp_src_start': '*', 'id': 37, 'dl_type_end': '*', 'dl_type_start': '*', 'port_num_start': 3, 'nw_proto_start': '*', 'dl_src_end': '*', 'nw_dst_end': '*', 'dl_src_start': '*', 'tp_src_end': '*', 'vlan_id_start': 2}], 'datapath_id': '00:00:00:00:00:00:00:0e'}, {'flowspace': [{'vlan_id_end': 2, 'tp_dst_start': '*', 'nw_dst_start': '*', 'port_num_end': 1, 'dl_dst_end': '*', 'nw_proto_end': '*', 'nw_src_end': '*', 'nw_src_start': '*', 'tp_dst_end': '*', 'dl_dst_start': '*', 'tp_src_start': '*', 'id': 37, 'dl_type_end': '*', 'dl_type_start': '*', 'port_num_start': 1, 'nw_proto_start': '*', 'dl_src_end': '*', 'nw_dst_end': '*', 'dl_src_start': '*', 'tp_src_end': '*', 'vlan_id_start': 2}], 'datapath_id': '00:00:00:00:00:00:00:0d'}]
slice_id = 'llull.ctx.i2cat.net:3443_46'
project_name = 'SFA Vm management'
project_description = 'Project to manage vms from SFA'
slice_name = 'OFSfaTest'
slice_description = 'bla'
controller_url = 'tcp:10.216.126.2:6633'
owner_email = 'i2catopenflow@gmail.com'
owner_password = 'ofeliaSlicePassword41674'

create_ofv3_rspec(slice_id, project_name, project_description,slice_name, slice_description, controller_url,owner_email, owner_password,switch_slivers, experimentflowspaces):
