from controller.dispatchers.provisioning.query import ProvisioningDispatcher
from controller.drivers.virt import VTDriver
from datetime import datetime, timedelta
from models.resources.virtualmachine import VirtualMachine
from models.resources.vmallocated import VMAllocated
from models.resources.vtserver import VTServer
from models.resources.xenserver import XenServer
from models.resources.xenvm import XenVM
from templates.manager import TemplateManager
from utils.base import db
from utils.expirationmanager import ExpirationManager
from utils.servicethread import ServiceThread
from utils.vmmanager import VMManager
from utils.xrn import *
import amsoil.core.log
import amsoil.core.pluginmanager as pm
import time
import utils.exceptions as virt_exception
import uuid

# AMsoil logger
logging=amsoil.core.log.getLogger('VTResourceManager')

'''
@author: SergioVidiella, CarolinaFernandez
'''

class VTResourceManager(object):
    config = pm.getService("config")
    worker = pm.getService("worker")
    translator = pm.getService("virtutils").Translator
    
    EXPIRY_CHECK_INTERVAL = config.get("virtrm.EXPIRATION_VM_CHECK_INTERVAL") 
    
    ALLOCATION_STATE_ALLOCATED = "allocated"
    ALLOCATION_STATE_PROVISIONED = "provisioned"
    
    def __init__(self):
        super(VTResourceManager, self).__init__()
        # Register callback for regular updates
        self.worker.addAsReccurring("virtrm", "check_vms_expiration", None, self.EXPIRY_CHECK_INTERVAL)
        self.expiration_manager = ExpirationManager()
        self.template_manager = TemplateManager()
    
    # Server methods
    def get_servers(self, uuid=None):
        """
        Get server by uuid. 
        If no uuid provided, return all servers.
        """
        if uuid:
            servers = get_server(uuid)
        else:
            servers = []
            server_objs = self.get_server_objects()
            for server_obj in server_objs:
                server = self.translator.model2dict(server_obj)
                templates = self.template_manager.get_templates_from_server(server["uuid"])
                if templates:
                    server["disc_image_templates"] = templates
                servers.append(server)
        return servers

    def get_server_objects(self, uuid=None):
        """
        Get server by uuid. 
        If no uuid provided, return all servers.
        """
        if uuid:
            servers = self.get_server_object(uuid)
        else:
            servers = VTDriver.get_all_servers()
        return servers

    def get_server(self, uuid):
        """
        Get server with a given UUID as a dict.
        """
        server_obj = self.get_server_object(uuid)
        server = self.translator.model2dict(server_obj)
        templates = self.template_manager.get_templates_from_server(server["uuid"])
        if templates:
            server["disc_image_templates"] = templates
        return server   

    def get_server_object(self, uuid):
        """
        Get server with a given UUID.
        """
        server = VTDriver.get_server_by_uuid(uuid)
        return server
    
    def get_server_info(self, uuid):
        """
        Retrieve info for a server with a given UUID.
        """
        pass

    def get_provisioned_vms_in_server(self, server_uuid):
        """
        Obtains list of provisioned VMs for a server with a given UUID as a dict.
        """
        vms = []
        vm_objs = self.get_provisioned_vms_object_in_server(server_uuid)
        for vm_obj in vm_objs:
            vm = self.get_vm_info(vm_obj)
            vms.append(vm)
        return vms
 
    def get_provisioned_vms_object_in_server(self, server_uuid):
        """
        Obtains list of provisioned VMs for a server with a given UUID.
        """
        server = self.get_server_object(server_uuid)
        vms = VTDriver.get_vms_in_server(server)
        return vms
    
    def get_allocated_vms_in_server(self, server_uuid):
        """
        Obtains list of allocated VMs for a server with given UUID as a dict.
        """
        vms = []
        vm_objs = self.get_allocated_vms_object_in_server(server_uuid)
        for vm_obj in vm_objs:
            vm = self.get_vm_info(vm_obj)
            vms.append(vm)
        return vms
    
    def get_allocated_vms_object_in_server(self, server_uuid):
        """
        Obtains list of alloacted VMs for a server with given UUID.
        """
        server = self.get_server_object(server_uuid)
        vms = get_allocated_vms_in_server(server)
        return vms

    # VM methods
    def get_vm_uuid_by_vm_urn(self, vm_urn):
        pass

    def get_vm_urn_by_bm_uuid(self, vm_uuid):
        pass

    def get_vm_info(self, vm):
         # Generate a dictionary from the VM
        vm_dict = self.translator.model2dict(vm)
        # Obtain the URN and add it to the dictionary
        try:
            vm_urn = self.get_vm_urn_by_vm_uuid(vm_dict["uuid"])
        except:
            vm_urn = None 
        if vm_urn:
            vm_dict["urn"] = vm_urn
        # Add the Expiration information
        try:
            generation_time = self.expiration_manager.get_start_time_by_vm_uuid(vm_dict["uuid"])
        except:
            generation_time = None
        if generation_time:
            vm_dict['generation_time'] = generation_time
        try:
            expiration_time = self.expiration_manager.get_end_time_by_vm_uuid(vm_dict["uuid"])
        except:
            expiration_time = None
        if expiration_time:
            vm_dict['expiration_time'] = expiration_time
        # Add the Template information
        template = self.template_manager.get_template_from_allocated_vm(vm_dict["uuid"])
        vm_dict["disc_image"] = template
        # Add server information manually
        server = self.get_server(vm_allocated_dict["server_uuid"])
        vm_allocated_dict["server_name"] = server["name"]
        vm_allocated_dict["virtualisation_technology"] = server["virtualisation_technology"]
        return vm_dict
    
    def get_vm(self, vm_uuid):
        try:
            vm = self.get_vm_object(vm_uuid)
        except Exception as e:
            raise e
        vm_dict = self.get_vm_info(vm)
        return vm_dict
         

    def get_vm_object(self, vm_uuid):
        try:
            vm = VTDriver.get_vm_by_uuid(vm_uuid)
        except:
            try:
                vm = VTDriver.get_vm_allocated_by_uuid(vm_uuid)
            except Exception as e:
                raise e
        return vm

    def get_vm_by_urn(self, vm_urn):
        # TODO: Call other class methods for this, or make a generic method in VTDriver
        try:
            vm = VirtualMachine.query.filter_by(urn=vm_urn).one()
            return vm
        except:
             raise Exception

    def get_vms_in_slice(self, slice_urn):
        """
        Get all VMs in slice with given slice_urn.
        """
        vms = list()
        vms_created = self._get_provisioned_vms_in_slice(slice_urn)
        vms.extend(vms_created)
        vms_reserved = self._get_allocated_vms_in_slice(slice_urn)
        vms.extend(vms_reserved)
        return vms
    
    def get_provisioned_vms_in_slice(self, slice_urn):
        """
        Get all VMs provisioned (created) in a given slice.
        """
        slice_hrn, hrn_type = urn_to_hrn(slice_urn)
        slice_name = get_leaf(slice_hrn)
        project_name = get_leaf(get_authority(slice_hrn))
        vms = VirtualMachine.query.filter_by(slice_name=slice_name).filter_by(project_name=project_name).all()
        return vms

    def get_allocated_vms_in_slice(self, slice_urn):
        """
        Get all VMs allocated (reserved) in a given slice.
        """
        slice_hrn, hrn_type = urn_to_hrn(slice_urn)
        slice_name = get_leaf(slice_hrn)
        project_name = get_leaf(get_authority(slice_hrn))
        vms = VMAllocated.query.filter_by(slice_name=slice_name).filter_by(project_name=project_name).all()
        return vms
    
    def _destroy_vm(self, vm_id, server_uuid):
        if not server_uuid:
            server_uuid = XenDriver.get_server_uuid_by_vm_id(vm_id)
        try:
            VTDriver.propagate_action_to_provisioning_dispatcher(vm_id, server_uuid, Action.PROVISIONING_VM_DELETE_TYPE)
            return "success"
        except Exception as e:
            return "error" 
    
    def provision_allocated_vms(self, slice_urn, end_time):
        """
        Provision (create) previously allocated (reserved) VMs.
        """
        import uuid
        max_duration = self.RESERVATION_TIMEOUT
        max_end_time = datetime.utcnow() + timedelta(0, max_duration)
        if end_time == None:
            end_time = max_end_time
        if (end_time > max_end_time):
            raise VTMaxVMDurationExceeded(vm_name)
        if (end_time < datetime.utcnow()):
            end_time = max_end_time
        allocated_vms = VMAllocated.query.filter_by(slice_name=get_leaf(slice_urn)).all()        
        vms_params = list()
        servers = list()
        project = None
        for allocated_vm in allocated_vms:
            server = VTDriver.get_server_by_id(allocated_vm.get_server_id())
            params = dict()
            params['name'] = allocated_vm.name
            params['uuid'] = uuid.uuid4()
            params['state'] = "creating"
            params['project-id'] = None
            params['server-id'] = server.uuid
            params['slice-id'] = allocated_vm.sliceId
            params['slice-name'] = allocated_vm.slice_name
            params['operating-system-type'] = allocated_vm.operatingSystemType
            params['operating-system-version'] = allocated_vm.operatingSystemVersion
            params['operating-system-distribution'] = allocated_vm.operatingSystemDistribution
            params['virtualization-type'] = allocated_vm.hypervisor
            params['hd-setup-type'] = allocated_vm.hdSetupType
            params['hd-origin-path'] = allocated_vm.hdOriginPath
            params['virtualization-setup-type'] = allocated_vm.virtualizationSetupType
            params['memory-mb'] = allocated_vm.memory
            #XXX: Currently, this is always an empty list, interfaces are not allowed
            interfaces = list()
            interface = dict()
            interface['gw'] = None
            interface['mac'] = None
            interface['name'] = None
            interface['dns1'] = None
            interface['dns2'] = None
            interface['ip'] = None
            interface['mask'] = None
            interfaces.append(interface) 
            #for allocated_interface in allocated_vm.interfaces:
            #        interface = dict()
            #        interface['gw'] = allocated_interface.gw
            #        interface['mac'] = allocated_interface.mac
            #        interface['name'] = allocated_interface.name
            #        interface['dns1'] = allocated_interface.dns1
            #        interface['dns2'] = allocated_interface.dns2
            #        interface['ip'] = allocated_interface.ip
            #        interface['mask'] = allocated_interface.mask
            #        interfaces.append(interface)
            params['interfaces'] = interfaces
            if not project:
                project = params['project-id']
            if not server.uuid in servers:
                servers.append(server.uuid)
                new_server = dict()
                new_server['component_id'] = server.uuid 
                new_server['slivers'] = list()
                new_server['slivers'].append(params)
                vms_params.append(new_server)
            else:
                for vm_server in vms_params:
                    if vm_server['component_id'] is server.uuid:
                        vm_server['slivers'].append(params)
        if vms_params:
            created_vms = self._provision_vms(vms_params, slice_urn, project)
        else:
            raise virt_exception.VTAMNoSliversInSlice(slice_urn)
        for key in created_vms.keys():
            for created_vm in created_vms[key]:
                vm_hrn, hrn_type = urn_to_hrn(created_vm['name'])
                vm_name = get_leaf(vm_hrn)
                slice_name = get_leaf(get_authority(vm_hrn))
                vm = VMAllocated.query.filter_by(name=vm_name).filter_by(slice_name=slice_name).first()
                current_vm = VirtualMachine.query.filter_by(name=vm_name).filter_by(slice_name=slice_name).first().get_child_object()
                time.sleep(10)
                #XXX: Very ugly, improve this
                if not current_vm:
                    time.sleep(10)
                    current_vm = VirtualMachine.query.filter_by(name=vm_name).filter_by(slice_name=slice_name).first().get_child_object()
                if current_vm:
                    db.session.delete(vm)
                    db.session.commit()
                    vm_expiration = Expiration()
                    vm_expiration.expiration = end_time
                    vm_expiration.vm_id = current_vm.id
                    created_vm['expiration'] = end_time 
                    db.session.add(vm_expiration)
                    db.session.commit()
                else:
                    created_vm['expiration'] = vm.expiration
                    created_vm['error'] = 'VM cannot be created'
        return created_vms
        
    def _provision_vms(self, vm_params, slice_urn, project_name):
        """
        Provision (create) VMs.
        """
        created_vms = list()
        slice_hrn, urn_type = urn_to_hrn(slice_urn)
        slice_name = get_leaf(slice_hrn)
        provisioning_rspecs, actions = VMManager.get_action_instance(vm_params,project_name,slice_name)
        vm_results = dict()
        for provisioning_rspec, action in zip(provisioning_rspecs, actions):
            ServiceThread.start_method_in_new_thread(ProvisioningDispatcher.process, provisioning_rspec, 'SFA.OCF.VTM')
            vm = provisioning_rspec.action[0].server.virtual_machines[0]
            vm_hrn = 'geni.gpo.gcf.' + vm.slice_name + '.' + vm.name
            vm_urn = hrn_to_urn(vm_hrn, 'sliver')
            server = VTDriver.get_server_by_uuid(vm.server_id)
            if server.name not in vm_results.keys():
                vm_results[server.name] = list()
            vm_results[server.name].append({'name':vm_urn, 'status':'ongoing'})
        return vm_results
    
    # VM status methods
    def start_vm(self, vm_urn):
        vm_hrn, type = urn_to_hrn(vm_urn)
        vm_name = get_leaf(vm_hrn)
        slice_name = get_leaf(get_authority(vm_hrn))
        vm = VirtualMachine.query.filter_by(name=vm_name).filter_by(slice_name=slice_name).first().get_child_object()
        expiration = Expiration.query.get(vm.id).expiration
        vm_id = vm.id
        status = vm.status
        #FIXME: This should not be done that way
        xen_vm = db_session.query(XenVM).filter(XenVM.virtualmachine_ptr_id == vm_id).first()
        server = xen_vm.xenserver_associations
        server_uuid = server.uuid
        db_session.expunge_all()
        try:
            VTDriver.propagate_action_to_provisioning_dispatcher(vm_id, server_uuid, Action.PROVISIONING_VM_START_TYPE)
            return {'name':vm_urn, 'status':status, 'expiration':expiration}
        except Exception as e:
            return {'name':vm_urn, 'status':status, 'expiration':expiration, 'error': 'Could not start the VM'}
    
    def pause_vm(self, vm_urn):
        """
        Stores VM status in memory.
        Xen: xm pause <my_vm>
        See http://stackoverflow.com/questions/11438922/how-does-xen-pause-a-vm
        """
        pass
    
    def stop_vm(self, vm_urn=None, vm_name=None, slice_name=None):
        if vm_urn and not (vm_name and slice_name):
            vm_hrn, type = urn_to_hrn(vm_urn)
            vm_name = get_leaf(vm_hrn)
            slice_name = get_leaf(get_authority(vm_hrn))
            vm = VirtualMachine.query.filter_by(name=vm_name).filter_by(slice_name=slice_name).one().get_child_object()
            expiration = Expiration.query.get(vm.id).one().expiration
        try:
            VTDriver.propagate_action_to_provisioning_dispatcher(vm.id, vm.xenserver.uuid, Action.PROVISIONING_VM_STOP_TYPE)
            return {'name':vm_urn, 'status':vm.status, 'expiration':expiration}
        except Exception as e:
            return {'name':vm_urn, 'status':vm.status, 'expiration':expiration, 'error': 'Could not stop the VM'}
    
    def restart_vm(self, vm_urn):
        vm_hrn, type = urn_to_hrn(vm_urn)
        vm_name = get_leaf(vm_hrn)
        slice_name = get_leaf(get_authority(vm_hrn))
        vm = VirtualMachine.query.filter_by(name=vm_name).filter_by(slice_name=slice_name).one().get_child_object()
        expiration = Expiration.query.get(vm.id).one().expiration
        try:
            VTDriver.propagate_action_to_provisioning_dispatcher(vm.id, vm.xenserver.uuid, Action.PROVISIONING_VM_REBOOT_TYPE)
            return {'name':vm_urn, 'status':vm.status, 'expiration':expiration}
        except Exception as e:
            return {'name':vm_urn, 'status':vm.status, 'expiration':expiration, 'error': 'Could not Restart the VM'}
    
    def delete_vm(self, vm_urn, slice_name=None):
        vm_hrn, hrn_type = urn_to_hrn(vm_urn)
        if not slice_name:
            slice_name = get_leaf(get_authority(vm_hrn))
        vm_name = get_leaf(vm_hrn)
        vm = db_session.query(VirtualMachine).filter(VirtualMachine.name == vm_name).filter(VirtualMachine.slice_name == slice_name).first()
        if vm != None:
             db_session.expunge(vm)
             deleted_vm = self._destroy_vm_with_expiration(vm.id)
        else:
             vm = db_session.query(VMAllocated).filter(VMAllocated.name == vm_name).first()
             if vm != None:
                db_session.expunge(vm)
                deleted_vm = self._unallocate_vm(vm.id)
                if not deleted_vm:
                    deleted_vm = dict()
                    deleted_vm = dict()
                    deleted_vm['name'] = vm_urn
                    deleted_vm['expiration'] = None
                    deleted_vm['error'] = "The requested VM does not exist, it may have expired"
             else:
                deleted_vm = dict()
                deleted_vm['name'] = vm_urn
                deleted_vm['expiration'] = None
                deleted_vm['error'] = "The requested VM does not exist, it may have expired"
        return deleted_vm
    
    # Slice methods
    def add_vm_to_slice(self, slice_urn, vm_urn):
        """
        Add VM to slive with given URN.
        """
        pass
    
    def remove_vm_to_slice(self, slice_urn, vm_urn):
        """
        Remove VM from slive with given URN.
        """
        pass
    
    # XXX Check
    def start_vms_in_slice(self, slice_urn):
        slice_name = get_leaf(urn_to_hrn(slice_urn)[0])
        vms = db_session.query(VirtualMachine).filter(VirtualMachine.slice_name == slice_name).all()
        started_vms = list()
        for vm in vms:
            started_vms.append(self.start_vm(None, vm.name, vm.slice_name))
        db_session.expunge_all()
        return started_vms
    
    def stop_vms_in_slice(self, slice_urn):
        slice_name = get_leaf(urn_to_hrn(slice_urn)[0])
        vms = db_session.query(VirtualMachine).filter(VirtualMachine.slice_name == slice_name).all()
        stopped_vms = list()
        for vm in vms:
            stopped_vms.append(self.stop_vm(None, vm.name, vm.slice_name))
        db_session.expunge_all()
        return stopped_vms
    
    # XXX Check
    def restart_vms_in_slice(self, slice_urn):
        slice_name = get_leaf(urn_to_hrn(slice_urn)[0])
        vms = db_session.query(VirtualMachine).filter(VirtualMachine.slice_name == slice_name).all()
        restarted_vms = list()
        for vm in vms:
            restarted_vms.append(self.restart_vm(None, vm.name, vm.slice_name))
        db_session.expunge_all()
        return restarted_vms

    def delete_vm_by_uuid(self, vm_uuid):
        pass
    
    def delete_vms_in_slice(self, slice_urn):
        slice_hrn, hrn_type = urn_to_hrn(slice_urn)
        slice_name = get_leaf(slice_hrn)
        # get all the vms from the given slice and delete them
        vms = list()
        vms_created = db_session.query(VirtualMachine).filter(VirtualMachine.slice_name == slice_name).all()
        if vms_created:
            vms.extend(vms_created)
        vms_allocated = db_session.query(VMAllocated).filter(VMAllocated.slice_name == slice_name).all()
        if vms_allocated:
            vms.extend(vms_allocated)
        if not vms:
            raise virt_exception.VTAMNoVMsInSlice(slice_name)
        deleted_vms = list()        
        for vm in vms:
            vm_hrn = 'geni.gpo.gcf.' + slice_name + '.' + vm.name
            vm_urn = hrn_to_urn(vm_hrn, 'sliver')
            deleted_vm = self.delete_vm(vm_urn, slice_name)
            deleted_vms.append(deleted_vm)
        db_session.expunge_all()
        return deleted_vms
    
    # Allocation methods
    def allocate_vm(self, vm, end_time):
        """
        Allocate a VM in the given slice.
        """
        # Check if the VM name already exists, as a created VM or an allocated VM
        logging.debug("** delegate.vm: %s" % str(vm))
        logging.debug("** delegate.vm_name: %s" % str(vm["name"]))
        logging.debug("** delegate.slice_name: %s" % str(vm["slice_name"]))
        logging.debug("** delegate.project_name: %s" % str(vm["project_name"]))
        provisioned_vm = VirtualMachine.query.filter_by(name=vm["name"], slice_name=vm["slice_name"], project_name=vm["project_name"]).first()
        allocated_vm = VMAllocated.query.filter_by(name=vm["name"], slice_name=vm["slice_name"], project_name=vm["project_name"]).first()
        # If VM already exists either on allocated or in provisioned, return error
        if provisioned_vm or allocated_vm:
            raise virt_exception.VTAMVmNameAlreadyTaken(vm["name"])
        # Check if the server is one of the given servers
        try: 
            VTServer.query.filter_by(uuid=vm["server_uuid"]).one()
        except:
            raise virt_exception.VTAMServerNotFound(vm["server_uuid"])
        # Check if the expiration time is a valid time
        try:
            self.expiration_manager.check_valid_reservation_time(end_time)
        except:
            raise virt_exception.VTMaxVMDurationExceeded(end_time)
        # Try to obtain the Template definition
        try:
            template_info = vm.pop("template_definition")
        # Otherwhise we assume the "default" Template
        except:
            template_info = dict()
            template_info["template_name"] = "Default"
        # Check if the Template is a valid one and return it
        try:
            template = self.template_manager.get_template_by(template_info.values()[0])
        except:
            try: 
                template = self.template_manager.get_template_by(template_info)
            except Exception as e:
                raise e
        # Check if the project already exists
        vm_in_project = VirtualMachine.query.filter_by(project_name=vm["project_name"])
        allocated_vm_in_project = VMAllocated.query.filter_by(project_name=vm["project_name"])
        # If exists, assign the same UUID
        if vm_in_project.first() or allocated_vm_in_project.first():
            try:
                project_uuid = vm_in_project.first().get_project_id()
            except:
                project_uuid = allocated_vm_in_project.first().get_project_id()
            vm["project_id"] = project_uuid
            # Check if the slice already exists on this project
            vm_in_slice = vm_in_project.filter_by(slice_name=vm["slice_name"]).first()
            allocated_vm_in_slice = allocated_vm_in_project.filter_by(slice_name=vm["slice_name"]).first()
            # If exists, assign the same UUID
            if vm_in_slice or allocated_vm_in_slice:
                try:
                    slice_uuid = vm_in_slice.get_slice_id()
                except:
                    slice_uuid = allocated_vm_in_slice.get_slice_id()
                vm["slice_id"] = slice_uuid
            # Otherwhise, assign one randomly.
            else:
                vm["slice_id"] = uuid.uuid4()
        # Otherwhise, assign one randomly.
        # If the project did not exist previously, the slice will be new too.
        else:
            vm["project_id"] = uuid.uuid4()
            vm["slice_id"] = uuid.uuid4()
        # Create the VM URN and assign it to the VM
        vm_hrn = vm["project_name"] + '.' + vm["slice_name"] + '.' + vm["name"]
        vm_urn = hrn_to_urn(vm_hrn, "sliver")
        vm["urn"] = vm_urn
        # Once we know the VM can be created, we reserve
        vm_allocated_model = self.translator.dict2class(vm, VMAllocated)
        vm_allocated_model.save()
        # Add the expiration time to the allocated VM
        self.expiration_manager.add_expiration_to_vm_by_uuid(vm_allocated_model.get_uuid(), end_time)
        # Add the template to the allocated VM
        self.template_manager.add_template_to_allocated_vm(vm_allocated_model.get_uuid(), template)
        # Obtain the Allocated VM information
        vm_allocated_dict = self.get_vm(vm_allocated_model.get_uuid())
        return vm_allocated_dict
        
    def deallocate_vm_by_urn(self, vm_urn):
        pass

    def deallocate_vm_by_uuid(self, vm_uuid):
        vm = self.get_vm_obj(vm_uuid)
        try:
            deleted_vm = deallocate_vm(vm)
        except Exception as e:
            raise e
        return deleted_vm

    def deallocate_vm(self, vm):
        """
        Delete the entry in the table of allocated VMs.
        """
        deleted_vm = self.get_vm_info(vm)
        try:
            vm.destroy()
        except Exception as e:
            raise e
        return deleted_vm
    
    # Authority methods
    def get_vms_in_authority(self, authority_urn):
        """
        Get list of VMs in authority with given URN.
        """
        pass
    
    def get_allocated_vms_in_authority(self, authority_urn):
        """
        Get list of allocated (reserved) VMs in authority with given URN.
        """
        pass
    
    def get_provisioned_vms_in_authority(self, authority_urn):
        """
        Get list of provisioned (created) VMs in authority with given URN.
        """
        pass
    
    @worker.outsideprocess
    def check_vms_expiration(self, params):
        """
        Checks expiration for both allocated and provisioned VMs
        and deletes accordingly, either from DB or disk.
        """
        expired_vms = self.expiration_manager.get_expired_vms()
        for expired_vm in expired_vms:
            vm_uuid = expired_vm.get_uuid()
            self.delete_vm_by_uuid(vm_uuid)
            self.expiration_manager.delete_expiration_by_vm_uuid(vm_uuid)
        return
    
    # Backup & migration methods
    # XXX Do not implement right now
    def copy_vm_to_slice(self, slice_urn, vm_urn):
        pass
    
    def move_vm_to_slice(self, slice_urn, vm_urn):
        pass
    
    def copy_vm_to_server(self, server_urn, vm_urn):
        pass
    
    def move_vm_to_server(self, server_urn, vm_urn):
        pass
    
    def update_template_to_server(self, server_urn, template_path):
        pass
    
    def get_vm_snapshot(self, server_urn, template_name):
        pass

