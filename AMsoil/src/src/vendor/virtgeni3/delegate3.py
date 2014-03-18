import time 
import amsoil.core.pluginmanager as pm
import xml.etree.ElementTree as ET
import lxml
from geni3util.filterednodes import RSPECS_FILTERED_NODES
from geni3util.xrn import *

import amsoil.core.log

logging=amsoil.core.log.getLogger('VTDelegate3')


'''@author: SergioVidiella, CarolinaFernandez'''


GENIv3DelegateBase = pm.getService('geniv3delegatebase')
geniv3_exception = pm.getService('geniv3exceptions')
virt_exception = pm.getService('virtexceptions')

class VTDelegate3(GENIv3DelegateBase):
    """
        A Delegate for the VT AM 
    """

    URN_PREFIX = 'urn:publicid:IDN+geni:gpo:gcf'
#    ACCEPTED_TAGS_REQUEST = ["name", "project-name", "server-name", "operating-system-type", "operating-system-version", "operating-system-distribution", "virtualization-type", "hd-setup-type", "hd-size-mb", "hd-origin-path", "hypervisor", "virtualization-setup-type", "memory-mb"]

    def __init__(self):
        super(VTDelegate3, self).__init__()
        self._resource_manager = pm.getService("virtrm")
        self._admin_resource_manager = pm.getService("virtadminrm")
        self._translator = pm.getService("virtutils").Translator
        self._filter = pm.getService("virtutils").Filter

    def get_request_extensions_mapping(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return {'virtrm' : 'https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/geni3/virtualisation/request.xsd'} # /request.xsd

    def get_manifest_extensions_mapping(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return {'virtrm' : 'https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/geni3/virtualisation/manifest.xsd'} # /manifest.xsd

    def get_ad_extensions_mapping(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return {'virtrm' : 'https://github.com/fp7-ofelia/ocf/blob/ocf.rspecs/geni3/virtualisation/advertisement.xsd'} # /ad.xsd

    def is_single_allocatioNetworkInterfaceConnectedTon(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return False
    
    def get_allocation_mode(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return 'geni_many'

    def list_resources(self, client_cert, credentials, geni_available):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        #XXX: Check if the certificate and credentials are correct for this method
        #self.auth(client_cert, credentials, None, ('listslices',))
        namespace = self.get_ad_extensions_mapping()
        # Generate the XML
        root_node = self.lxml_ad_root()
        node_generator = self.lxml_ad_element_maker(namespace.keys()[0])
        # Obtain the servers
        servers = self._resource_manager.get_servers()
        logging.debug("SERVER (DICTIONARY): %s" % str(servers))
        # Craft the XML
        r = node_generator.network()
#        from lxml import objectify
#        r = objectify.Element("{%s}sliver" % namespace)
#        parser = lxml.etree.XMLParser(recover=True)
        for server in servers:
            # XXX SOLVE VISUALIZATION ISSUES WITH NAMESPACES IN XML PASSED TO LXML
#            sliver_node = "<%s:sliver>%s<%s:/sliver>" % (namespace, self._translator.json2xml(server, "", namespace), namespace)
            # Translator JSON -> XML. Arguments: (dictionary, [initial XML], [namespace])
#            filtered_nodes = ["id", "vtserver_ptr_id", "agent_url", "agent_password", "enabled", "url", "vms"]
#            for filtered_node in filtered_nodes:
#                if filtered_node in server.keys():
#                    server.pop(filtered_node)
            sliver = node_generator.server()
            # Rearrange the dictionary according to the ad RSpec hierachy
            server["networking"] = dict()
            server["networking"]["network_interfaces"] = server.pop("network_interfaces")
            server["networking"]["subscribed_ip4_ranges"] = server.pop("subscribed_ip4_ranges")
            server["networking"]["subscribed_mac_ranges"] = server.pop("subscribed_mac_ranges")
            # Translate the dictionary into a XML
            logging.debug("*** Translator.list_resources => sliver: %s" % str(sliver))
            self._translator.dict2xml_tree(server, sliver, node_generator)
#            logging.debug("*** Translator.list_resources => sliver_node: %s" % sliver_node)
#            sliver_node = "<sliver>%s</sliver>" % self._translator.json2xml(server, "", namespace)
#            s = lxml.etree.fromstring(sliver_node, parser)
#            logging.debug("**** Translator.list_resources => sliver_contents to XML: %s" % str(s))
#            s = E.sliver()
            # Filter private tags/nodes from XML using a list defined by us
            advertisment_filtered_nodes = RSPECS_FILTERED_NODES['advertisement']
            for key, value in advertisment_filtered_nodes.iteritems():
                self._filter.filter_xml_by_dict(value, sliver, key, namespace)
#            nspace = self.get_ad_extensions_mapping()
#            for filtered_node in server_filtered_nodes:
#                for node in sliver.xpath("//%s%s%s" % (namespace, ":" if namespace else "", filtered_node), namespaces=nspace):
#                    logging.debug("*** Translator.list_resources => Node %s parent: %s" % (filtered_node, str(node.getparent().tag)))
#                    if node.getparent().tag == "%s%s%ssliver" %("{" if namespace else "", nspace[namespace], "}" if namespace else ""):
#                        node.getparent().remove(node)
#            logging.debug("*** Translator.list_resources => final XML: %s" % str(lxml.etree.tostring(s, pretty_print=True)))
            # If geni_available = True, show all servers. Otherwise, show only available servers
            if not geni_available:
                r.append(sliver)
            elif geni_available and server["available"] is "1":
                r.append(sliver)
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
        logging.debug("slice_urn: %s" % str(slice_urn))
        if self.urn_type(slice_urn) != 'slice':
            raise geniv3_exception.GENIv3OperationUnsupportedError('Only slice URNs are admited in this method for this AM')
        slice_hrn, hrn_type = urn_to_hrn(slice_urn)
        slice_name = get_leaf(slice_hrn)
        logging.debug("slice_name: %s" % str(slice_name))
        authority = get_authority(get_authority(slice_urn))
        logging.debug("authority: %s" % str(authority))
        namespace = self.get_ad_extensions_mapping().keys()[0]
        dictionary = self._translator.xml2json(rspec, {namespace:None})
        logging.debug("***** Translator.xml2json => First level Json.keys : %s" % str(dictionary.keys()))
        logging.debug("***** Translator.xml2json => Second level Json.keys : %s" % str(dictionary['rspec'].keys()))
        # Retrieve VMs from allocation request
        requested_vms = list()
#        slivers = dictionary["rspec"]["node"]
        slivers = dictionary["rspec"]["node"]["sliver"]
#        for vm in slivers.values():
        # If more than one VM is requested it will be a list of dictionaries.
        if type(slivers) is list:
            for vm in slivers:
                logging.debug("****** Allocate => dictionary : %s" % str(dictionary))
                logging.debug("****** Allocate => slivers.keys : %s" % str(slivers.keys()))
                vm["slice_name"] = slice_name
                vm["project_name"] = authority
                requested_vms.append(vm)
        # If the request only contains one VM, it will be a dictionary with the VM info.
        else:
            slivers["slice_name"] = slice_name
            slivers["project_name"] = authority
            requested_vms.append(slivers)
        try:
            allocated_vms = list()
            for requested_vm in requested_vms:
                # TODO CHECK VM DATA PROCESSING WITHIN RESOURCE MANAGER
                allocated_vm = self._resource_manager.allocate_vm(requested_vm, end_time)
                allocated_vms.append(allocated_vm)
        # If any VM fails in allocating, we unallocate all the previously allocated VMs
        except virt_exception.VTAMVmNameAlreadyTaken as e:
            self.undo_action("allocate", allocated_vms)            
            raise geniv3_exception.GENIv3AlreadyExistsError("The desired VM name(s) is already taken (%s)." % (requested_vms[0]['name'],))
        except virt_exception.VTAMServerNotFound as e:
            self.undo_action("allocate", allocated_vms)
            raise geniv3_exception.GENIv3SearchFailedError("The desired Server UUID(s) could no be found (%s)." % (requested_vms[0]['server_uuid'],))
        except virt_exception.VTMaxVMDurationExceeded as e:
            self.undo_action("allocate", allocated_vms)
            raise geniv3_exception.GENIv3BadArgsError("VM allocation can not be extended that long (%s)" % (requested_vm['name'],))
        # Generate the Manifest RSpec
        rspecs = self._get_manifest_rspec(allocated_vms)
        # Generate the JSON with the VMs information
        slivers = list()
        for allocated_vm in allocated_vms:
            # Add the status information here, due allocated vms does not have one
            allocated_vm["status"] = "allocated"    
            sliver = self._get_sliver_status_hash(allocated_vm, True)
            slivers.append(sliver)
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
                slice_vms = self._resource_manager.get_vms_in_slice(urn)
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
                slice_vms = self._resource_manager.get_vms_in_slice(urn)
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
                slice_vms = self._resource_manager.get_vms_in_slice(urn)
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
        result = {'geni_sliver_urn' : sliver['urn'],
                  'geni_expires'    : sliver['expiration_time'],
                  'geni_allocation_status' : self.ALLOCATION_STATE_UNALLOCATED}
        if (include_allocation_status):
            result['geni_allocation_status'] = self.ALLOCATION_STATE_ALLOCATED if sliver['status'] is "allocated" else self.ALLOCATION_STATE_PROVISIONED
        if (include_operational_status): 
            result['geni_operational_status'] = self.OPERATIONAL_STATE_NOTREADY if sliver['status'] is "ongoing" or "allocated" else self.OPERATIONAL_STATE_FAILED if error_message else self.OPERATIONAL_STATE_READY
        if (error_message):
            result['geni_error'] = error_message
        return result
    
    def _get_manifest_rspec(self, slivers):
        namespace = self.get_manifest_extensions_mapping()
        # Generate the RSpec root node
        root_node = self.lxml_manifest_root()
        # Generate the node generator with the specific namespace
        node_generator = self.lxml_manifest_element_maker(namespace.keys()[0])
        node = node_generator.node()
        # Generate a node for every sliver
        for sliver in slivers:
            vm = node_generator.sliver()
            self._translator.dict2xml_tree(sliver, vm, node_generator)
            # Filter the generated node according the Manifest schema
            manifest_filtered_nodes = RSPECS_FILTERED_NODES['manifest']
            for key, value in manifest_filtered_nodes.iteritems():
                self._filter.filter_xml_by_dict(value, vm, key, namespace)
            node.append(vm)
        root_node.append(node)
        logging.debug("****** MANIFEST RSPEC *****" + "\n\n" + self.lxml_to_string(root_node)) 
        return self.lxml_to_string(root_node)
    
    def undo_action(self, action, params):
        if action is "allocate":
            for param in params:
                self._resource_manager.delete_vm(param, "allocated")
        elif action is "create":
            for param in params:
                self._resource_manager.delete_vm(param, "provisioned")            
