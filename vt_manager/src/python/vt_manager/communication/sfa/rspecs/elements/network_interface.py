from sfa.rspecs.elements.element import Element

class NetworkInterface(Element):
    fields = ['from_server',
              'to_network_interface',
	      'port',
              'client_id',
              'ipv4',
              'node_id',
              'interface_id',
              'mac_address',
    ]

