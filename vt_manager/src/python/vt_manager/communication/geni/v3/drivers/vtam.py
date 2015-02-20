from am.geniutils.src.xrn.xrn import hrn_to_urn
from am.rspecs.src.geni.v3.container.resource import Resource
from am.rspecs.src.geni.v3.container.sliver import Sliver
from am.rspecs.src.geni.v3.container.link import Link

from vt_manager.controller.drivers.VTDriver import VTDriver
from vt_manager.controller.dispatchers.xmlrpc.ProvisioningDispatcher import ProvisioningDispatcher
from vt_manager.models.VirtualMachineKeys import VirtualMachineKeys
from vt_manager.utils.contextualization.vm_contextualize import VMContextualize
from vt_manager.utils.UrlUtils import UrlUtils
from vt_manager.models.VirtualMachine import VirtualMachine
from vt_manager.models.VTServer import VTServer
from vt_manager.models.Action import Action
from vt_manager.models.reservation import Reservation
from vt_manager.models.expiring_components import ExpiringComponents

from vt_manager.utils.SyncThread import SyncThread
from vt_manager.utils.ServiceProcess import ServiceProcess
from vt_manager.utils.ServiceThread import ServiceThread
from vt_manager.communication.utils.XmlHelper import XmlHelper
from vt_manager.communication.utils.XmlHelper import XmlCrafter
from vt_manager.models.VirtualMachineKeys import VirtualMachineKeys

from geniutils.src.xrn.xrn import hrn_to_urn
from geniutils.src.xrn.xrn import urn_to_hrn

import multiprocessing
import threading
import copy
import uuid
import logging
import random
from datetime import datetime
from datetime import timedelta
import dateutil.parser

