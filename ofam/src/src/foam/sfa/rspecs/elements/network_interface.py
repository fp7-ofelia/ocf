from foam.sfa.rspecs.elements.element import Element

class NetworkInterface(Element):
    fields = ['from_server_id',
	      'from_server_name'
	      'from_server_interface_id',
	      'from_server_interface_name',
	      'to_netwrk_interface_name',
              'to_network_interface_id',
	      'to_network_interface_port',
              'client_id',
              'ipv4',
              'node_id',
              'interface_id',
              'mac_address',
    ]

