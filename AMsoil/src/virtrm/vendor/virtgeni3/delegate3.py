import time 
import amsoil.core.pluginmanager as pm
import xml.etree.ElementTree as ET
import lxml
from geni3util.exceptiontranslator import ExceptionTranslator
from geni3util.filterednodes import RSPECS_FILTERED_NODES
from geni3util.xrn import *
import amsoil.core.log
import copy

logging=amsoil.core.log.getLogger('VTDelegate3')


'''@author: SergioVidiella, CarolinaFernandez'''


GENIv3DelegateBase = pm.getService('geniv3delegatebase')
geniv3_exception = pm.getService('geniv3exceptions')
virt_exception = pm.getService('virtexceptions')

# CONTAINER PREFIX FOR GENIv3 PLUGIN
GENIv3_prefix = "GENIv3"

# VIRTRM ACTIONS
VIRTM_START = "start"
VIRTRM_STOP = "stop"
VIRTRM_RESTART = "restart"

# METHOD ACTIONS TO UNDOO
ACTION_ALLOCATE = "allocate"
ACTION_PROVISIONING = "provisioning"
ACTION_RENEW = "renew"
ACTION_DELETE = "delete"

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
                    allocated_vm = self._resource_manager.allocate_vm(requested_vm, end_time, slice_urn, GENIv3_prefix)
                    allocated_vms.append(allocated_vm)
                # Translate the specific RM Exceptions into GENIv3 Exceptions
                except Exception as e:
                    logging.debug("********************* EXCEPTION => %s / TYPE => %s" % (str(e), str(type(e))))
                    raise ExceptionTranslator.virtexception2GENIv3exception(type(e), name=requested_vm['name'], server=requested_vm['server_uuid'], urn=requested_vm['urn'], default=requested_vm['urn'])
        # If any VM fails in allocating, we unallocate all the previously allocated VMs
        except Exception as e:
            self._undo_action(allocated_vms, ACTION_ALLOCATE)
            raise e
        # Generate the Manifest RSpec
        rspecs = self._get_manifest_rspec(allocated_vms)
        # Generate the JSON with the VMs information
        slivers = list()
        for allocated_vm in allocated_vms:
            # Add the status information here, due allocated vms does not have one
            sliver = self._get_sliver_status_hash(allocated_vm)
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
                        vms_in_container = self._resource_manager.get_allocated_vms_in_container(urn, GENIv3_prefix)
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
        if not vms and not renewed_vms:
            raise geniv3_exception.GENIv3SearchFailedError("There are no resources to renew. Perhaps they expired or the URN(s) is malformed.")
        for vm in vms:
            try:
                renewed_vm = self._resource_manager.extend_vm_expiration_by_uuid(vm['uuid'], expiration_time)
                renewed_vms.append(renewed_vm)
            except Exception as e:
                if best_effort:
                    self._undo_action(renewed_vms, ACTION_RENEW)
                    raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=vm['urn'], default=vm['urn'])
                else:
                    # First, try to let the failed VM on the previous state
                    self._undo_action(vm, ACTION_RENEW)
                    # Then, generate the error entry
                    vm['error_message'] = str(e)
                    renewed_vms.append(vm)
        # Once all the VMs are renewed, generate the response
        # Generate the JSON with the VMs information
        slivers = list()
        for renewed_vm in renewed_vms:
            sliver = self._get_sliver_status_hash(renewed_vm)
            slivers.append(sliver)
        return slivers

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
                        logging.debug("********************* TYPE SLICE")
                        vms = self._resource_manager.get_allocated_vms_in_container(urn, GENIv3_prefix)      
                        logging.debug("********************* VMS OBTAINED IN SLICE %s => %s" % (str(urn), str(vms)))
                    # Throw the Exception for every kind of error
                    except Exception as e:
                        raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=urn, default=urn)
                    allocated_vms.extend(vms)
                elif (self.urn_type(urn) == "sliver"):
                    logging.debug("********************* TYPE SLICE")
                    # If the UNR is from a VM, get it
                    try: 
                        vm = get_vm_allocated_by_urn(urn)
                        logging.debug("********************* VM %s OBTAINED => %s" % (str(urn), str(vm)))
                    except Exception as e:
                        raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=urn, default=urn)
                    allocated_vms.append(vm)
                else:
                    raise geniv3_exception.GENIv3BadArgsError("Urn has a type unable to create" % (urn,))
            # If {best_effort = False} throw the given Exception
            # If {best_effort = True} keep going 
            except Exception as e:
                if not best_effort:
                    raise e
                else:
                    provisioned_vms.append(self._generate_error_entry(urn, str(e)))
        # If any resource is obtained, raise an error
        if not allocated_vms and not provisioned_vms:
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
                if not best_effort:
                    self._undo_action(allocated_vms, ACTION_PROVISIONING)
                    raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=allocated_vm['urn'], default=urn)
                else:
                    # First, try to let the failed VM on the previous state
                    self._undo_action(allocated_vm, ACTION_PROVISIONING)
                    # Then, generate the error entry
                    allocated_vm['error_message'] = str(e)
                    provisioned_vms.append(allocated_vm)
        # Once all the VMs are provisioned, generate the response
        # Generate the Manifest RSpec
        rspecs = self._get_manifest_rspec(allocated_vms)
        # Generate the JSON with the VMs information
        slivers = list()
        for provisioned_vm in provisioned_vms:
            sliver = self._get_sliver_status_hash(provisioned_vm, True)
            slivers.append(sliver)
        return rspecs, slivers
    
    def status(self, urns, client_cert, credentials):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
         #client_urn, client_uuid, client_email = self.auth(client_cert, credentials, urn, ('sliverstatus',)) # authenticate for each given slice
        vms = list()
        for urn in urns:
            if self.urn_type(urn) == 'slice':
                try:
                    slice_vms = self._resource_manager.get_vms_in_container(urn, GENIv3_prefix)
                    vms.extend(slice_vms)
                except Exception as e:
                    raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=urn, default=urn)
            elif self.urn_type(urn) == 'sliver':
                try:
                    vm = self._resource_manager.get_vm_by_urn(urn)
                    vms.append(vm)
                except Exception as e:
                    raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=urn, default=urn)
            else:
                raise geniv3_exception.GENIv3OperationUnsupportedError('Only slice or sliver URNs can be given to status in this aggregate') 
        if not vms:
            raise geniv3_exception.GENIv3SearchFailedError("There are no resources in the given slice(s)")
        # Once all the VMs are given, generate the response
        # Generate the Manifest RSpec
        rspecs = self._get_manifest_rspec(vms)
        # Generate the JSON with the VMs information
        slivers = list()
        for vm in vms:
            sliver = self._get_sliver_status_hash(vm, True)
            slivers.append(sliver)
        return rspecs, slivers
    
    def perform_operational_action(self, urns, client_cert, credentials, action, best_effort):
        provisioned_vms = list()
        vms = list()
        for urn in urns:
            try:
                if self.urn_type(urn) == 'slice':
                    #client_urn, client_uuid, client_email = self.auth(client_cert, credentials, urn, ('sliverstatus',)) # authenticate for each given slice
                    try:
                        slice_vms = self._resource_manager.get_provisioned_vms_in_container(urn, GENIv3_prefix)
                        provisioned_vms.extend(slice_vms)
                    except Exception as e:
                        raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=urn, default=urn)
                elif self.urn_type(urn) == 'sliver':
                    try:
                        provisioned_vm = self._resource_manager.get_vm_by_urn(urn)
                        provisioned_vms.append(provisioned_vm)
                    except Exception as e:
                        raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=urn, default=urn)
                else:
                    raise geniv3_exception.GENIv3BadArgsError("Urn has a type unable to create" % (urn,))
            # If {best_effort = False} throw the given Exception
            # If {best_effort = True} keep going 
            except Exception as e:
                if not best_effort:
                    raise e
                else:
                    vms.append(self._generate_error_entry(urn, str(e)))
        if not provisioned_vms and not vms:
                raise geniv3_exception.GENIv3SearchFailedError("There are no resources in the given slice(s)")
        for provisioned_vm in provisioned_vms:
            try:
                if action == self.OPERATIONAL_ACTION_START:
                    crud_action = VIRTRM_START
                elif action == self.OPERATIONAL_ACTION_STOP:
                    crud_action = VIRTRM_STOP
                elif action == self.OPERATIONAL_ACTION_RESTART:
                    crud_action = VIRTRM_RESTART
                else:
                    raise geniv3_exception.GENIv3BadArgsError("Action not suported in this AM" % (urn,))
                try:
                    vm = self._resource_manager.crud_vm_by_urn(provisioned_vm['urn'], crud_action)
                    vms.extend(vm)
                except Exception as e:
                    raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=urn, default=urn)
            except Exception as e:
                if not best_effort:
                    self._undo_action(vms, ACTION_PERFORM_ACTION)
                    raise e
                else:
                    # First, try to let the failed VM on the previous state
                    self._undo_action(provisioned_vm, ACTION_PERFORM_ACTION)
                    # Then, generate the error entry
                    provisioned_vm['error_message'] = str(e)
                    vms.append(provisioned_vm)
        # Once all the VMs are provisioned, generate the response
        # Generate the JSON with the VMs information
        slivers = list()
        for vm in vms:
            sliver = self._get_sliver_status_hash(vm, True)
            slivers.append(sliver)
        return slivers
    
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
                        vms_in_slice = self._resource_manager.get_vms_in_container(urn, GENIv3_prefix)
                    except Exception as e:
                        raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=urn, default=urn)
                    vms.extend(copy.deepcopy(vms_in_slice))
                # If the urn is a resource urn, obtain the resource
                elif (self.urn_type(urn) == 'sliver'):
                    try:
                        vm_to_delete = self._resource_manager.get_vm_by_urn(urn)
                    except Exception as e:
                        raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=urn, default=urn)
                    vms.append(copy.deepcopy(vm_to_delete))
                # Otherwhise, the urn is invalid
                else:
                    raise geniv3_exception.GENIv3OperationUnsupportedError('Only slice and sliver URNs can be deleted in this aggregate')
            except Exception as e:
                if not best_effort:
                    raise e
                else:
                    deleted_vms.append(self._generate_error_entry(urn, str(e)))
        # If no vms to delete, raise an Exception
        # XXX: If no VMs to delete but the Container exists return an empty list
        # TODO: Container should have an Expiration equals to the maximum Expiration of any contained VM
        # TODO: Worker should find expired Containers and check if any VM is contained, then destroy all
        # TODO: Every time allocate/provision/renew is invoked Container expiration should be updated