class VTAMDriver:

    def __init__(self):
       self.__geni_best_effort_mode = True
       self.__agent_callback_url = "SFA.OCF.VTM"
       self.__mutex_thread = threading.Lock()
       self.__mutex_process = multiprocessing.Lock()
       self.GENI_ALLOCATED = "geni_allocated"
       self.GENI_UNALLOCATED = "geni_unallocated"
       self.GENI_PROVISIONED = "geni_provisioned"
       self.GENI_READY = "geni_ready"
       self.GENI_NOT_READY = "geni_notready"
       self.GENI_CONFIGURING = "geni_configuring"
       self.GENI_FAILED = "geni_failed"
       self.GENI_PENDING_TO_ALLOCATE = "geni_pending_allocation"
       self.GENI_UPDATING_USERS = "geni_updating_users"
       
       self.__config = None

    def get_version(self):
        return None

    def get_specific_server_and_vms(self, urn, geni_available=False):
        """
        When 'available' is False or unspecified, all resources must be retrieved.
        """
        params =  self.__urn_to_vm_params(urn)
        servers = VTServer.objects.all()
        resources = list() 
        vms = list()
        for server in servers:
            if not server.available and geni_available:
                continue
            # Look for provisioned VMs
            vms_provisioned = server.getChildObject().getVMs(**params)
            # ... Also for reserved VMs
            vms_allocated = Reservation.objects.filter(server__id=server.id)
            vms.extend(vms_provisioned)
            # NOTE: if there are VMs provisioned, these are the ones to be returned
            # Explanation: when a VM is provisioned, the reservation for the
            # VM may still be active, but it is of no interest to the user
            #if not vms_provisioned:
            vms.extend(vms_allocated)
            if vms:
                converted_resources = self.__convert_to_resources_with_slivers(server, vms)
                resources.extend(converted_resources)
        return resources

    def get_all_servers(self, geni_available=False):
        """
        When 'available' is False or unspecified, all resources must be retrieved.
        """
        resources = list()
        servers = VTServer.objects.all()
        for server in servers:
            if server.available or not geni_available:
                resource = self.__convert_to_resource(server)
                resources.append(resource)
                links = self.__convert_to_links(server)
                resources.extend(links)
            else:
                continue
        return resources        

    def __validate_precondition_states(self, vm, method_name=""):
        method_name += " action"
        # Methods that alter VirtualMachine should not operate on VMs in a transient state ("..." on it)
        if "..." in self.__translate_to_operational_state(vm):
            raise Exception("REFUSED to perform %s on sliver in a transient state" % str(method_name))
    
    def create_vms(self, urn, expiration=None, users=list(), geni_best_effort=True):
        #TODO: Manage Exceptions,
        # NOTE that "geni_best_effort" is False by default. This is not how it is intended to work
        vm_params  = self.__urn_to_vm_params(urn)
        reservations = Reservation.objects.filter(**vm_params)
        # Provisioning a VM must be made after an Allocate. Allocate:Provisioning follow 1:1 ratio
        if not reservations:
            # Be cautious when changing the messages, as handler depends on those
            raise Exception("No allocation found")
        
        # Retrieve only the reservations that are provisioned
        reservations = Reservation.objects.filter(**vm_params).filter(is_provisioned=False)
        
        if not reservations:
            # Be cautious when changing the messages, as handler depends on those
            raise Exception("Re-provisioning not possible. Try allocating first")
        
        slivers_to_manifest = list()
        
        for r in reservations:
            try:
                provisioning_rspec = self.get_action_instance(r)
                with self.__mutex_thread:
                    SyncThread.startMethodAndJoin(ProvisioningDispatcher.processProvisioning,provisioning_rspec,self.__agent_callback_url)
                vms = VirtualMachine.objects.filter(**vm_params)
                self.__store_user_keys(users, vms)
                # When reservation (allocation) is fulfilled, mark appropriately
                r.set_provisioned(True)
                r.save()
            except Exception as e:
                if geni_best_effort:
                    manifested_resource = self.__convert_to_resources_with_slivers(r.server,vms,expiration)
                    manifested_resource.set_error_message(str(e))
                    if type(manifested_resource) == list:
                        slivers_to_manifest.extend(manifested_resource)
                    else:
                        slivers_to_manifest.append(manifested_resource)
                    continue
                else:
                    raise e
            manifested_resource = self.__convert_to_resources_with_slivers(r.server,vms,expiration)
            len(manifested_resource)
            if type(manifested_resource) == list:
                slivers_to_manifest.extend(manifested_resource)
            else:
                slivers_to_manifest.append(manifested_resource)
        self.__add_expiration(expiration, reservations[0].projectName, reservations[0].sliceName)
        return slivers_to_manifest       
    
    def reserve_vms(self, slice_urn, reservation, expiration=None, users=list()):
        # VMs are dynamic resource -> no collision will happen
        slice_hrn, hrn_type = urn_to_hrn(slice_urn)
        server_hrn, hrn_type = urn_to_hrn(reservation.get_component_id())

        server_name = server_hrn.split(".")[-1]
        server = VTServer.objects.get(name=server_name).getChildObject()
        server_id = server.id 
        if reservation.get_id():
            if Reservation.objects.filter(sliceName=slice_hrn, projectName=slice_hrn, name=reservation.get_id()) or VirtualMachine.objects.filter(sliceName=slice_hrn, projectName=slice_hrn, name=reservation.get_id()):
                raise Exception("There is another VM with client id %s on this slice already <GENI PROVISIONED> or <GENI ALLOCATED>" %reservation.get_id())
            reservation_name = reservation.get_id()
        else:
            reservation_name = str(random.randint(0,1000*1000))
        
        if expiration == None:
            expiration = datetime.utcnow() + timedelta(hours=1) 

        reserved_vm = Reservation()
        #reserved_vm.reservation_id = random.randint(0,1000)
        reserved_vm.server_id = server_id
        reserved_vm.set_slice_name(slice_hrn)
        reserved_vm.set_project_name(slice_hrn)
        reserved_vm.set_name(reservation_name)
        reserved_vm.set_valid_until(str(expiration))
        reserved_vm.uuid = str(uuid.uuid4())
        reserved_vm.save()
        
        # Set information for sliver
        reservation.get_sliver().set_urn(hrn_to_urn(server_hrn+"."+str(reserved_vm.id), "sliver"))
        reservation.get_sliver().set_allocation_status(self.GENI_ALLOCATED)
        reservation.get_sliver().set_expiration(expiration)
        reservation.get_sliver().set_operational_status(self.GENI_NOT_READY)
        reservation.get_sliver().set_client_id(reservation_name)
        reservation.set_allocation_status = self.GENI_ALLOCATED
        #vm_params = self.__urn_to_vm_params(slice_urn)
        #self.__store_user_keys(users, vm_params)
        return reservation
    
    def renew_vms(self, urn, expiration):
        vm_params =  self.__urn_to_vm_params(urn)
        resources = list()
        try:
            provisioned_vms = VirtualMachine.objects.filter(**vm_params)
            if provisioned_vms:
               for provisioned_vm in provisioned_vms:
                   self.__add_expiration(expiration, provisioned_vm.projectName, provisioned_vm.sliceName)
        except Exception as e:
            if self.__geni_best_effort:
                resources.extend(self.get_specific_server_and_vms(urn))
                for resource in resources:
                    resource.set_error_message(str(e))
                    continue
            else:
                raise e
        # An existing Reservation and a non existing VirtualMachine implies there is only an allocated VM
        try:
            reserved_vms = Reservation.objects.filter(**vm_params)
            for reserved_vm in reserved_vms:
                reserved_vm.set_valid_until(expiration)
                reserved_vm.save()
                self.__add_expiration(expiration, reserved_vm.projectName, reserved_vm.sliceName)
                resources.extend(self.__convert_to_resources_with_slivers(reserved_vm.server, [reserved_vm], expiration))
        except Exception as e:
            if reserved_vms:
               for reserved_vm in reserved_vms:
                   self.__add_expiration(expiration, reserved_vm.projectName, reserved_vm.sliceName)
                   resources.extend(self.__convert_to_resources_with_slivers(reserved_vm.server, [reserved_vm], expiration))
            raise e 
        return self.get_specific_server_and_vms(urn)

    def start_vm(self, urn):
        return self.__crud_vm(urn, Action.PROVISIONING_VM_START_TYPE) 

    def stop_vm(self, urn):
        return self.__crud_vm(urn, Action.PROVISIONING_VM_STOP_TYPE)

    def reboot_vm(self, urn):
        return self.__crud_vm(urn, Action.PROVISIONING_VM_REBOOT_TYPE)

    def delete_vm(self, urn):
        vm_params  = self.__urn_to_vm_params(urn)
        # Deleting allocated slivers
        vms_allocated = Reservation.objects.filter(**vm_params)
        # Deleting provisioned slivers
        vms_provisioned = VirtualMachine.objects.filter(**vm_params)
        # Remove SSH keys for each provisioned VM
        for vm_provisioned in vms_provisioned:
            params_list = self.__vm_to_ssh_keys_params_list(vm_provisioned)
            for params in params_list:
                VirtualMachineKeys.objects.filter(**params).delete()
        # Provisioned VMs are deleted here
        resources = self.__crud_vm(urn, Action.PROVISIONING_VM_DELETE_TYPE)
        if vms_provisioned or vms_allocated:
            expiration = ExpiringComponents.objects.filter(slice = vm_params["sliceName"])[0].expires
            for resource in resources:
                resource.set_allocation_state(self.GENI_UNALLOCATED)
                resource.set_operational_state(self.GENI_PENDING_TO_ALLOCATE)
                resource.get_sliver().set_allocation_status(self.GENI_UNALLOCATED)
                resource.get_sliver().set_operational_status(self.GENI_PENDING_TO_ALLOCATE)
                resource.get_sliver().set_expiration(expiration)
        # Allocated VMs are deleted here
        vms_allocated.delete()
        if not resources:
            raise Exception("Slice Does Not Exist")
        return resources

    def get_geni_best_effort_mode(self):
        return self.__geni_best_effort_mode

    def set_geni_best_effort_mode(self, value):
        self.__geni_best_effort_mode = value

    def __crud_vm(self, urn, action):
        params = self.__urn_to_vm_params(urn)
        servers = VTServer.objects.all()
        vm_server_pairs = list()
        resources = list()
        vms = list()
        for server in servers:
            # Look for provisioned VMs
            vms_provisioned = server.getChildObject().getVMs(**params)
            # ... Also for reserved VMs
            vms_allocated = Reservation.objects.filter(server__id=server.id)
            vms.extend(vms_provisioned)
            vms.extend(vms_allocated)
            for vm in vms:
                # The following is to be executed only for provisioned VMs
                if isinstance(vm, VirtualMachine):
                    # Return "REFUSED" exception if sliver is in a transient state
                    self.__validate_precondition_states(vm, action)
                    # Return "BUSY" exception if sliver is in incorrect operational state
                    if self.__translate_to_operational_state(vm) == self.GENI_UPDATING_USERS:
                        raise Exception("BUSY sliver in state '%s'" % self.GENI_UPDATING_USERS)
                    vm_params = {"server_uuid":server.uuid, "vm_id":vm.id}
                    if vm_params not in vm_server_pairs:
                        vm_server_pairs.append(vm_params)
                    try:
                        with self.__mutex_thread:
                            VTDriver.PropagateActionToProvisioningDispatcher(vm.id, server.uuid, action)
                    except Exception as e:
                        try:
                            if self.get_geni_best_effort_mode():
                                resource = self.__convert_to_resources_with_slivers(server, [vm])[0]
                                resource.set_error_message(str(e))
                                #resources.extend(resource)
                                resources.append(resource)
                                continue
                            else:
                                raise e
                        except Exception as e:
                            raise e
                # The resources are fetched for any (allocated/provisioned) VM
                resource = self.__convert_to_resources_with_slivers(server, [vm])
                resources.extend(resource)
        return resources

    def __urn_to_vm_params(self, urn):
        #XXX For now, I prefer to have the same slice name as project name
        hrn, hrn_type = urn_to_hrn(urn)
        if hrn_type == "sliver":
            value = hrn.split(".")[-1]
            return {"id":int(value)}
        elif hrn_type == "slice":
            return {"projectName":hrn, "sliceName":hrn} 
        else:
            return None

    def __convert_to_resource(self, server):
        #TODO add missing params 
        component_manager_id = self.__generate_component_manager_id(server)
        component_manager_name = self.__generate_component_manager_id(server)
        component_id = self.__generate_component_id(server)
        component_name = self.__generate_component_id(server)
        resource = Resource()
        resource.set_component_manager_id(component_manager_id)
        resource.set_component_id(component_id)
        resource.set_component_manager_name(component_manager_name)
        resource.set_component_name(component_name)
        # Default params
        resource.set_available(server.available)
        resource.set_exclusive(False)
        return resource

    def __convert_to_links(self, server):
        links = list()
        network_ifaces = server.networkInterfaces.all()
        for network_interface in network_ifaces:
            link = Link()
            if not network_interface.switchID:
                continue
                #network_interface.switchID = "OfeliaVPNGateWay"
            dpid_port = "%s_%s" % (network_interface.switchID, network_interface.port)
            component_id = self.__get_link_urn(network_interface.name, dpid_port, server.name)
            link.set_component_id(component_id)
            link.set_component_name(component_id)
            link.set_capacity("1024MB/s")
            link.set_dest_id(self.__get_foreign_urn(network_interface.switchID))
            link.set_source_id(self.__get_port_urn(network_interface.name, server.name))
            link.set_type("L2 Link")
            links.append(link)
        return links

    def __get_link_urn(self, source, dst, server_name):
        name = self.__correct_iface_name(source)
        return hrn_to_urn(self.__config.CM_HRN + "." + str(server_name)+ "." + str(name) + "-" + str(dst),"link")

    def __correct_iface_name(self, iface_name):
        # Returns correct eth name from server
        if "." not in iface_name:
    	    return iface_name.replace(iface_name[-1], str(int(iface_name[-1])-1))
        else:
            return self.__correct_iface_name(iface_name.split(".")[0])

    def __get_foreign_urn(self, dpid):
        return hrn_to_urn(self.__config.FOREIGN_HRN + "." + str(dpid),"datapath")

    def __get_port_urn(self, port, server_name):
        name = self.__correct_iface_name(port)
        return hrn_to_urn(self.__config.CM_HRN + "." + str(server_name) + "." + str(name),"interface")

    def __convert_to_resources_with_slivers(self, server, vms, expiration=None):
        """
        Always return a list of slivers, independently of the number of resources inside.
        """
        resource = self.__convert_to_resource(server)
        resources = list()
        for vm in vms:
            if not expiration:
                try:
                    expiration = ExpiringComponents.objects.filter(slice=vm.sliceName, authority=vm.projectName)[0].expires
                except Exception as e:
                    print e
            new_resource = copy.deepcopy(resource)
            new_resource.set_id(vm.name)
            sliver = Sliver()
            sliver.set_type("VM")
            sliver.set_expiration(expiration)
            sliver.set_client_id(vm.name)
            sliver.set_urn(self.__generate_sliver_urn(vm))
            sliver.set_slice_urn(hrn_to_urn(vm.sliceName, "slice"))
            if isinstance(vm, VirtualMachine):
                sliver.set_services(self.__generate_vt_am_services(vm))        
            sliver.set_allocation_status(self.__translate_to_allocation_state(vm))
            sliver.set_operational_status(self.__translate_to_operational_state(vm))
            sliver.set_expiration(expiration)
            new_resource.set_sliver(sliver)
            resources.append(copy.deepcopy(new_resource))
        return resources
    
    # Sliver Utils Stuff
    
    def __generate_vt_am_services(self, vm):
        vm_ip = self.__get_ip_from_vm(vm)
        login_services = [{"login":{"authentication":"ssh", "hostname":vm_ip, "port": "22", "username":"root:openflow"}}]
        keys = VirtualMachineKeys.objects.filter(vm_uuid=vm.uuid)
        used_user_names = []
        for key in keys:
            if not key.user_name in used_user_names:
                login_services.append({"login":{"authentication":"ssh-keys", "hostname":vm_ip, "port": "22", "username":key.user_name}})
                used_user_names.append(key.user_name)
        return login_services

    # URN Stuff

    def __generate_component_manager_id(self, server):
        return hrn_to_urn(self.__config.CM_HRN, "authority+cm")
    
    def __generate_component_manager_name(self, server):
        return hrn_to_urn(self.__config.CM_HRN, "authority+cm")

    def __generate_component_id(self, server):
        return hrn_to_urn(self.__config.CM_HRN+"."+str(server.name),"node")

    def __generate_component_name(self, server):
        return hrn_to_urn(self.__config.CM_HRN+"."+str(server.name),"node")

    def __generate_sliver_urn(self, vm):
        return hrn_to_urn(self.__config.CM_HRN+"."+str(vm.id), "sliver")

    def __select_sliver_expiration(self, user_expiration, slice_expiration=None, **kwargs):
        if not slice_expiration:
            current_time = datetime.utcnow()
            if "extension_timedelta" in kwargs:
                extension_timedelta = kwargs["extension_timedelta"]
            else:
                extension_timedelta = {"days": 31} # Default set to one month
            slice_expiration = current_time + timedelta(**extension_timedelta)
            slice_expiration = slice_expiration.replace(tzinfo=dateutil.tz.tzutc()).strftime("%Y-%m-%d %H:%M:%S")
            slice_expiration = slice_expiration.replace(" ", "T")+"Z"
        # Retrieve expiration = minimum ( user expiration, slice expiration )
        extended_expiration = min(user_expiration, slice_expiration)
        return extended_expiration
    
    # VT AM Models Utils
 
    def __get_ip_from_vm(self, vm):
        ifaces = vm.getNetworkInterfaces()
        for iface in ifaces:
            if iface.isMgmt:
                return iface.ip4s.all()[0].ip #IP
        return "None"
 
    def get_action_instance(self, reservation):
 	rspec = XmlHelper.getSimpleActionQuery()
 	actionClass = copy.deepcopy(rspec.query.provisioning.action[0])
        actionClass.type_ = "create"
        rspec.query.provisioning.action.pop()
        #server = reservation.server()
        server = reservation.server
 	vm = self.get_default_vm_parameters(reservation)
        actionClass.id = uuid.uuid4()
        self.vm_dict_to_class(vm, actionClass.server.virtual_machines[0])
 	self.vm_dict_ifaces_to_class(vm["interfaces"],actionClass.server.virtual_machines[0].xen_configuration.interfaces)
        actionClass.server.uuid = server.uuid
        actionClass.server.virtualization_type = server.getVirtTech()
        rspec.query.provisioning.action.append(actionClass)
        return rspec.query.provisioning
   
    def get_default_vm_parameters(self, reservation):
        vm = dict()
        ### TODO: Consider used the same name as id for porject and slices
        vm["project-id"] = str(uuid.uuid4())
        vm["slice-id"] = str(uuid.uuid4())	
 	vm["project-name"] = reservation.get_project_name()
 	vm["slice-name"]= reservation.get_slice_name()
 	vm["uuid"] = reservation.uuid
        vm["virtualization-type"] = reservation.server.getVirtTech()
 	vm["server-id"] = reservation.server.getUUID()
        vm["name"] = reservation.get_name()
        vm["state"] = "on queue"
        vm["aggregate-id"] = "aggregate-id"
        vm["operating-system-type"] = "GNU/Linux"
        vm["operating-system-version"] = "6.0"
        vm["operating-system-distribution"] = "Debian"
        vm["hd-origin-path"] = "legacy/legacy.tar.gz"
        vm["interfaces"] = list()
        vm["hd-setup-type"] = "file-image"
        vm["virtualization-setup-type"] = "paravirtualization"
        vm["memory-mb"] = 512
        return vm 

    def vm_dict_to_class(self, vm_dict, vm_class):
        vm_class.name = vm_dict["name"]
        vm_class.uuid = vm_dict["uuid"]
        vm_class.status = vm_dict["state"]
        vm_class.project_id = vm_dict["project-id"]
        vm_class.project_name = vm_dict["project-name"]
        vm_class.slice_id = vm_dict["slice-id"]
        vm_class.slice_name = vm_dict["slice-name"]
        vm_class.operating_system_type = vm_dict["operating-system-type"]
        vm_class.operating_system_version = vm_dict["operating-system-version"]
        vm_class.operating_system_distribution = vm_dict["operating-system-distribution"]
        vm_class.virtualization_type = vm_dict["virtualization-type"]
        vm_class.server_id = vm_dict["server-id"]
        vm_class.xen_configuration.hd_setup_type = vm_dict["hd-setup-type"]
        vm_class.xen_configuration.hd_origin_path = vm_dict["hd-origin-path"]
        vm_class.xen_configuration.virtualization_setup_type = vm_dict["virtualization-setup-type"]
        vm_class.xen_configuration.memory_mb = int(vm_dict["memory-mb"])
 
    def vm_dict_ifaces_to_class(self, iface_list, iface_class):
        iface_class_empty = copy.deepcopy(iface_class.interface[0])
        if not iface_list:
            iface_list = []
            iface = dict()
            iface["gw"] = None
            iface["mac"] = None
            iface["name"] = None
            iface["dns1"] = None
            iface["dns2"] = None
            iface["ip"] = None
            iface["mask"] = None               
            iface_list.append(iface)
	for iface in iface_list:
 	    iface_class_empty = copy.deepcopy(iface_class.interface[0])
 	    iface_class_empty.gw = iface["gw"]
 	    iface_class_empty.mac = iface["mac"]
 	    iface_class_empty.name = iface["name"]
 	    iface_class_empty.dns1 = iface["dns1"]
 	    iface_class_empty.dns2 = iface["dns2"]
 	    iface_class_empty.ip = iface["ip"]
 	    iface_class_empty.mask = iface["mask"]
 	    if "ismgmt" in iface.keys():
 	    	iface_class_empty.ismgmt = iface["ismgmt"]
 	    else:
 		iface_class_empty.ismgmt = "false"
            iface_class.interface.append(iface_class_empty)
        iface_class.interface.pop(0) # Deleting the empty interface instance

    def __translate_to_allocation_state(self, vm):
        if isinstance(vm, Reservation):
            return self.GENI_ALLOCATED
        else:
            return self.GENI_PROVISIONED
    
    def __translate_to_operational_state(self, vm):
        # TODO Extend
        """
        Defines mapping between OFELIA and GENI states
        """
        if isinstance(vm, Reservation):
            return self.GENI_NOT_READY
        else:
            if "running" in vm.state:
                return self.GENI_READY
            elif "contextualizing..." in vm.state:
                return self.GENI_UPDATING_USERS
            elif "ing..." in vm.state:
                return self.GENI_CONFIGURING 
            elif "failed" in vm.state:
                return self.GENI_FAILED
            else:
                return self.GENI_NOT_READY
    
    def __add_expiration(self, expiration, project_name, slice_name):
        expiring_slivers = ExpiringComponents.objects.filter(slice=slice_name)
        if expiring_slivers:
            expiring_sliver = expiring_slivers[0]
            expiring_sliver.expires = expiration
        else:
            expiring_sliver = ExpiringComponents(authority=project_name, slice=slice_name, expires=expiration)
        expiring_sliver.save()
    
    def retrieve_access_data(self, urns, geni_best_effort=False):
        accesses_data = []
        for urn in urns:
            vm_params =  self.__urn_to_vm_params(urn)
            vms = VirtualMachine.objects.filter(**vm_params)
            for vm in vms:
                vm_data = dict()
                vm_data["host"] = dict()
                access_data = self.__generate_vt_am_services(vm)
                vm_data["host"]["name"] = vm.name
                vm_data["login"] = []
                for access in access_data:
                    # Regroup and filter data to avoid replication
                    access = access["login"]
                    vm_data["host"]["ip"] = access["hostname"]
                    access.pop("hostname", None)
                    vm_data["login"].append(access)
                accesses_data.append(vm_data)
        return accesses_data
    
    def update_keys(self, urns, geni_users, geni_best_effort=False):
        """
        geni_update_users: The credentials[] argument must include credentials over the slice as usual. The options struct must include the geni_users option as specified in AM API v3 and with the semantics described above. This action is only legal on slivers in the geni_ready operational state. This action immediately moves all such slivers to a new geni_updating_users operational state. Slivers stays in that state until the aggregate completes the needed changes, at which time the slivers change back to the geni_ready operational state. Slivers may be in the geni_updating_users state for several minutes; during this time no other operational actions can be taken on the slivers.
        """
        self.set_geni_best_effort_mode(geni_best_effort)
        vms = list()
        resources = list()
        for urn in urns:
            params = self.__urn_to_vm_params(urn)
            servers = VTServer.objects.all()
            resources = list()
            for server in servers:
                vms = server.getChildObject().getVMs(**params)
        
        # Check preconditions (VMs must be in allowed state prior to update the keys)
        # If not on "best effort" mode, honor or revoke all requests
        if not self.get_geni_best_effort_mode():
            for vm in vms:
                # Return "REFUSED" exception if sliver is in a transient state
                self.__validate_precondition_states(vm, "PerformOperationalAction")
                # Only acts on slivers with state "geni_ready"
                if self.__translate_to_operational_state(vm) != self.GENI_READY:
                    raise Exception("REFUSED to perform OperationalAction on sliver not ready (maybe stopped or configuring)")
        
        # Store user's SSH keys
        self.__store_user_keys(geni_users, vms)
        for vm in vms:
            try:
                # Return "REFUSED" exception if sliver is in a transient state
                self.__validate_precondition_states(vm, "PerformOperationalAction")
                # Only acts on slivers with state "geni_ready"
                if self.__translate_to_operational_state(vm) != self.GENI_READY:
                    raise Exception("REFUSED to perform OperationalAction on sliver not ready (maybe stopped or configuring)")
                else: 
                    # Contextualize independently of the SSH keys stored this time
                    # Note that user might lose access to VM at some point after creation
                    ip = self.__get_ip_from_vm(vm)
                    vm_dict = self.__vm_to_ssh_keys_params_list(vm, geni_users)
                    # If no error was found, change operational status to "geni_updating_users"
                    try:
                        # NOTE that this is somewhat insecure
                        vm.state = "contextualizing..." # New state for states similar to self.GENI_UPDATING_USERS
                        vm.save()
                    except:
                        pass
                    self.__contextualize_vm(vm, ip)
                # Create resources with proper format
                servers = VTServer.objects.all()
                for server in servers:
                    # The server for the VM has been just found
                    vms = server.getChildObject().getVMs(**params)
                    if vms:
                        # Create resources with proper format
                        resource = self.__convert_to_resources_with_slivers(server, [vm])
                        resources.extend(resource)
            except Exception as e:
                try:
                    if self.get_geni_best_effort_mode():
                        # Create resources with proper format
                        resource = self.__convert_to_resources_with_slivers(server, [vm])[0]
                        resource.set_error_message(str(e))
                        resources.append(resource)
                        continue
                    else:
                        raise e
                except Exception as e:
                    raise e
            # If no error was found, change operational status back to "geni_ready"
            # (after information of slivers is sent to client)
            try:
                # NOTE that this is somewhat insecure
                vm.state = "running" # New state for states similar to self.GENI_READY
                vm.save()
            except:
                pass
        return resources
    
    def cancel_update_keys(self, urns, geni_best_effort=False):
        self.set_geni_best_effort_mode(geni_best_effort)
        vms = list()
        resources = list()
        servers = VTServer.objects.all()
        
        if not self.get_geni_best_effort_mode():
            for urn in urns:
                params = self.__urn_to_vm_params(urn)
                for server in servers:
                    vms = server.getChildObject().getVMs(**params)
                    # Check preconditions (VMs must be in allowed state prior to update the keys)
                    # If not on "best effort" mode, honor or revoke all requests
                    for vm in vms:
                        # NOTE that this method acts on transient states, as it is its aim to revert some of them
                        # Only acts on slivers with state "geni_updating_users"
                        if self.__translate_to_operational_state(vm) != self.GENI_UPDATING_USERS:
                            raise Exception("REFUSED to perform OperationalAction on sliver that had not updated users")
        
        for urn in urns:
            params = self.__urn_to_vm_params(urn)
            resources = list()
            for server in servers:
                # The server for the VM has been just found
                vms = server.getChildObject().getVMs(**params)
                for vm in vms:
                    try:
                        # Only acts on slivers with state "geni_updating_users"
                        if self.__translate_to_operational_state(vm) != self.GENI_UPDATING_USERS:
                            raise Exception("REFUSED to perform OperationalAction on sliver that had not updated users")
                        else:
                            # If no error was found, change operational status to "geni_ready"
                            try:
                                # NOTE that this is somewhat insecure
                                vm.state = "running" # State equivalent to self.GENI_READY
                                vm.save()
                            except:
                                pass
                    except Exception as e:
                        try:
                            if self.get_geni_best_effort_mode():
                                # Create resources with proper format
                                resource = self.__convert_to_resources_with_slivers(server, [vm])[0]
                                resource.set_error_message(str(e))
                                resources.append(resource)
                                continue
                            else:
                                raise e
                        except Exception as e:
                            raise e
                    # Create resources with proper format
                    resource = self.__convert_to_resources_with_slivers(server, [vm])
                    resources.extend(resource)
        return resources
    
    def __contextualize_vm(self, vm, ip):
        # SSH keys for users are passed to the VM right after it is started
        vm_keys = VirtualMachineKeys.objects.filter(slice_uuid=vm.sliceId, project_uuid=vm.projectId)
        params = {
            "vm_address": str(ip) ,
            "vm_user": "root",
            "vm_password": "openflow",
        }
        vm_context = VMContextualize(**params)
        try:
            for vm_key in vm_keys:
                with self.__mutex_process:
                    # FIXME Sometimes do not work properly and keys are not getting to the VM
                    ServiceProcess.startMethodInNewProcess(vm_context.contextualize_add_pub_key, 
                                    [vm_key.get_user_name(), vm_key.get_ssh_key()], self.__agent_callback_url)
        except Exception as e:
            raise e
    
    def __vm_to_ssh_keys_params_list(self, vm, users=[]):
        params_list = list()
        params = {"project_uuid": vm.projectId,
                "slice_uuid": vm.sliceId,
                "vm_uuid": vm.uuid,
                }
        if not users:
            params_list.append(params)
       
        for user in users:
            # Reuse "params" structure by operating on a new structure
            params_user = copy.deepcopy(params)
            # Retrieve user string from URN
            try:
                user_name = urn_to_hrn(user["urn"])[0].split(".")[-1]
            except:
                user_name = user["urn"]
            params_user.update({"user_name": user_name,})
            for key in user["keys"]:
                params_user_keys = copy.deepcopy(params_user)
                params_user_keys.update({"ssh_key": key,})
                params_list.append(params_user_keys)
        return params_list
    
    def __store_user_keys(self, users, vms):
        stored_keys = False
        try:
            # Wrap users into list, if not already
            if not isinstance(users, list):
                users = [users]
            for vm in vms:
                params_list = self.__vm_to_ssh_keys_params_list(vm, users)
                # Create N entries, each for a specific key
                for params in params_list:
                    # If SSH key is not yet stored
                    if not VirtualMachineKeys.objects.filter(**params):
                        key_entry = VirtualMachineKeys(**params)
                        key_entry.save()
                        stored_keys = True
        except Exception as e:
            logging.error("Could not store user SSH key. Details: %s" % str(e))  
        return stored_keys
    
    def get_config(self):
        return self.__config
    
    def set_config(self, value):
        self.__config = value
