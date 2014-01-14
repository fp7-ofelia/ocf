import time 

import amsoil.core.pluginmanager as pm

import xml.etree.ElementTree as ET

from util.xrn import *

import amsoil.core.log

logging=amsoil.core.log.getLogger('VTDelegate')


'''@author: SergioVidiella'''


GENIv3DelegateBase = pm.getService('geniv3delegatebase')
geniv3_exception = pm.getService('geniv3exceptions')
virt_exception = pm.getService('virtexceptions')

class VTDelegate(GENIv3DelegateBase):
    """
        A Delegate for the VT AM 
    """

    URN_PREFIX = 'urn:publicid:IDN+geni:gpo:gcf'

    def __init__(self):
        super(VTDelegate, self).__init__()
        self._resource_manager = pm.getService("virtrm")
        self._admin_resource_manager = pm.getService("virtadminrm")

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
            if int(server.available) is 0 and geni_available: 
                continue
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
                        ip.append(E.name("IpRange"))
                        ip.append(E.start_value(ips.startIp))
                        ip.append(E.end_value(ips.endIp))
                        n.append(ip)
                if server.subscribedMacRanges:
                    for macs in server.subscribedMacRanges:
                        mac = E.service(type="Range")
                        mac.append(E.name("MacRange"))
                        mac.append(E.start_value(macs.startMac))
                        mac.append(E.end_value(macs.endMac))
                        n.append(mac)
                if server.networkInterfaces:
                    for network_interface in server.networkInterfaces:
                        interface = E.service(type="Network")
                        interface.append(E.type("Interface"))
                        interface.append(E.server_interface_name(network_interface.name))
                        interface.append(E.isMgmt(str(network_interface.isMgmt)))
                        if network_interface.switchID:
                            interface.append(E.interface_switch_id(network_interface.switchID))
                        if network_interface.port:
                            interface.append(E.interface_port(str(network_interface.port))) 
                        n.append(interface)                
                r.append(n)
        root_node.append(r)
        return self.lxml_to_string(root_node)
    
    def describe(self, urns, client_cert, credentials):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        rspec, sliver_list = self.status(urns, client_cert, credentials)
        return rspec
    
    # XXX: improve
    def __extract_node_from_rspec(self, rspec_node):
        node = dict()
        for elm in rspec_node.getchildren():
            node[elm.replace("vtam:","")] = elm.text.strip()
        return node
    
    def allocate(self, slice_urn, client_cert, credentials, rspec, end_time=None):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        slice_hrn, hrn_type = urn_to_hrn(slice_urn)
        slice_name = get_leaf(slice_hrn)
        requested_vms = list()
        rspec_root = self.lxml_parse_rspec(rspec)

        # XXX Start. Adapted from dhcpgeni3 --> test and remove
        vms = []
        # parse RSpec -> requested_ips
        rspec_root2 = self.lxml_parse_rspec(rspec)
        for elm in rspec_root2.getchildren():
            if not self.lxml_elm_has_request_prefix(elm, 'vtam'):
                raise geni_ex.GENIv3BadArgsError("RSpec contains elements/namespaces I do not understand (%s)." % (elm,))
            if (self.lxml_elm_equals_request_tag(elm, 'vtam', 'node')):
                vms.append(self.__extract_node_from_rspec(elm))
                # raise geni_ex.GENIv3GeneralError('IP ranges in RSpecs are not supported yet.') # TODO
            else:
                raise geni_ex.GENIv3BadArgsError("RSpec contains an element I do not understand (%s)." % (elm,))
        # XXX End

        for nodes in rspec_root.getchildren():
            if not nodes.tag == "node":
                raise geniv3_exception.GENIv3BadArgsError("RSpec contains elements/namespaces I do not understand (%s)." % (nodes,))        
            for slivers in nodes.getchildren():
                vm = dict()
                if not slivers.tag == "sliver":
                    raise geniv3_exception.GENIv3BadArgsError("RSpec contains elements/namespaces I do not understand (%s)." % (slivers,))
                for elm in slivers.getchildren():
                    if (elm.tag == "name"):
                        vm['name'] = elm.text.strip()
                    elif (elm.tag == "project-name"):
                        vm['project_name'] = elm.text.strip()
                    elif (elm.tag == "server-name"):
                        vm['server_name'] = elm.text.strip()
                    elif (elm.tag == "operating-system-type"):
                        vm['operating_system_type'] = elm.text.strip()
                    elif (elm.tag == "operating-system-version"):
                        vm['operating_system_version'] = elm.text.strip()
                    elif (elm.tag == "operating-system-distribution"):
                        vm['operating_system_distribution'] = elm.text.strip()
                    elif (elm.tag == "virtualization-type"):
                        vm['virtualization_type'] = elm.text.strip()
                    elif (elm.tag == "hd-setup-type"):
                        vm['hd_setup_type'] = elm.text.strip()
                    elif (elm.tag == "hd-size-mb"):
                        vm['hd_size_mb'] = elm.text.strip()
                    elif (elm.tag == "hd-origin-path"):
                        vm['hd_origin_path'] = elm.text.strip()
                    elif (elm.tag == "hypervisor"):
                        vm['hypervisor'] = elm.text.strip()
                    elif (elm.tag == "virtualization-setup-type"):
                        vm['virtualization_setup_type'] = elm.text.strip()
                    elif (elm.tag == "memory-mb"):
                        vm['memory_mb'] = elm.text.strip()
                    else:
                        raise geniv3_exception.GENIv3BadArgsError("RSpec contains an element I do not understand (%s)." % (elm,))
                requested_vms.append(vm)
        if self.urn_type(slice_urn) is 'slice': 
            try:
                allocated_vms = dict()
                for requested_vm in requested_vms:
                    allocated_vm, server = self._resource_manager.allocate_vm(requested_vm, slice_name, end_time)
                    if server.name not in allocated_vms:
                        allocated_vms[server.name] = list()
                    allocated_vms[server.name].append(allocated_vm)
            except virt_exception.VTAMVmNameAlreadyTaken as e:
                self.undo_action("allocate", allocated_vms)            
                raise geniv3_exception.GENIv3AlreadyExistsError("The desired VM name(s) is already taken (%s)." % (requested_vms[0]['name'],))
            except virt_exception.VTAMServerNotFound as e:
                self.undo_action("allocate", allocated_vms)
                raise geniv3_exception.GENIv3SearchFailedError("The desired Server name(s) cloud no be found (%s)." % (requested_vms[0]['server_name'],))
            except virt_exception.VTMaxVMDurationExceeded as e:
                self.undo_action("allocate", allocated_vms)
                raise geniv3_exception.GENIv3BadArgsError("VM allocation can not be extended that long (%s)" % (requested_vm['name'],))
        else:
            raise geniv3_exception.GENIv3OperationUnsupportedError('Only slice URNs are admited in this method for this AM')
        rspecs = self._get_manifest_rspec(allocated_vms, slice_urn)
        slivers = list()
        for key in allocated_vms.keys():
            for allocated_vm in allocated_vms[key]:
                vm_hrn = get_authority(get_authority(slice_urn)) + '.' + allocated_vm.projectName + '.' + allocated_vm.sliceName + '.' + allocated_vm.name
                vm_urn = hrn_to_urn(vm_hrn, 'sliver')
                slivers.append(self._get_sliver_status_hash({'name':vm_urn, 'expires':allocated_vm.expires, 'status':"allocated"}, True))
        return rspecs, slivers
              
    def renew(self, urns, client_cert, credentials, expiration_time, best_effort):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        # This code is similar to the provision call
        if best_effort is True:
           ex_flag = True
           for urn in urns:
                if self.urn_type(urn) is 'slice' or 'sliver':
                    ex_flag = False
           if ex_flag is True:
                raise geniv3_exception.GENIv3OperationUnsupportedError('Only slice and sliver URNs can be renewed in this aggregate')
        if self._resource_manager.check_expiration_time(expiration_time) is False:
            raise geniv3_exception.GENIv3BadArgsError("VMs can not be extended that long")
        vms = list()
        expirations = list()
        for urn in urns:
            if (self.urn_type(urn) == 'slice'):
                #client_urn, client_uuid, client_email = self.auth(client_cert, credentials, urn, ('renewsliver',)) # authenticate for each given slice
                slice_vms = self._resource_manager.vms_in_slice(urn)
                if slice_vms:
                    for vm in slice_vms: # extend the vm expiration time, so we have a longer timeout.
                        try:
                            ext_vm, last_expiration = self._resource_manager.set_vm_expiration(vm['name'], vm['status'], expiration_time)
                            expirations.append(last_expiration)
                            vms.extend(ext_vm)
                        except virt_exception.VTMaxVMDurationExceeded as e:
                            if best_effort is True:
                                vms.append({'name':urn, 'expires':e.time, 'error':"Expiration time is exceed"})
                            else: 
                                #If best_effort is False, undo all and throw an exception
                                for vm, expiration in vms, expirations:
                                    try:
                                        ext_vm = self._resource_manager.set_vm_expiration(vm['name'], vm['status'], expiration)
                                    except virt_exception.VTMaxVMDurationExceeded as e:
                                        pass
                        raise geniv3_exception.GENIv3BadArgsError("VM can not be extended that long (%s)" % (ext_vm['name'],))
                else:
                     if best_effort is False:
                        for vm, expiration in vms, expirations:
                            try:
                                ext_vm = self._resource_manager.set_vm_expiration(vm['name'], vm['status'], expiration)
                            except virt_exception.VTMaxVMDurationExceeded as e:
                                pass
                        raise geniv3_exception.GENIv3BadArgsError("The urn doesn't contain any resource (%s)" % (str(urn),))
            elif (self.urn_type(urn) == 'sliver'):
                try:
                    vm, state = self._resource_manager.verify_vm(urn)
                    ext_vm, last_expiration = self._resource_manager.set_vm_expiration(vm, state, expiration_time)
                    expirations.extend(last_expiration)
                    vms.extend(ext_vm)
                except virt_exception.VTAMVMNotFound as e:
                    if best_effort is True:
                        vms.append({'name':urn, 'expires':None, 'error':"No exist any resource with the given urn, it may have expired"})
                    else:
                        for vm, expiration in vms, expirations:
                            try:
                                ext_vm = self._resource_manager.set_vm_expiration(vm['name'], vm['status'], expiration)
                            except virt_exception.VTMaxVMDurationExceeded as e:
                                pass
                    raise geniv3_exception.GENIv3BadArgsError("The urn don't contain any resource (%s)" % (str(urn),))
                except virt_exception.VTAMMaxVMDurationExceeded as e:
                    if best_effort is True:
                        vms.append({'name':urn, 'expires':e.time, 'error':"Expiration time is exceed"})
                    else:
                        # If best_effort is False, undo all and throw an exception
                        for vm, expiration in vms, expirations:
                            try:
                                ext_vm = self._resource_manager.set_vm_expiration(vm['name'], vm['status'], expiration)
                            except virt_exception.VTMaxVMDurationExceeded as e:
                                pass
                    raise geniv3_exception.GENIv3BadArgsError("VM can not be extended that long (%s)" % (ext_vm['name'],))
            else:
                if best_effort is True:
                    vms.append({'name':urn, 'expires':e.time, 'error':"Malformed URN, it doesn't belong to a Slice either a Sliver, only this types of URN are accepted"})
                else:
                    # If best_effort is False, undo all and throw an exception
                    for vm, expiration in vms, expirations:
                        try:
                            ext_vm = self._resource_manager.set_vm_expiration(vm['name'], vm['status'], expiration)
                        except virt_exception.VTMaxVMDurationExceeded as e:
                            pass
                raise geniv3_exception.GENIv3OperationUnsupportedError('Only slice and sliver URNs can be renewed in this aggregate')
        slivers = list()
        for vm in vms:
            if vm.has_key('error'):
                slivers.append(self._get_sliver_status_hash(vm, True, True, vm['error']))
            else:
                sliver.append(self._get_sliver_status_hash(vm, True, True))
        return slivers
    
    def provision(self, urns, client_cert, credentials, best_effort, end_time, geni_users):
        """Documentation see [geniv3rpc] GENIv3DelegateBase.
        {geni_users} is not relevant here."""
        # TODO: honor best_effort
        for urn in urns:
            # First we check the type of the urn
            if (self.urn_type(urn) == "slice"):
                provisioned_vms = self._resource_manager.provision_allocated_vms(urn, end_time)        
            else:
                raise geniv3_exception.GENIv3BadArgsError("Urn has a type unable to create" % (urn,))        
        rspecs = self._get_manifest_rspec(provisioned_vms)
        slivers = list()
        for key in provisioned_vms.keys():
            for provisioned_vm in provisioned_vms[key]:
                if provisioned_vm.has_key('error'):
                    slivers.append(self._get_sliver_status_hash(provisioned_vm, False, False, provisioned_vm['error']))
                else:
                    slivers.append(self._get_sliver_status_hash(provisioned_vm, True, True))
        return rspecs, slivers
    
    def status(self, urns, client_cert, credentials):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        vms = list()
        for urn in urns:
            if (self.urn_type(urn) == 'slice'):
                #client_urn, client_uuid, client_email = self.auth(client_cert, credentials, urn, ('sliverstatus',)) # authenticate for each given slice
                slice_vms = self._resource_manager.vms_in_slice(urn)
                if not slice_vms:
                    raise geniv3_exception.GENIv3SearchFailedError("There are no resources in the given slice(s)")
                for vm in slice_vms:
                    vm_status = self._resource_manager.get_vm_status(vm['name'], vm['status'])
                    vms.append(vm_status)
            elif (self.urn_type(urn) == 'sliver'):
                try:
                    vm, status = self._resource_manager.verify_vm(urn)
                    vm_status = self._resource_manager.get_vm_status(vm, status)
                    vms.append(vm_status)        
                except virt_exception.VTAMVMNotFound as e:
                    raise geniv3_exception.GENIv3SearchFailedError("The desired VM urn(s) cloud not be found (%s)." % (vm,))
            else:
                raise geniv3_exception.GENIv3OperationUnsupportedError('Only slice or sliver URNs can be given to status in this aggregate')
        sliver_list = [self._get_sliver_status_hash(vm, True, True) for vm in vms]
        status_vms = dict()
        for vm in vms:
            if status_vms.has_key(vm['server']):
                status_vms[vm['server']].append(vm)
            else:    
                status_vms[vm['server']] = list()
                status_vms[vm['server']].append(vm)
        return self._get_manifest_rspec(status_vms), sliver_list
    
    def perform_operational_action(self, urns, client_cert, credentials, action, best_effort):
        # TODO: honor best_effort
        vms = list()
        for urn in urns:
            if (self.urn_type(urn) == 'slice'):
                #client_urn, client_uuid, client_email = self.auth(client_cert, credentials, urn, ('sliverstatus',)) # authenticate for each given slice
                slice_vms = self._resource_manager.vms_in_slice(urn)
                if not slice_vms:
                    raise geniv3_exception.GENIv3SearchFailedError("There are no resources in the given slice(s)")
                for vm in slice_vms:
                    if (action == self.OPERATIONAL_ACTION_START):
                        started_vm = self._resource_manager.start_vm(vm['name'])
                        vms.extend(started_vm)
                    elif (action == self.OPERATIONAL_ACTION_STOP):
                        stopped_vm = self._resource_manager.stop_vm(vm['name'])
                        vms.extend(stopped_vm)
                    elif (action == self.OPERATIONAL_ACTION_RESTART):
                        restarted_vm = self._resource_manager.restart_vm(vm['name'])        
                        vms.extend(restarted_vm)
                    else:
                        raise geniv3_exception.GENIv3BadArgsError("Action not suported in this AM" % (urn,))
            elif (self.urn_type(urn) == 'sliver'):     
                if (action == self.OPERATIONAL_ACTION_START):
                    vm = self._resource_manager.start_vm(urn)
                    vms.extend(vm)
                elif (action == self.OPERATIONAL_ACTION_STOP):
                    vm = self._resource_manager.stop_vm(urn)
                    vms.extend(vm)
                elif (action == self.OPERATIONAL_ACTION_RESTART):
                    vm = self._resource_manager.restart_vm(vm['name'])
                    vms.extend(vm)
                else:
                    raise geniv3_exception.GENIv3BadArgsError("Action not suported in this AM" % (urn,))
            else:
                raise geniv3_exception.GENIv3OperationUnsupportedError('Only slice or sliver URNs can be given in this aggregate')
        sliver_list = list()
        for vm in vms:
            if vm.has_key('error'):
                silver_list.append(self._get_sliver_status_hash(vm, True, True, vm['error']))
            else:
                sliver_list.append(self._get_sliver_status_hash(vm, True, True))
        return sliver_list
    
    def delete(self, urns, client_cert, credentials, best_effort):
        # TODO: honor best_effort
        # First we check that the urns in the list are valid urns
        for urn in urns:
            if (self.urn_type(urn) != "slice") and (self.urn_type(urn) != "sliver"):
                raise geniv3_exception.GENIv3OperationUnsupportedError('Only slice and sliver URNs can be deleted in this aggregate') 
        # Once we know the input is a list of urns
        vms = list()
        for urn in urns:
            # If the urn is a slice urn, delete all the slivers associated to this slice
            if (self.urn_type(urn) == "slice"):
                deleted_vms = self._resource_manager.delete_vms_in_slice(urn)
                vms.extend(deleted_vms)
            # If the urn is a resource urn, delete the resource
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
        if (self.urn_type(slice_urn) == 'slice'):
            #client_urn, client_uuid, client_email = self.auth(client_cert, credentials, urn, ('sliverstatus',)) # authenticate for each given slice
            results = self._resource_manager.stop_vms_in_slice(slice_urn)
            sliver_list = list()
            for result in results:
                if result.has_key('error'):
                    silver_list.append(self._get_sliver_status_hash(result, True, True, result['error']))
                else:
                    sliver_list.append(self._get_sliver_status_hash(result, True, True))
            return sliver_list
        else:
            raise geniv3_exception.GENIv3OperationUnsupportedError('Only slice URNs can be given to shutdown in this aggregate')

    ''' Helper methods '''
    def _get_sliver_status_hash(self, sliver, include_allocation_status=False, include_operational_status=False, error_message=None):
        """Helper method to create the sliver_status return values of allocate and other calls."""
        result = {'geni_sliver_urn' : sliver['name'],
                  'geni_expires'    : sliver['expires'],
                  'geni_allocation_status' : self.ALLOCATION_STATE_UNALLOCATED}
        if (include_allocation_status):
            result['geni_allocation_status'] = self.ALLOCATION_STATE_ALLOCATED if sliver['status'] is "allocated" else self.ALLOCATION_STATE_PROVISIONED
        if (include_operational_status): 
            result['geni_operational_status'] = self.OPERATIONAL_STATE_NOTREADY if sliver['status'] is "ongoing" or "allocated" else self.OPERATIONAL_STATE_FAILED if error_message else self.OPERATIONAL_STATE_READY
        if (error_message):
            result['error'] = error_message
        return result
    
    def _get_manifest_rspec(self, nodes, slice_urn):
        E = self.lxml_manifest_element_maker('vtam')
        manifest = self.lxml_manifest_root()
        # XXX: Add more information about the AM? 
        for key in nodes.keys():
            # Assemble manifest
            server = E.node(server = key)
            # XXX: More information about the server? urn? id?
            #server.append(component_id = node['server_urn'])
            for sliver in nodes[key]:
                vm = E.sliver(type = 'VM')
                vm.append(E.name(hrn_to_urn(get_authority(get_authority(slice_urn)) + '.' + sliver.projectName + '.' + sliver.sliceName + '.' + sliver.name, 'sliver')))
                server.append(vm)
            manifest.append(server)
        return self.lxml_to_string(manifest)
    
    def undo_action(self, action, params):
        if action is "allocate":
            for param in params:
                self._resource_manager.delete_vm(param, "allocated")
        elif action is "create":
            for param in params:
                self._resource_manager.delete_vm(param, "provisioned")            