#        if not vms:           
#            raise geniv3_exception.GENIv3SearchFailedError("There are no resources to provision. Perhaps they expired or the URN(s) is malformed.")    
        logging.debug("***************** VMS TO DELETE => %s" % str(vms))
        # Once we know all the VMs exists, delete them
        deleted_vms = list()
        for vm in vms:
            # Honor best-effort
            try:
                deleted_vm = self._resource_manager.delete_vm_by_uuid(vm['uuid'])    
                logging.debug("*************** DELETED DELEGATE VM => %s" % str(deleted_vm))
                deleted_vms.append(deleted_vm)
            except Exception as e:
                logging.debug("*************************** EXCEPTION IS => %s" % str(e))
                if not best_effort:
                    self._undo_action(deleted_vms, ACTION_DELETE)
                    raise ExceptionTranslator.virtexception2GENIv3exception(type(e), urn=urn, default=urn)
                else:
                    # First, try to let the failed VM on the previous state
                    self._undo_action(vm, ACTION_DELETE)
                    # Then, generate the error entry
                    vm['error_message'] = str(e)
                    deleted_vms.append(vm)
        # Once all the VMs are provisioned, generate the response
        # Generate the JSON with the VMs information
        slivers = list()
        for deleted_vm in deleted_vms:
            sliver = self._get_sliver_status_hash(deleted_vm)
            slivers.append(sliver)
        logging.debug("******************* SLIVERS => %s" % str(slivers))
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
    def _get_sliver_status_hash(self, sliver, include_operational_status=False):
        """Helper method to create the sliver_status return values of allocate and other calls."""
        result = {'geni_sliver_urn' : sliver['urn'],
                  'geni_expires'    : sliver['expiration_time'] if 'expiration_time' in sliver.keys() else None,
                  'geni_allocation_status' : self.ALLOCATION_STATE_ALLOCATED if sliver['state'] == "allocated" else self.ALLOCATION_STATE_UNALLOCATED if sliver['state'] == "deleted" else self.ALLOCATION_STATE_PROVISIONED}
        if include_operational_status: 
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
        if action is ACTION_ALLOCATE:
            for param in params:
                # For every allocated VM, try to delete it
                try:
                    self._resource_manager.delete_vm_by_uuid(param['uuid'])
                except:
                    continue
        elif action is ACTION_PROVISIONING:
            for param in params:
                # First try to delete the provisioned VMs 
                try:
                    self._resource_manager.delete_vm_by_uuid(param['uuid'])            
                except:
                    continue
                # Then, try to allocate them to the previous state
                try:
                    # TODO: Get the correct args
                    self._resource_manager.allocate_vm(requested_vm, end_time, slice_urn, GENIv3_prefix)
                except:
                    continue
