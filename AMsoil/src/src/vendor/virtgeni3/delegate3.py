import time 
import amsoil.core.pluginmanager as pm
import xml.etree.ElementTree as ET
import lxml
from geni3util.exceptiontranslator import ExceptionTranslator
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
        try:
            servers = self._resource_manager.get_servers()
        except Exception as e:
            raise ExceptionTranslator.virtexception2GENIv3exception(type(e), default=None)
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
                try:
                    # Create the VM URN and assign it to the VM
                    vm_hrn = requested_vm["project_name"] + '.' \
                             + requested_vm["slice_name"] + '.' \
                             + requested_vm["name"] 
                    vm_urn = hrn_to_urn(vm_hrn, "sliver")
                    requested_vm["urn"] = vm_urn
                    # TODO CHECK VM DATA PROCESSING WITHIN RESOURCE MANAGE, slice_urnR
                    allocated_vm = self._resource_manager.allocate_vm(requested_vm, end_time, slice_urn, "GENIv3")
                    allocated_vms.append(allocated_vm)
                # Translate the specific RM Exceptions into GENIv3 Exceptions
                except Exception as e:
                    logging.debug("********************* EXCEPTION => %s / TYPE => %s" % (str(e), str(type(e))))
                    raise ExceptionTranslator.virtexception2GENIv3exception(type(e), name=requested_vm['name'], server=requested_vm['server_uuid'], urn=requested_vm['urn'], default=requested_vm['urn'])
        # If any VM fails in allocating, we unallocate all the previously allocated VMs
        except Exception as e:
            self._undo_action(allocated_vms, "allocate")
            raise e
        # Generate the Manifest RSpec
        rspecs = self._get_manifest_rspec(allocated_vms)
        # Generate the JSON with the VMs information
        slivers = list()
        for allocated_vm in allocated_vms:
            # Add the status information here, due allocated vms does not have one
            sliver = self._get_sliver_status_hash(allocated_vm, True)
            slivers.append(sliver)
        return rspecs, slivers

    def renew(self, urns, client_cert, credentials, expiration_time, best_effort):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        # This code is similar to the provision call
        vms = list()
        renewed_vms = list()
        for urn in urns:
            try:
                logging.debug("***************** URN => %s" % (str(urn)))
                logging.debug("***************** URN TYPE => %s" % (str(self.urn_type(urn))))
                # First we check the type of the urn
                if (self.urn_type(urn) == "slice"):
                    # If the URN is from a slice, get all the allocated
                    try:
                        vms_in_container = self._resource_manager.get_allocated_vms_in_container(urn, "GENIv3")
                    # Throw the Exception for every kind of error
                    except Exception as e:
                        raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=urn, default=urn)
                    vms.extend(vms_in_container)
                elif (self.urn_type(urn) == "sliver"):
                    # If the UNR is from a VM, get it
                    try:
                        vm = get_vm_allocated_by_urn(urn)
                    except Exception as e:
                        raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=urn, default=urn)
                    vms.append(vm)
                else:
                    raise geniv3_exception.GENIv3BadArgsError("Urn has a type unable to create" % (urn,))
            # If {best_effort = False} throw the given Exception
            # If {best_effort = True} keep going 
            except Exception as e:
                if best_effort:
                    raise e
                else:
                    renewed_vms.append(self._generate_error_entry(urn, str(e)))
            # If any resource is obtained, raise an error
            if not vms:
                raise geniv3_exception.GENIv3SearchFailedError("There are no resources to provision. Perhaps they expired or the URN(s) is malformed.")
            # TODO: Add extend_expiration method to RM
