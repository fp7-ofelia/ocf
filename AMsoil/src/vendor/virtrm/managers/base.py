import time
import amsoil.core.pluginmanager as pm

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from datetime import datetime, timedelta

from resources.vtserver import VTServer
from resources.xenserver import XenServer
from resources.virtualmachine import VirtualMachine
from resources.vmexpires import VMExpires
from resources.vmallocated import VMAllocated

import utils.exceptions as virt_exception
from utils.xrn import *
from utils.action import Action
from utils.vmmanager import VMManager
from utils.servicethread import ServiceThread
from utils.commonbase import db_session

from controller.dispatchers.provisioning.query import ProvisioningDispatcher
from controller.drivers.virt import VTDriver

import amsoil.core.log

logging=amsoil.core.log.getLogger('VTResourceManager')

'''@author: SergioVidiella'''

class VTResourceManager(object):
    config = pm.getService("config")
    worker = pm.getService('worker')
    # FIXME or REMOVE: circular dependency
    #virtrm = pm.getService("virtrm")
    #from virtrm.controller.drivers.virt import VTDriver

    RESERVATION_TIMEOUT = config.get("virtrm.MAX_RESERVATION_DURATION") # sec in the allocated state
    MAX_VM_DURATION = config.get("virtrm.MAX_VM_DURATION") # sec in the provisioned state (you can always call renew)

    EXPIRY_ALLOCATED_CHECK_INTERVAL = config.get("virtrm.ALLOCATED_VM_CHECK_INTERVAL") 
    EXPIRY_CHECK_INTERVAL = config.get("virtrm.CREATED_VM_CHECK_INTERVAL")

    def __init__(self):
        super(VTResourceManager, self).__init__()
        # Register callback for regular updates
        # FIXME: set workers back
        #self.worker.addAsReccurring("virtrm", "expire_vm", None, self.EXPIRY_CHECK_INTERVAL)
        #self.worker.addAsReccurring("virtrm", "expire_allocated_vm", None, self.EXPIRY_ALLOCATED_CHECK_INTERVAL)

    # Server functions
    def get_servers(self, uuid=None):
        """
            Get server by uuid. 
            If no uuid provided, return all servers.
        """
        servers = VTDriver.get_all_servers()
        logging.debug("**************************************" + str(servers))
        if uuid:
            for server in servers:
                if str(server.uuid) == str(uuid):
                    return server
            return None
        else:
            return servers
    
    # VM functions
    def get_vm_status(self, vm_urn, slice_name=None, project_name=None, allocation_status=False, operational_status=False, server_name=False, expiration_time=False):
        """
            Verify if the VM exists and return the status with the required params.
        """
        vm_hrn, hrn_type = urn_to_hrn(vm_urn)
        vm_name = get_leaf(vm_hrn)
        vm_status = dict()
        vm_status['name'] = vm_urn
        if not slice_name:
            slice_name = get_leaf(get_authority(vm_hrn))
        if not project_name:
            project_name = get_leaf(get_authority(get_authority(vm_hrn)))
        vm = db_session.query(VMAllocated).filter(VMAllocated.name == vm_name).filter(VMAllocated.sliceName == slice_name).filter(VMAllocated.projectName == project_name).first()
        if vm:
            server = db_session.query(VTServer).filter(VTServer.id == vm.serverId).first()
            db_session.expunge(vm)
            if allocation_status:
                vm_status['allocation_status'] = "allocated"
            if expiration_time:
                vm_status['expires'] = vm.expires
            if server_name:
                vm_status['server'] = server.name
            db_session.expunge(server)
        else:
            vm = db_session.query(VirtualMachine).filter(VirtualMachine.name == vm_name).filter(VirtualMachine.sliceName == slice_name).filter(VirutalMachine.projectName == project_name).first().getChildObject()
            if vm:
                server = vm.xenserver
                vm_expies = db_session.query(VMExpires).filter(VMExpires.vm_id == vm.id).first()
                if server_name:
                    vm_status['server'] = server.name
                if allocation_status:
                    vm_status['allocation_status'] = "provisioned"
                if operational_status:
                    vm_status['operational_status'] = vm.status
                if expiration_time and vm_expires:
                    vm_status['expires'] = vm_expires.expires
                db_session.expunge(vm)
                db_session.expunge(vm_expires)
            else:
                raise virt_exception.VTAMVMNotFound(urn)
        return vm_status

    def get_vms_in_slice(self, slice_urn):
        """
            Get all VMs in slice.
        """
        vms = list()
        vms_created = self._get_vms_created_in_slice(slice_urn)
        if vms_created:
            vms.extend(vms_created)
        vms_reserved = self._get_vms_reserved_in_slice(slice_urn)
        if vms_reserved:
            vms.extend(vms_reserved)
        return vms

    def _get_vms_created_in_slice(self, slice_urn):
        """
            Get all VMs created in a given slice.
        """
        slice_hrn, hrn_type = urn_to_hrn(slice_urn)
        slice_name = get_leaf(slice_hrn)
        project_name = get_leaf(get_authority(slice_hrn))
        vms = db_session.query(VirtualMachine).filter(VirtualMachine.sliceName == slice_name).filter(VirtualMachine.projectName == project_name).all()
        if vms:
            vms_created = list()
            for vm in vms:
                vm_expires = db_session.query(VMExpires).filter(VMExpires.vm_id == vm.id).first()
                vm_hrn = get_authority(get_authority(slice_urn)) + '.' + vm.projectName + '.' + vm.sliceName + '.' + vm.name
                vm_urn = hrn_to_urn(vm_hrn, 'sliver')
                vms_created.append({'name':vm_urn, 'status':vm.status, 'expires':vm_expires.expires})
            db_session.expunge_all()
            return vms_created
        else:
            db_session.expunge_all()
            return None

    def _get_vms_reserved_in_slice(self, slice_urn):
        """
            Get all VMs allocated in a given slice.
        """
        slice_hrn, hrn_type = urn_to_hrn(slice_urn)
        slice_name = get_leaf(slice_hrn)
        project_name = get_leaf(get_authority(slice_hrn))
        vms = db_session.query(VMAllocated).filter(VMAllocated.sliceName == slice_name).filter(VMAllocated.projectName == project_name).all()
        if vms:
            vms_created = list()
            for vm in vms:
                vm_hrn = get_authority(get_authority(slice_hrn)) + '.' + vm.projectName + '.' + vm.sliceName + '.' + vm.name
                vm_urn = hrn_to_urn(vm_hrn, 'sliver')
                vms_created.append({'name':vm_urn, 'expires':vm.expires, 'status':"allocated"})
            db_session.expunge_all()
            return vms_created
        else:
            db_session.expunge_all()
            return None
    
    def allocate_vm(self, vm, slice_name, end_time):
        """
            Allocate a VM in the given slice.
        """
        # Check if the VM name already exists, as a created VM or an allocated VM
        if db_session.query(VirtualMachine).filter(VirtualMachine.name == vm['name']).filter(VirtualMachine.sliceName == slice_name).filter(VirtualMachine.projectName == vm['project_name']).first() != None or db_session.query(VMAllocated).filter(VMAllocated.name == vm['name']).filter(VMAllocated.sliceName == slice_name).filter(VMAllocated.projectName == vm['project_name']).first() != None:
            raise virt_exception.VTAMVmNameAlreadyTaken(vm['name'])
        # Check if the server is one of the given servers
        if db_session.query(VTServer).filter(VTServer.name == vm['server_name']).first() == None:
            raise virt_exception.VTAMServerNotFound(vm['server_name'])
        try:
            expiration_time = self._check_reservation_time(end_time)
        except Exception as e:
            raise e
        # Once we know all the VMs could be created, we start reserving them
        vmAllocatedModel = self._vm_dict_to_class(vm, slice_name, expiration_time)
        db_session.add(vmAllocatedModel)
        db_session.commit()
        server = VTDriver.get_server_by_id(vmAllocatedModel.serverId)
        return vmAllocatedModel, server
        
    #XXX: continue from this point
    def extend_vm_expiration(self, vm_urn, status, expiration_time):
        vm_hrn, hrn_type = urn_to_hrn(vm_urn)
        vm_name = get_leaf(vm_hrn)
        slice_name = get_leaf(get_authority(vm_hrn))
        project_name = get_leaf(get_authority(get_authority(vm_hrn)))
        max_duration = self.RESERVATION_TIMEOUT
        max_end_time = datetime.utcnow() + timedelta(0, max_duration)
        if (status == "allocated"):
            vm_expires = db_session.query(VMAllocated).filter(VMAllocated.sliceName == slice_name).filter(VMAllocated.name == vm_name).filter(VMAllocated.projectName == project_name).one()
            vm_state = "allocated"
        else:
            vm = db_session.query(VirtualMachine).filter(VirtualMachine.sliceName == slice_name).filter(VirtualMachine.name == vm_name).filter(VirtualMachine.projectName == project_name).one()
            vm_state = vm.state
            db_session.expunge(vm)
            vm_expires = db_session.query(VMExpires).filter(VMExpires.vm_id == vm.id).first()
        if (expiration_time > max_end_time):
            db_sesion.expunge_all()
            raise VTMaxVMDurationExceeded(vm_name, vm_expires.expires)
        last_expiration = vm_expires.expires
        vm_expires.expires = expiration_time
        vm_hrn = get_leaf(get_authority(get_authority(get_authority(vm_hrn)))) + '.' + vm.projectName + '.' + vm.sliceName + '.' + vm.name
        vm_urn = hrn_to_urn(vm_hrn, 'sliver')
        db_session.add(vm_expires)
        db_session.commit()
        db_session.expunge(vm_expires)
        return {'name':vm_urn, 'expires':expiration_time, 'status':vm_state}, last_expiration
    
    def _unallocate_vm(self, vm_id):
        """
            Delete the entry in the table of allocated VMs.
        """
        vm = db_session.query(VMAllocated).filter(VMAllocated.id == vm_id).first()
        deleted_vm = dict()
        deleted_vm['name'] = vm.name
        deleted_vm['expires'] = vm.expires
        db_session.delete(vm)
        db_session.commit()
        db_session.expunge(vm)
        return deleted_vm
    
    def _destroy_vm(self, vm_id, server_uuid):
        if not server_uuid:
            server_uuid = XenDriver.get_server_uuid_by_vm_id(vm_id)
        try:
            VTDriver.propagate_action_to_provisioning_dispatcher(vm_id, server_uuid, Action.PROVISIONING_VM_DELETE_TYPE)
            return "success"
        except Exception as e:
            return "error" 
    
    def _destroy_vm_with_expiration(self, vm_id, server_uuid=None):
        vm_expires = db_session.query(VMExpires).filter(VMExpires.vm_id == vm_id).first()
        if vm_expires != None:
            db_session.delete(vm_expires)
            db_session.commit()
            db_session.expunge(vm_expires)
            if not server_uuid:
                server_uuid = XenDriver.get_server_uuid_by_vm_id(vm_id)
            deleted_vm = self._destroy_vm(vm_id, server_uuid)
            return deleted_vm
        else:
            return None
    
    def _vm_dict_to_class(self, requested_vm, slice_name, end_time):
        vm = VMAllocated()
        vm.name = requested_vm['name']
        vm.memory = int(requested_vm['memory_mb'])
        vm.discSpaceGB = float(requested_vm['hd_size_mb'])/1024
        vm.projectName = requested_vm['project_name']
        vm.sliceId = 0 #necessary?
        vm.sliceName = slice_name
        vm.operatingSystemType = requested_vm['operating_system_type'] 
        vm.operatingSystemVersion = requested_vm['operating_system_version']
        vm.operatingSystemDistribution = requested_vm['operating_system_distribution']
        vm.hypervisor = requested_vm['hypervisor']
        vm.hdSetupType = requested_vm['hd_setup_type']
        vm.hdOriginPath = requested_vm['hd_origin_path']
        vm.virtualizationSetupType = requested_vm['virtualization_setup_type']
        vm.expires = end_time 
        vm.serverId = db_session.query(VTServer).filter(VTServer.name == requested_vm['server_name']).first().id
        #XXX: Currently, allocating interfaces is not allowed        
