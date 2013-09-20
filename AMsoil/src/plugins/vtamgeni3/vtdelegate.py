import time 

import amsoil.core.pluginmanager as pm

import xml.etree.ElementTree as ET

from util.xrn import *


'''@author: SergioVidiella'''


GENIv3DelegateBase = pm.getService('geniv3delegatebase')
geni_ex = pm.getService('geniv3exceptions')
vt_ex = pm.getService('vtexceptions')

class VTDelegate(GENIv3DelegateBase):
    """
	A Delegate for the VT AM 
    """

    def __init__(self):
        super(VTDelegate, self).__init__()
        self._resource_manager = pm.getService("vtresourcemanager")

    #TODO: set the location of the schemas
    #TODO: redo the schemas according to the fields needed
    def get_request_extensions_mapping(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return {'vtam' : 'https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/schema.xsd'} # /request.xsd

    def get_manifest_extensions_mapping(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return {'vtam' : 'https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/schema.xsd'} # /manifest.xsd

    def get_ad_extensions_mapping(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return {'vtam' : 'https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/server_schema.xsd'} # /ad.xsd

    def is_single_allocatioNetworkInterfaceConnectedTon(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return False
    
    def get_allocation_mode(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return 'geni_many'

    def list_resources(self, client_cert, credentials, geni_available):
	"""Documentation see [geniv3rpc] GENIv3DelegateBase."""
	#check if the certificate and credentials are correct for this method
	#self.auth(client_cert, credentials, None, ('listslices',))
	root_node = self.lxml_ad_root()
	E = self.lxml_ad_element_maker('vtam')
        servers = self._resource_manager.get_servers()
	r = E.network()
	for server in servers:
	    if int(server.available) is 0 and geni_available: continue
	    else:
	        n = E.node()
            	n.append(E.name(server.name))
	    	n.append(E.available("True" if int(server.available) is 1 else "False"))
  	    	n.append(E.operating_system_type(server.operatingSystemType))
	    	n.append(E.operating_system_distribution(server.operatingSystemDistribution))
	    	n.append(E.operating_system_version(server.operatingSystemVersion))
	    	n.append(E.virtualization_technology(server.virtTech))
	    	n.append(E.cpus_number("0" if not server.numberOfCPUs else server.numberOfCPUs))
	    	n.append(E.cpu_frequency("0" if not server.CPUFrequency else server.CPUFrequency))
	    	n.append(E.memory("0" if not server.memory else server.memory))
	    	n.append(E.hdd_space_GB("0" if not server.discSpaceGB else server.discSpaceGB))
	    	n.append(E.agent_url(server.agentURL))
	    
		if server.subscribedIp4Ranges: 
		    for ips in server.subscribedIp4Ranges:
		    	ip = E.service(type='Range')
		    	ip.append(E.type("IpRange"))
		    	ip.append(E.name("IpRange"))
		    	ip.append(E.start_value(ips.subscribed_ip4_range.startIp))
		    	ip.append(E.end_value(ips.subscribed_ip4_range.endIp))
		    	n.append(ip)

		if server.subscribedMacRanges:
		    for macs in server.subscribedMacRanges:
		    	mac = E.service(type="Range")
		    	mac.append(E.type("MacRange"))
		    	mac.append(E.name("MacRange"))
		    	mac.append(E.start_value(macs.subscribed_mac_range.startMac))
		    	mac.append(E.end_value(macs.subscribed_mac_range.endMac))
		    	n.append(mac)

    		if server.networkInterfaces:
		    for network_interface in server.networkInterfaces:
		    	interface = E.service(type="Network")
		        interface.append(E.type("Interface"))
		        interface.append(E.server_interface_name(network_interface.networkinterface.name))
	            	interface.append(E.isMgmt(str(network_interface.networkinterface.isMgmt)))
		        if network_interface.networkinterface.switchID:
		    	    interface.append(E.interface_switch_id(network_interface.networkinterface.switchID))
		        if network_interface.networkinterface.port:
		    	    interface.append(E.interface_port(str(network_interface.networkinterface.port))) 
		        n.append(interface)		

	        r.append(n)
	root_node.append(r)
	return self.lxml_to_string(root_node)
 
    def describe(self, urns, client_cert, credentials):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
	rspec, sliver_list = self.status(urns, client_cert, credentials)
        return rspec

    def allocate(self, slice_urn, client_cert, credentials, rspec, end_time=None):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
	requested_vms = list()
        rspec_root = self.lxml_parse_rspec(rspec)
        for nodes in rspec_root.getchildren():
#            if not self.lxml_elm_has_request_prefix(nodes, 'vtam'):
#                raise geni_ex.GENIv3BadArgsError("RSpec contains elements/namespaces I dont understand (%s)." % (nodes,))
#            if not self.lxml_elm_equals_request_tag(nodes, 'vtam', 'node'):
	    if not nodes.tag == "node":
                raise geni_ex.GENIv3BadArgsError("RSpec contains elements/namespaces I dont understand (%s)." % (nodes,))
	    
            for slivers in nodes.getchildren():
		vm = dict()
#		if not self.lxml_elm_equals_request_tag(slivers, 'vtam', 'sliver'):
		if not slivers.tag == "sliver":
		    raise geni_ex.GENIv3BadArgsError("RSpec contains elements/namespaces I dont understand (%s)." % (slivers,))
		for elm in slivers.getchildren():
#		    if (self.lxml_elm_equals_request_tag(elm, 'vtam', 'name')):
		    if (elm.tag == "name"):
			vm['name'] = elm.text.strip()
#		    elif (self.lxml_elm_equals_request_tag(elm, 'vtam', 'project-id')):
		    elif (elm.tag == "project-id"):
			vm['project_id'] = elm.text.strip()
#		    elif (self.lxml_elm_equals_request_tag(elm, 'vtam', 'server-name')):
		    elif (elm.tag == "server-name"):
			vm['server_name'] = elm.text.strip()
#		    elif (self.lxml_elm_equals_request_tag(elm, 'vtam', 'operating-system-type')):
		    elif (elm.tag == "operating-system-type"):
                        vm['operating_system_type'] = elm.text.strip()
#		    elif (self.lxml_elm_equals_request_tag(elm, 'vtam', 'operating-system-version')):
		    elif (elm.tag == "operating-system-version"):
                        vm['operating_system_version'] = elm.text.strip()
#		    elif (self.lxml_elm_equals_request_tag(elm, 'vtam', 'operating-system-distribution')):
		    elif (elm.tag == "operating-system-distribution"):
                        vm['operating_system_distribution'] = elm.text.strip()
#		    elif (self.lxml_elm_equals_request_tag(elm, 'vtam', 'virtualization-type')):
		    elif (elm.tag == "virtualization-type"):
                        vm['virtualization_type'] = elm.text.strip()
#                    elif (self.lxml_elm_equals_request_tag(elm, 'vtam', 'hd-setup-type')):
		    elif (elm.tag == "hd-setup-type"):
                        vm['hd_setup_type'] = elm.text.strip()
#                    elif (self.lxml_elm_equals_request_tag(elm, 'vtam', 'hd-size-mb')):
		    elif (elm.tag == "hd-size-mb"):
                        vm['hd_size_mb'] = elm.text.strip()
#                    elif (self.lxml_elm_equals_request_tag(elm, 'vtam', 'hd-origin-path')):
		    elif (elm.tag == "hd-origin-path"):
                        vm['hd_origin_path'] = elm.text.strip()
#		    elif (self.lxml_elm_equals_request_tag(elm, 'vtam', 'hypervisor')):
		    elif (elm.tag == "hypervisor"):
                        vm['hypervisor'] = elm.text.strip()
#                    elif (self.lxml_elm_equals_request_tag(elm, 'vtam', 'virtualization-setup-type')):
		    elif (elm.tag == "virtualization-setup-type"):
                        vm['virtualization_setup_type'] = elm.text.strip()
#                    elif (self.lxml_elm_equals_request_tag(elm, 'vtam', 'memory-mb')):
		    elif (elm.tag == "memory-mb"):
                        vm['memory_mb'] = elm.text.strip()
	    	    else:
                	raise geni_ex.GENIv3BadArgsError("RSpec contains an element I dont understand (%s)." % (elm,))
	        requested_vms.append(vm)
	try:
	    allocated_vms_nodes = self._resource_manager.reserve_vms(requested_vms, slice_urn, end_time)
	except vt_ex.VTAMVmNameAlreadyTaken as e:
	    raise geni_ex.GENIv3AlreadyExistsError("The desired VM name(s) is already taken (%s)." % (requested_vms[0]['name'],))
	except vt_ex.VTAMServerNotFound as e:
	    raise geni_ex.GENIv3SearchFailedError("The desired Server name(s) cloud no be found (%s)." % (requested_vms[0]['server_name'],))
	except vt_ex.VTAMMalformedUrn as e:
	    raise geni_ex.GENIv3OperationUnsupportedError('Only slice URNs are admited in this AM')
	except vt_ex.VTMaxVMDurationExceeded as e:
	    raise geni_ex.GENIv3BadArgsError("VM allocation can not be extended that long (%s)" % (requested_vm['name'],))
	#TODO: maybe it should return only the allocated VMs, not all the VMs
	#rspecs is a RSpec GeniV3 (manifest) of newly allocated slivers 
	rspecs = self._get_manifest_rspec(allocated_vms_nodes)
	slivers = list()
	for key in allocated_vms_nodes.keys():
	    for allocated_vm in allocated_vms_nodes[key]:
	  	slivers.append(self._get_sliver_status_hash(allocated_vm, True))
	return rspecs, slivers
		

    def renew(self, urns, client_cert, credentials, expiration_time, best_effort):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
	# this code is similar to the provision call
        # TODO honor best effort
	vms = list()
        for urn in urns:
            if (self.urn_type(urn) == 'slice'):
                #client_urn, client_uuid, client_email = self.auth(client_cert, credentials, urn, ('renewsliver',)) # authenticate for each given slice
                slice_vms = self._resource_manager.vms_in_slice(urn)
		if slice_vms:
                    for vm in slice_vms: # extend the vm expiration time, so we have a longer timeout.
                    	try:
                            self._resource_manager.extend_vm_expiration(vm['urn'], expiration_time)
                    	except vt_ex.VTMaxVMDurationExceeded as e:
                            raise geni_ex.GENIv3BadArgsError("VM can not be extended that long (%s)" % (str(e),))
              	    vms.extend(slice_vms)
	    elif (self.urn_type(urn) == 'sliver')
		try:
		    vm, state = self._resource_manager.verify_vm(urn)
		    if vm:
		    	self._resource_manager.extend_vm_expiration(urn, expiration_time)
			vms.extend(vm)
		except vt_ex.VTMaxVMDurationExceeded as e:
                        raise geni_ex.GENIv3BadArgsError("VM can not be extended that long (%s)" % (str(e),))
            else:
                raise geni_ex.GENIv3OperationUnsupportedError('Only slice and sliver URNs can be renewed in this aggregate')

        return [self._get_sliver_status_hash(vm, True, True, "") for vm in vms]


 
    def provision(self, urns, client_cert, credentials, best_effort, end_time, geni_users):
        """Documentation see [geniv3rpc] GENIv3DelegateBase.
        {geni_users} is not relevant here."""
	for urn in urns:
	    #first we check the type of the urn
	    name, urn_type = urn_to_hrn(urn)
	    if urn_type is "slice":
		self._resource_manager.create_allocated_vm_from_slice(urn)
	    elif urn_type is "sliver":
	 	provisioned_vm = self._resource_manager.create_allocated_vm(name)
	    else:
		 raise geni_ex.GENIv3BadArgsError("Urn has a type unable to create" % (urn,))		
	#TODO: Generate the manifest rspec and the slivers list	
        return rspecs, slivers

    def status(self, urns, client_cert, credentials):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
	return "Dummy delegate working! Status"

    def delete(self, urns, client_cert, credentials, best_effort):
	#first we check that the urns in the list are valid urns
	for urn in urns:
            if (self.urn_type(urn) != "slice") and (self.urn_type(urn) != "sliver"):
		raise geni_ex.GENIv3OperationUnsupportedError('Only slice URNs can be deleted in this aggregate') 
	#once we know the input is a list of urns
	vms = list()
        for urn in urns:
	    #if the urn is a slice urn, delete all the slivers associated to this slice
	    if (self.urn_type(urn) == "slice"):
		deleted_vms = self._resource_manager.delete_vms_in_slice(urn)
		vms.extend(deleted_vms)
	    #if the urn is a resource urn, delete the resource
	    elif (self.urn_type(urn) == 'sliver'):
		deleted_vm = self._resource_manager.delete_vm(urn)
		vms.extend(deleted_vm)
	slivers = list()
	for vm in vms:
	    error = None
	    if vm.has_key("error"):
	        error = vm["error"]
	    slivers.append(self._get_sliver_status_hash(vm, False, False, error))

	return slivers
    

    def shutdown(self, slice_urn, client_cert, credentials):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return "Dummy delegate working! Shutdown"


    # Some helper methods

    def _get_sliver_status_hash(self, sliver, include_allocation_status=False, include_operational_status=False, error_message=None):
        """Helper method to create the sliver_status return values of allocate and other calls."""
        result = {'geni_sliver_urn' : sliver['name'],
                  'geni_expires'    : sliver['expires'],
                  'geni_allocation_status' : self.ALLOCATION_STATE_UNALLOCATED}
        if (include_allocation_status):
            result['geni_allocation_status'] = self.ALLOCATION_STATE_ALLOCATED if sliver['status'] is "allocated" else self.ALLOCATION_STATE_PROVISIONED
        if (include_operational_status): 
            result['geni_operational_status'] = self.OPERATION_STATE_NOTREADY if sliver['status'] is "ongoing" else self.OPERATIONAL_STATE_READY
        if (error_message):
            result['geni_error'] = error_message
        return result


    def _get_manifest_rspec(self, nodes):
        E = self.lxml_manifest_element_maker('vtam')
        manifest = self.lxml_manifest_root()
	#XXX: Add more information about the AM? 
        for key in nodes.keys():
            # assemble manifest
            server = E.node(server = key)
	    #XXX: More information about the server? urn? id?
	    #server.append(component_id = node['server_urn'])
	    server.append(exclusive = "true")
	    for sliver in nodes[key]:
	    	vm = E.sliver(type = 'VM')
		vm.append(E.name(sliver['name']))
	        server.append(vm)
            manifest.append(server)
        return self.lxml_to_string(manifest)

