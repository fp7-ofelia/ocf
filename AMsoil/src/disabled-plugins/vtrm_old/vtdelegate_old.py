import time, 

import amsoil.core.pluginmanager as pm

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

    def is_single_allocation(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return False

    def get_allocation_mode(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return 'geni_many'

    #TODO: implement all the methods for VT AM
    def list_resources(self, client_cert, credentials, geni_available):
	"""Documentation see [geniv3rpc] GENIv3DelegateBase."""
	#check if the certificate and credentials are correct for this method
	#self.auth(client_cert, credentials, None, ('listslices',))

	root_node = self.lxml_ad_root()
	E = self.lxml_ad_element_maker('vtam')
	nodes = self._resource_manager.GetNodes()
	r = E.network()
	for node in nodes:
	    if int(node.available) is 0 and geni_available: continue
	    else:
	        n = E.node()
            	n.append(E.name(node.name))
	    	n.append(E.available("True" if int(node.available) is 1 else "False"))
  	    	n.append(E.operating_system_type(node.operatingSystemType))
	    	n.append(E.operating_system_distribution(node.operatingSystemDistribution))
	    	n.append(E.operating_system_version(node.operatingSystemVersion))
	    	n.append(E.virtualization_technology(node.virtTech))
	    	n.append(E.cpus_number("0" if not node.numberOfCPUs else node.numberOfCPUs))
	    	n.append(E.cpu_frequency("0" if not node.CPUFrequency else node.CPUFrequency))
	    	n.append(E.memory("0" if not node.memory else node.memory))
	    	n.append(E.hdd_space_GB("0" if not node.discSpaceGB else node.discSpaceGB))
	    	n.append(E.discSpaceGB(node.agentURL))
	    
	    	ip_range = self._resource_manager.GetIpRange(int(node.id))	    
	    	if ip_range:
		    for ips in ip_range:
		    	ip = E.service(type='Range')
		    	ip.append(E.type("IpRange"))
		    	ip.append(E.name("IpRange"))
		    	ip.append(E.start_value(ips['startIp']))
		    	ip.append(E.end_value(ips['endIp']))
		    	n.append(ip)

		mac_range = self._resource_manager.GetMacRange(int(node.id))
	        if mac_range:
		    for macs in mac_range:
		    	mac = E.service(type="Range")
		    	mac.append(E.type("MacRange"))
		    	mac.append(E.name("MacRange"))
		    	mac.append(E.start_value(macs['startMac']))
		    	mac.append(E.end_value(macs['endMac']))
		    	n.append(mac)

		network_interfaces = self._resource_manager.GetNetworkInterfaces(int(node.id))
	    	if network_interfaces:
		    for network_interface in network_interfaces:
		    	for interfaces in network_interface:
		            interface = E.service(type="Network")
		            interface.append(E.type("Interface"))
		            interface.append(E.server_interface_name(interfaces['name']))
		            interface.append(E.isMgmt(str(interfaces['isMgmt'])))
		            if interfaces['switchID']:
		    	    	interface.append(E.interface_switch_id(interfaces['switchID']))
		            if interfaces['port']:
		    	    	interface.append(E.interface_port(str(interfaces['port']))) 
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
	    server = nodes.attrib['component_manager_id'].strip()
            if not self.lxml_elm_has_request_prefix(nodes, 'vtam'):
                raise geni_ex.GENIv3BadArgsError("RSpec contains elements/namespaces I dont understand (%s)." % (nodes,))
            if not self.lxml_elm_equals_request_tag(nodes, 'vtam', 'node'):
                raise geni_ex.GENIv3BadArgsError("RSpec contains elements/namespaces I dont understand (%s)." % (nodes,))
	    
            for slivers in nodes.getchildren():
		vm = dict()
		if not self.lxml_elm_equals_request_tag(slivers, 'vtam', 'sliver'):
		    raise geni_ex.GENIv3BadArgsError("RSpec contains elements/namespaces I dont understand (%s)." % (slivers,))
		vm['server'] = server
		for elm in slivers.getchildren():
		    if (self.lml_elm_equals_request_tag(elm, 'vtam', 'name')):
			vm['name'] = elm.text.strip()
		    elif (self.lml_elm_equals_request_tag(elm, 'vtam', 'uuid')):
			vm['uuid'] = elm.text.strip()
		    elif (self.lml_elm_equals_request_tag(elm, 'vtam', 'project-id')):
			vm['project_id'] = elm.text.strip()
		    elif (self.lml_elm_equals_request_tag(elm, 'vtam', 'slice-id')):
			vm['slice_id'] = elm.text.strip()
		    elif (self.lml_elm_equals_request_tag(elm, 'vtam', 'slice-name')):
			vm['slice_name'] = elm.text.strip()
		    elif (self.lml_elm_equals_request_tag(elm, 'vtam', 'server-name')):
			vm['server_name'] = elm.text.strip()
		    elif (self.lml_elm_equals_request_tag(elm, 'vtam', 'operating-system-type')):
                        vm['operating_system_type'] = elm.text.strip()
		    elif (self.lml_elm_equals_request_tag(elm, 'vtam', 'operating-system-version')):
                        vm['operating_system_version'] = elm.text.strip()
		    elif (self.lml_elm_equals_request_tag(elm, 'vtam', 'operating-system-distribution')):
                        vm['operating_system_distribution'] = elm.text.strip()
		    elif (self.lml_elm_equals_request_tag(elm, 'vtam', 'virtualization-type')):
                        vm['virtualization_type'] = elm.text.strip()
                    elif (self.lml_elm_equals_request_tag(elm, 'vtam', 'hd-setup-type')):
                        vm['hd_setup_type'] = elm.text.strip()
                    elif (self.lml_elm_equals_request_tag(elm, 'vtam', 'hd-size-mb')):
                        vm['hd_size_mb'] = elm.text.strip()
                    elif (self.lml_elm_equals_request_tag(elm, 'vtam', 'hd-origin-path')):
                        vm['hd_origin_path'] = elm.text.strip()
		    elif (self.lml_elm_equals_request_tag(elm, 'vtam', 'configurator')):
                        vm['configurator'] = elm.text.strip()
                    elif (self.lml_elm_equals_request_tag(elm, 'vtam', 'virtualization-setup-type')):
                        vm['virtualization_setup_type'] = elm.text.strip()
                    elif (self.lml_elm_equals_request_tag(elm, 'vtam', 'memory-mb')):
                        vm['memory_mb'] = elm.text.strip()
#XXX: Deprecated, interfaces are assigned automatically
#                    elif (self.lml_elm_equals_request_tag(elm, 'vtam', 'interfaces')):
#			vm_interfaces = list()
#			for interface in elm.getchildren():
#			    if not self.lml_elm_equals_request_tag(interface, 'vtam', 'interface'):
#				raise geni_ex.GENIv3BadArgsError("RSpec contains elements/namespaces I dont understand (%s)." % (interface,))
#			    vm_interface = dict()
#			    vm_interface['isMgmt'] = interface.attrib['ismgmt']
#			    for interface_elm in interface.getchildren():
#				if (self.lml_elm_equals_request_tag(interface_elm, 'vtam', 'name')):
#				    vm_interface['name'] = interface_elm.text.strip()
#				elif (self.lml_elm_equals_request_tag(interface_elm, 'vtam', 'mac')):
#				    vm_interface['mac'] = interface_elm.text.strip()
#				elif (self.lml_elm_equals_request_tag(interface_elm, 'vtam', 'ip')):
#				    vm_interface['ip'] = interface_elm.text.strip()
#				elif (self.lml_elm_equals_request_tag(interface_elm, 'vtam', 'mask')):
#				    vm_interface['mask'] = interface_elm.text.strip()
#				elif (self.lml_elm_equals_request_tag(interface_elm, 'vtam', 'gw')):
#				    vm_interface['gw'] = interface_elm.text.strip()
#				elif (self.lml_elm_equals_request_tag(interface_elm, 'vtam', 'dns1')):
#                                    vm_interface['dns1'] = interface_elm.text.strip()
#				elif (self.lml_elm_equals_request_tag(interface_elm, 'vtam', 'dns2')):
#                                    vm_interface['dns2'] = interface_elm.text.strip()
#				elif (self.lml_elm_equals_request_tag(interface_elm, 'vtam', 'switch-id')):
#                                    vm_interface['switch_id'] = interface_elm.text.strip()
#				elif (self.lml_elm_equals_request_tag(interface_elm, 'vtam', 'switch-port')):
#                                    vm_interface['switch_port'] = interface_elm.text.strip()
#				else:
#                        	    raise geni_ex.GENIv3BadArgsError("RSpec contains an element I dont understand (%s)." % (interface_elm,))
#			    vm_interfaces.append(vm_interface)
#			vm['interfaces'] = vm_interfaces
#XXX: Deprecated
#		    elif (self.lml_elm_equals_request_tag(elm, 'vtam', 'users')):
#			vm_users = list()
#                        for users in elm.getchildren():
#                            if not self.lml_elm_equals_request_tag(interface, 'vtam', 'user'):
#                                raise geni_ex.GENIv3BadArgsError("RSpec contains elements/namespaces I dont understand (%s)." % (users,))
#			     vm_user = dict()
#                            for user_elm in users.getchildren():
#                                if (self.lml_elm_equals_request_tag(user_elm, 'vtam', 'name')):
#                                    vm_user['name'] = user_elm.text.strip()
#	 			 elif (self.lml_elm_equals_request_tag(user_elm, 'vtam', 'password')):
#                                    vm_user['password'] = user_elm.text.strip()
#                                else:
#                                    raise geni_ex.GENIv3BadArgsError("RSpec contains an element I dont understand (%s)." % (user_elm,))
#                            vm_users.append(vm_user)
#                        vm['users'] = vm_users
	    	    else:
                	raise geni_ex.GENIv3BadArgsError("RSpec contains an element I dont understand (%s)." % (elm,))
	        requested_vms.append(vm)
	try:
	    allocated_vms_nodes = self._resource_manager.reserve_vms(requested_vms, slice_urn, end_time)
#XXX: Deprecated, interfaces are assigned automatically
#	except vt_ex.VTAMInterfaceNotFound as e:
#	    raise geni_ex.GENIv3SearchFailedError("The desired Interface(s) could no be found (%s)." % (requested_vm['interfaces'][0]['name'],))
#	except vt_ex.VTAMIpNotFound as e:
#	    raise geni_ex.GENIv3SearchFailedError("The desired IP(s) could no be found (%s)." % (requested_vm['interfaces'][0]['ip'],))
#        except vt_ex.VTAMMacNotFound as e:
#            raise geni_ex.GENIv3SearchFailedError("The desired Mac(s) could no be found (%s)." % (requested_vm['interfaces'][0]['mac'],))
#        except vt_ex.VTAMIpAlreadyTaken as e:
#            raise geni_ex.GENIv3AlreadyExistsError("The desired IP(s) is already taken (%s)." % (requested_vm['interfaces'][0]['ip'],))
#        except vt_ex.VTAMMacAlreadyTaken as e:
#            raise geni_ex.GENIv3AlreadyExistsError("The desired Mac(s) is already taken (%s)." % (requested_vm['interfaces'][0]['mac'],))
	except vt_ex.VTAMVmNameAlreadyTaken as e:
	    raise geni_ex.GENIv3AlreadyExistsError("The desired VM name(s) is already taken (%s)." % (requested_vm['name'],))
	except vt_ex.VTAMServerNotFound as e:
	    raise geni_ex.GENIv3SearchFailedError("The desired Server name(s) cloud no be found (%s)." % (requested_vm['server_name'],))
	#TODO: maybe it should return only the allocated VMs, not all the VMs
	#rspecs is a RSpec GeniV3 (manifest) of newly allocated slivers 
	rspecs = self._get_manifest_rspec(allocated_vms_nodes)
	slivers = list()
	for allocated_vms_node in allocated_vms_nodes:
	    for allocated_vms in allocated_vms_node:
		for allocated_vm in allocated_vms:
	    	    slivers.append(self._get_sliver_status_hash(allocated_vm, True))
	return rspecs, slivers
		

    def renew(self, urns, client_cert, credentials, expiration_time, best_effort):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
	return "Dummy delegate working! Renew"   
 
    def provision(self, urns, client_cert, credentials, best_effort, end_time, geni_users):
        """Documentation see [geniv3rpc] GENIv3DelegateBase.
        {geni_users} is not relevant here."""
        return "Dummy delegate working! Provision"

    def status(self, urns, client_cert, credentials):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
	return "Dummy delegate working! Status"

    def delete(self, urns, client_cert, credentials, best_effort):
	
        for urn in urns:
	    #if the urn is an slice urn, delete all the slivers associated to this slice
	    if(urn_type(urn) == 'slice'):
		deleted_slivers = self._resource_manager.delete_slice(urn)
	    elif(urn_type(urn) == 'sliver'):
		self._resource_manager.delete_vm(urn)
	    else:
		raise geni_ex.GENIv3BadArgsError("Urn has a type unable to delete" % (urn,))
	#TODO: Define the list() of slivers
	#[{'geni_sliver_urn'         : String,
        #     'geni_allocation_status'  : one of the ALLOCATION_STATE_xxx,
        #     'geni_expires'            : Python-Date,
        #     'geni_error'              : optional String}, 
        #    ...]
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
        for node in nodes:
            # assemble manifest
            server = E.node(component_manager_id = node['am_urn'])
	    server.append(component_id = node['server_urn'])
	    server.append(exclusive = "false")
	    server.append(component_name = node['server_urn'])
	    server.append(E.hostname(hrn_to_urn(node['hostname'], 'sliver')))    
	
	    for sliver in node['vms']:
	    	vm = E.sliver(type = 'VM')
		vm.append(E.name(sliver['name']))
		vm.append(E.ip(sliver['ip']))
		vm.append(E.mac(sliver['mac']))
		vm.append(E.status(sliver['status']))
	        server.append(vm)
            # TODO add more info here
            manifest.append(server)
        return manifest