#        for interface in requested_vm['interfaces']:
#            allocated_interface = VMAllocatedNetworkInterfaces()
#            allocated_interface.allocated_vm_id = vm.id
#            allocated_interface.name = interface['name']
#            allocated_interface.mac = interface['mac']
#            allocated_interface.ip = interface['ip']
#            allocated_interface.gw = interface['gw']
#            allocated_interface.dns1 = interface['dns1']
#            allocated_interface.dns2 = interface['dns2']
#            allocated_interface.msk = interface['mask']
#            allocated_interface.isMgmt = interface['ismgmt']
#            db_session.add(allocated_interface)
#            db_session.commit()
#            db_session.expunge(allocated_interface)
        return vm
    
    def create_allocated_vms(self, slice_urn, end_time):
        import uuid
        max_duration = self.RESERVATION_TIMEOUT
        max_end_time = datetime.utcnow() + timedelta(0, max_duration)
        if end_time == None:
            end_time = max_end_time
        if (end_time > max_end_time):
            raise VTMaxVMDurationExceeded(vm_name)
        if (end_time < datetime.utcnow()):
            end_time = max_end_time
        allocated_vms = db_session.query(VMAllocated).filter(VMAllocated.sliceName == get_leaf(slice_urn)).all()        
        vms_params = list()
        servers = list()
        project = None
        for allocated_vm in allocated_vms:
            server = db_session.query(VTServer).filter(VTServer.id == allocated_vm.serverId).first()
            params = dict()
            params['name'] = allocated_vm.name
            params['uuid'] = uuid.uuid4()
            params['state'] = "creating"
            params['project-id'] = None
            params['server-id'] = server.uuid
            params['slice-id'] = allocated_vm.sliceId
            params['slice-name'] = allocated_vm.sliceName
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

        db_session.expunge_all()
        if vms_params:
            created_vms = self._create_vms(vms_params, slice_urn, project)
        else:
            raise virt_exception.VTAMNoSliversInSlice(slice_urn)
        for key in created_vms.keys():
            for created_vm in created_vms[key]:
                vm_hrn, hrn_type = urn_to_hrn(created_vm['name'])
                vm_name = get_leaf(vm_hrn)
                slice_name = get_leaf(get_authority(vm_hrn))
                vm = db_session.query(VMAllocated).filter(VMAllocated.name == vm_name).filter(VMAllocated.sliceName == slice_name).first()
                current_vm = db_session.query(VirtualMachine).filter(VirtualMachine.name == vm_name).filter(VirtualMachine.sliceName == slice_name).first()
                time.sleep(10)
                #XXX: Very ugly, improve this
                if not current_vm:
                    time.sleep(10)
                    current_vm = db_session.query(VirtualMachine).filter(VirtualMachine.name == vm_name).filter(VirtualMachine.sliceName == slice_name).first()
                if current_vm:
                    db_session.delete(vm)
                    db_session.commit()
                    vm_expires = VMExpires()
                    vm_expires.expires = end_time
                    vm_expires.vm_id = current_vm.id
                    created_vm['expires'] = end_time 
                    db_session.add(vm_expires)
                    db_session.commit()
                else:
                    created_vm['expires'] = vm.expires
                    created_vm['error'] = 'VM cannot be created'
                db_session.expunge_all()
        return created_vms
        
    def _create_vms(self, vm_params, slice_urn, project_name):
        created_vms = list()
        slice_hrn, urn_type = urn_to_hrn(slice_urn)
        slice_name = get_leaf(slice_hrn)
        provisioning_rspecs, actions = VMManager.getActionInstance(vm_params,project_name,slice_name)
        vm_results = dict()
        for provisioning_rspec, action in zip(provisioning_rspecs, actions):
            ServiceThread.startMethodInNewThread(ProvisioningDispatcher.process, provisioning_rspec, 'SFA.OCF.VTM')
            vm = provisioning_rspec.action[0].server.virtual_machines[0]
            vm_hrn = 'geni.gpo.gcf.' + vm.slice_name + '.' + vm.name
            vm_urn = hrn_to_urn(vm_hrn, 'sliver')
            server = db_session.query(VTServer).filter(VTServer.uuid == vm.server_id).first()
            if server.name not in vm_results.keys():
                vm_results[server.name] = list()
            vm_results[server.name].append({'name':vm_urn, 'status':'ongoing'})
            db_session.expunge_all()
        return vm_results
    
    def start_vm(self, vm_urn):
        vm_hrn, type = urn_to_hrn(vm_urn)
        vm_name = get_leaf(vm_hrn)
        slice_name = get_leaf(get_authority(vm_hrn))
        vm = db_session.query(VirtualMachine).filter(VirtualMachine.name == vm_name).filter(VirtualMachine.sliceName == slice_name).first()
        expiration = db_session.query(VMExpires).filter(VMExpires.id == vm.id).first().expires
        vm_id = vm.id
        status = vm.status
        xen_vm = db_session.query(XenVM).filter(XenVM.virtualmachine_ptr_id == vm_id).first()
        server = xen_vm.xenserver_associations
        server_uuid = server.uuid
        db_session.expunge_all()
        try:
            VTDriver.propagate_action_to_provisioning_dispatcher(vm_id, server_uuid, Action.PROVISIONING_VM_START_TYPE)
            return {'name':vm_urn, 'status':status, 'expires':expiration}
        except Exception as e:
            return {'name':vm_urn, 'status':status, 'expires':expiration, 'error': 'Could not start the VM'}
    
    def stop_vm(self, vm_urn=None, vm_name=None, slice_name=None):
        if vm_urn and not (vm_name and slice_name):
            vm_hrn, type = urn_to_hrn(vm_urn)
            vm_name = get_leaf(vm_hrn)
            slice_name = get_leaf(get_authority(vm_hrn))
        vm = db_session.query(VirtualMachine).filter(VirtualMachine.name == vm_name).filter(VirtualMachine.sliceName == slice_name).first()
        vm = db_session.query(VirtualMachine).filter(VirtualMachine.name == vm_name).first()
        expiration = db_session.query(VMExpires).filter(VMExpires.id == vm.id).first().expires
        vm_id = vm.id
        status = vm.status
        xen_vm = db_session.query(XenVM).filter(XenVM.virtualmachine_ptr_id == vm_id).first()
        server = xen_vm.xenserver_associations
        server_uuid = server.uuid
        db_session.expunge_all()
        try:
            VTDriver.propagate_action_to_provisioning_dispatcher(vm_id, server_uuid, Action.PROVISIONING_VM_STOP_TYPE)
            return {'name':vm_urn, 'status':status, 'expires':expiration}
        except Exception as e:
            return {'name':vm_urn, 'status':status, 'expires':expiration, 'error': 'Could not stop the VM'}
    
    def restart_vm(self, vm_urn):
        vm_hrn, type = urn_to_hrn(vm_urn)
        vm_name = get_leaf(vm_hrn)
        slice_name = get_leaf(get_authority(vm_hrn))
        vm = db_session.query(VirtualMachine).filter(VirtualMachine.name == vm_name).filter(VirtualMachine.sliceName == slice_name).first()
        vm = db_session.query(VirtualMachine).filter(VirtualMachine.name == vm_name).first()
        expiration = db_session.query(VMExpires).filter(VMExpires.id == vm.id).first().expires
        vm_id = vm.id
        status = vm.status
        xen_vm = db_session.query(XenVM).filter(XenVM.virtualmachine_ptr_id == vm_id).first()
        server = xen_vm.xenserver_associations
        server_uuid = server.uuid
        db_session.expunge_all()
        try:
            VTDriver.propagate_action_to_provisioning_dispatcher(vm_id, server_uuid, Action.PROVISIONING_VM_REBOOT_TYPE)
            return {'name':vm_urn, 'status':status, 'expires':expiration}
        except Exception as e:
            return {'name':vm_urn, 'status':status, 'expires':expiration, 'error': 'Could not Restart the VM'}
    
    def delete_vm(self, vm_urn, slice_name=None):
        vm_hrn, hrn_type = urn_to_hrn(vm_urn)
        if not slice_name:
            slice_name = get_leaf(get_authority(vm_hrn))
        vm_name = get_leaf(vm_hrn)
        vm = db_session.query(VirtualMachine).filter(VirtualMachine.name == vm_name).filter(VirtualMachine.sliceName == slice_name).first()
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
                    deleted_vm['expires'] = None
                    deleted_vm['error'] = "The requested VM does not exist, it may have expired"
             else:
                deleted_vm = dict()
                deleted_vm['name'] = vm_urn
                deleted_vm['expires'] = None
                deleted_vm['error'] = "The requested VM does not exist, it may have expired"
        return deleted_vm
    
    def stop_vms_in_slice(self, slice_urn):        
        slice_name = get_leaf(urn_to_hrn(slice_urn)[0])
        vms = db_session.query(VirtualMachine).filter(VirtualMachine.sliceName == slice_name).all()
        stopped_vms = list()
        for vm in vms:
            stopped_vms.append(self.stop_vm(None, vm.name, vm.sliceName))
        db_session.expunge_all()
        return stopped_vms
    
    def delete_vms_in_slice(self, slice_urn):
        slice_hrn, hrn_type = urn_to_hrn(slice_urn)
        slice_name = get_leaf(slice_hrn)
        # get all the vms from the given slice and delete them
        vms = list()
        vms_created = db_session.query(VirtualMachine).filter(VirtualMachine.sliceName == slice_name).all()
        if vms_created:
            vms.extend(vms_created)
        vms_allocated = db_session.query(VMAllocated).filter(VMAllocated.sliceName == slice_name).all()
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
    
    def _check_reservation_time(self, end_time):
        max_duration = self.RESERVATION_TIMEOUT
        max_end_time = datetime.utcnow() + timedelta(0, max_duration)
        if end_time == None or end_time < datetime.utcnow():
            return max_end_time
        elif (end_time > max_end_time):
            raise VTMaxVMDurationExceeded(vm_name)
        else:
            return end_time
    
    @worker.outsideprocess
    def expire_vm(self, params):
        vms = db_session.query(VMExpires).filter(VMExpires.expires <= datetime.utcnow()).all()
        for vm in vms:
            self._destroy_vm_with_expiration(vm.vm_id)
        db_session.expunge_all()
        return

    @worker.outsideprocess
    def expire_allocated_vm(self, params):
        vms = db_session.query(VMAllocated).filter(VMAllocated.expires <= datetime.utcnow()).all()
        for vm in vms:
             db_session.expunge(vm)
             self._unallocate_vm(vm.id)
        db_session.expunge_all()
        return