#            for vm in vms:
#                try:
#                    renewed_vm = self._resource_manager.

    def provision(self, urns, client_cert, credentials, best_effort, end_time, geni_users):
        """Documentation see [geniv3rpc] GENIv3DelegateBase.
        {geni_users} is not relevant here."""
        # TODO: honor best_effort
        allocated_vms = list()
        provisioned_vms = list()
        logging.debug("************* URNs => %s" % (str(urns)))
        for urn in urns:
            try:
                logging.debug("***************** URN => %s" % (str(urn)))
                logging.debug("***************** URN TYPE => %s" % (str(self.urn_type(urn))))
                # First we check the type of the urn
                if (self.urn_type(urn) == "slice"):
                    # If the URN is from a slice, get all the allocated
                    try:
                        vms = self._resource_manager.get_allocated_vms_in_container(urn, "GENIv3")      
                    # Throw the Exception for every kind of error
                    except Exception as e:
                        raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=urn, default=urn)
                    allocated_vms.extend(vms)
                elif (self.urn_type(urn) == "sliver"):
                    # If the UNR is from a VM, get it
                    try: 
                        vm = get_vm_allocated_by_urn(urn)
                    except Exception as e:
                        raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=urn, default=urn)
                    allocated_vms.append(vm)
                else:
                    raise geniv3_exception.GENIv3BadArgsError("Urn has a type unable to create" % (urn,))
            # If {best_effort = False} throw the given Exception
            # If {best_effort = True} keep going 
            except Exception as e:
                if best_effort:
                    raise e
                else:
                    provisioned_vms.append(self._generate_error_entry(urn, str(e)))
        # If any resource is obtained, raise an error
        if not provisioned_vms:
            raise geniv3_exception.GENIv3SearchFailedError("There are no resources to provision. Perhaps they expired or the URN(s) is malformed.")   
        logging.debug("***************** ALL VMS OBTAINED, PROVISION THEM")
        # Once all the VMs are obtained, provision them
        for allocated_vm in allocated_vms:
            # First catch the RM Exception and translate them into GENIv3 Exceptions.
            # Then, apply best effort. 
            try:
                provisioned_vm = self._resource_manager.provision_vm(allocated_vm, end_time)
                provisioned_vms.append(provisioned_vm)
            except Exception as e:
                if best_effort:
                    self._undo_action(allocated_vms, "provision")
                    raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=allocated_vm['urn'], default=urn)
                else:
                    # First, try to let the failed VM on the previous state
                    self._undo_action(allocated_vm, "provision")
                    # Then, generate the error entry
                    allocated_vm['error_message'] = str(e)
                    provisioned_vms.append(allocated_vm)
        # Once all the VMs are provisioned, generate the response
        # Generate the Manifest RSpec
        rspecs = self._get_manifest_rspec(allocated_vms)
        # Generate the JSON with the VMs information
        slivers = list()
        for allocated_vm in allocated_vms:
            sliver = self._get_sliver_status_hash(allocated_vm, True)
            slivers.append(sliver)
        return rspecs, slivers
    
    def status(self, urns, client_cert, credentials):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
         #client_urn, client_uuid, client_email = self.auth(client_cert, credentials, urn, ('sliverstatus',)) # authenticate for each given slice
        vms = list()
        for urn in urns:
            if (self.urn_type(urn) == 'slice'):
                try:
                    slice_vms = self._resource_manager.get_vms_in_container(urn)
                except Exception as e:
                    raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=urn, default=urn)
                if slice_vms:
                    vms.extend(slice_vms)
            elif (self.urn_type(urn) == 'sliver'):
                try:
                    vm = self._resource_manager.get_vm_object_by_urn(urn)
                    vms.append(vm)
                except Exception as e:
                    raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=urn, default=urn)
            else:
                raise geniv3_exception.GENIv3OperationUnsupportedError('Only slice or sliver URNs can be given to status in this aggregate') 
        if not vms:
            raise geniv3_exception.GENIv3SearchFailedError("There are no resources in the given slice(s)")
        vms_info = list()
        for vm in vms:
            vm_info = self._resource_manager.get_vm_info(vm)
            vms_info.append(vm_info)
        sliver_list = [self._get_sliver_status_hash(vm, True, True) for vm in vms_info]
        result_rspec = self._get_manifest_rspec(vms_info)
        return result_rspec, sliver_list
    
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
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        vms = list()
        # First get all the information from the VMs, in case any problem on the delete process occurs 
        for urn in urns:
            # Honor best-effort
            try:
                # If the urn is a slice urn, obtain all the VMs associated to it
                if (self.urn_type(urn) == "slice"):
                    try:
                        vms_in_slice = self._resource_manager.get_vms_in_container(urn, "GENIv3")
                    except Exception as e:
                        raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=urn, default=urn)
                    vms.extend(vms_in_slice)
                # If the urn is a resource urn, obtain the resource
                elif (self.urn_type(urn) == 'sliver'):
                    try:
                        vm_to_delete = self._resource_manager.get_vm_by_urn(urn)
                    except Exception as e:
                        raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=urn, default=urn)
                    vms.append(vm_to_delete)
                # Otherwhise, the urn is invalid
                else:
                    raise geniv3_exception.GENIv3OperationUnsupportedError('Only slice and sliver URNs can be deleted in this aggregate')
            except Exception as e:
                if best_effort:
                    raise e
                else:
                    deleted_vms.append(self._generate_error_entry(urn, str(e)))
        # If no vms to delete, raise an Exception
        if not vms:
            raise geniv3_exception.GENIv3SearchFailedError("There are no resources to provision. Perhaps they expired or the URN(s) is malformed.")    
        # Once we know all the VMs exists, delete them
        deleted_vms = list()
        for vm in vms:
            # Honor best-effort
            try:
                deleted_vm = self._resource_manager.delete_vm(vm['uuid'])    
                deleted_vms.append(deleted_vm)
            except Exception as e:
                if best_effort:
                    self._undo_action(allocated_vms, "delete")
                    raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=urn, default=urn)
                else:
                    # First, try to let the failed VM on the previous state
                    self._undo_action(vm, "delete")
                    # Then, generate the error entry
                    vm['error_message'] = str(e)
                    deleted_vms.append(vm)
        # Once all the VMs are provisioned, generate the response
        # Generate the Manifest RSpec
        rspecs = self._get_manifest_rspec(deleted_vms)
        # Generate the JSON with the VMs information
        slivers = list()
        for deleted_vm in deleted_vms:
            sliver = self._get_sliver_status_hash(deleted_vm, True)
            slivers.append(sliver)
        return rspecs, slivers
 
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
    def _get_sliver_status_hash(self, sliver, include_allocation_status=False, include_operational_status=False):
        """Helper method to create the sliver_status return values of allocate and other calls."""
        result = {'geni_sliver_urn' : sliver['urn'],
                  'geni_expires'    : sliver['expiration_time'] if 'expiration_time' in sliver.keys() else None,
                  'geni_allocation_status' : self.ALLOCATION_STATE_UNALLOCATED}
        if (include_allocation_status):
            result['geni_allocation_status'] = self.ALLOCATION_STATE_ALLOCATED if sliver['state'] is "allocated" else self.ALLOCATION_STATE_PROVISIONED
        if (include_operational_status): 
            result['geni_operational_status'] = self.OPERATIONAL_STATE_NOTREADY if sliver['state'] is "ongoing" or "allocated" else self.OPERATIONAL_STATE_FAILED if 'error_message' in sliver.keys() else self.OPERATIONAL_STATE_READY
        try:
            result['geni_error'] = sliver['error_message']
        except:
            pass
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
 
    def _generate_error_entry(self, urn, error_message):
        vm_with_error = {'urn':urn, 'error_message':error_message}
        return vm_with_error
    
    def _undo_action(self, params, action):
        if action == "allocate":
            for param in params:
                try:
                    self._resource_manager.delete_vm_by_uuid(param['uuid'])
                except:
                    continue
        elif action == "create":
            for param in params: 
                try:
                    self._resource_manager.delete_vm_by_uuid(param['uuid'])            
                except:
                    continue
