import time
import amsoil.core.pluginmanager as pm

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from datetime import datetime, timedelta

from interfaces.servernetworkinterfaces import VTServerNetworkInterfaces
from interfaces.networkinterface import NetworkInterface
from interfaces.vmallocatednetworkinterfaces import VMAllocatedNetworkInterfaces

from resources.vtserver import VTServer
from resources.virtualmachine import VirtualMachine
from resources.vmexpires import VMExpires
from resources.vmallocated import VMAllocated

from ranges.serveriprange import VTServerIpRange
from ranges.servermacrange import VTServerMacRange
from ranges.ip4range import Ip4Range
from ranges.macrange import MacRange

import utils.vtexceptions as vt_exception
from utils.xrn import hrn_to_urn, urn_to_hrn, get_leaf, get_authority
from utils.action import Action
from utils.vmmanager import VMManager
from utils.servicethread import ServiceThread

from controller.dispatchers.provisioningdispatcher import ProvisioningDispatcher
from controller.drivers.vtdriver import VTDriver



'''@author: SergioVidiella'''

class VTResourceManager(object):
    config = pm.getService("config")
    worker = pm.getService('worker')

    RESERVATION_TIMEOUT = config.get("vtam.max_reservation_duration") # sec in the allocated state
    MAX_VM_DURATION = config.get("vtam.max_vm_duration") # sec in the provisioned state (you can always call renew)

    EXPIRY_ALLOCATED_CHECK_INTERVAL = config.get("vtam.allocated_vm_check_interval") 
    EXPIRY_CHECK_INTERVAL = config.get("vtam.created_vm_check_interval")

    def __init__(self):
	super(VTResourceManager, self).__init__()
        # register callback for regular updates
        self.worker.addAsReccurring("vtresourcemanager", "expire_vm", None, self.EXPIRY_CHECK_INTERVAL)
        self.worker.addAsReccurring("vtresourcemanager", "expire_allocated_vm", None, self.EXPIRY_ALLOCATED_CHECK_INTERVAL)


    def get_servers(self, uuid=None):
        servers = db_session.query(VTServer).all()
        if uuid:
            for server in servers:
                if str(server.uuid) == str(uuid):
                    db_session.expunge_all()
                    return server
            db_session.expunge_all()
            return None
        else:
            return servers


    def vms_in_slice(self, slice_urn):
	vms = list()
	vms_created = self._vms_created_in_slice(slice_urn)
	if vms_created:
	    vms.extend(vms_created)
	vms_reserved = self._vms_reserved_in_slice(slice_urn)
	if vms_reserved:
	    vms.extend(vms_reserved)
	return vms


    def _vms_created_in_slice(self, slice_urn):
	slice_hrn, hrn_type = urn_to_hrn(slice_urn)
	slice_name = get_leaf(slice_hrn)
	vms = db_session.query(VirtualMachine).filter(VirtualMachine.sliceName == slice_name).all()
	if vms:
	    vms_created = list()
	    for vm in vms:
		vm_expires = db_session.query(VMExpires).filter(VMExpires.vm_id == vm.id).first()
		vm_hrn = 'geni.gpo.gcf.' + vm.sliceName + '.' + vm.name
                vm_urn = hrn_to_urn(vm_hrn, 'sliver')
		vms_created.append({'name':vm_urn, 'status':vm.status, 'expires':vm_expires.expires})
	    db_session.expunge_all()
	    return vms_created
	else:
	    db_session.expunge_all()
	    return None


    def _vms_reserved_in_slice(self, slice_urn):
	slice_hrn, hrn_type = urn_to_hrn(slice_urn)
        slice_name = get_leaf(slice_hrn)
	vms = db_session.query(VMAllocated).filter(VMAllocated.sliceName == slice_name).all()
	if vms:
            vms_created = list()
            for vm in vms:
		vm_hrn = 'geni.gpo.gcf.' + vm.sliceName + '.' + vm.name
                vm_urn = hrn_to_urn(vm_hrn, 'sliver')
                vms_created.append({'name':vm_urn, 'expires':vm.expires, 'status':"allocated"})
            db_session.expunge_all()
            return vms_created
        else:
            db_session.expunge_all()
            return None


    def verify_vm(self, vm_urn):
	vm_hrn, hrn_type = urn_to_hrn(vm_urn)
        vm_name = get_leaf(vm_hrn)
        vm = db_session.query(VMAllocated).filter(VMAllocated.name == vm_name).first()
	db_session.expunge(vm)
	if vm:
	    return vm_name, "allocated"
	else:
	    vm = db_session.query(VirtualMachine).filter(VirtualMachine.name == vm_name).first()
	    db_session.expunge(vm)
	    if vm:
		return vm_name, "provisioned"
	    else:
		raise vt_exception.VTAMVMNotFound(vm_urn)
	

    def extend_vm_expiration(self, vm_urn, status, expiration_time):
	vm_hrn, hrn_type = urn_to_hrn(vm_urn)
        vm_name = get_leaf(vm_hrn)
	max_duration = self.RESERVATION_TIMEOUT
        max_end_time = datetime.utcnow() + timedelta(0, max_duration)
	if (status == "allocated"):
	    vm_expires = db_session.query(VMAllocated).filter(VMAllocated.name == vm_name).first()
	    vm_state = "allocated"
	else:
	    vm = db_session.query(VirtualMachine).filter(VirtualMachine.name == vm_name).first()
	    vm_state = vm.state
	    db_session.expunge(vm)
	    vm_expires = db_session.query(VMExpires).filter(VMExpires.vm_id == vm.id).first()
	if (expiration_time > max_end_time):
	    db_sesion.expunge_all()
            raise VTMaxVMDurationExceeded(vm_name, vm_expires.expires)
	last_expiration = vm_expires.expires
        vm_expires.expires = expiration_time
        vm_hrn = 'geni.gpo.gcf.' + vm.sliceName + '.' + vm.name
        vm_urn = hrn_to_urn(vm_hrn, 'sliver')
        db_session.add(vm_expires)
        db_session.commit()
	db_session.expunge(vm_expires)
        return {'name':vm_urn, 'expires':expiration_time, 'status':vm_state}, last_expiration


    def reserve_vms(self, vms, slice_urn, end_time):
	slice_hrn, hrn_type = urn_to_hrn(slice_urn)
        if hrn_type != 'slice' or slice_hrn == None:
            raise vt_exception.VTAMMalformedUrn(slice_urn)
        slice_name = get_leaf(slice_hrn)
	for vm in vms:
	    #check if the vm name already exists
	    if db_session.query(VirtualMachine).filter(VirtualMachine.name == vm['name']).filter(VirtualMachine.sliceName == slice_name).filter(VirtualMachine.projectId == vm['project_id']).first() != None or db_session.query(VMAllocated).filter(VMAllocated.name == vm['name']).filter(VMAllocated.sliceName == slice_name).filter(VMAllocated.projectId == vm['project_id']).first() != None:
		raise vt_exception.VTAMVmNameAlreadyTaken(vm['name'])
	    #check if the server is one of the given servers
	    if db_session.query(VTServer).filter(VTServer.name == vm['server_name']).first() == None:
		raise vt_exception.VTAMServerNotFound(vm['server_name'])
	    db_session.expunge_all()
	max_duration = self.RESERVATION_TIMEOUT
	max_end_time = datetime.utcnow() + timedelta(0, max_duration)
        if end_time == None:
            end_time = max_end_time
        if (end_time > max_end_time):
            raise VTMaxVMDurationExceeded(vm_name)
	if (end_time < datetime.utcnow()):
	    end_time = max_end_time
	#once we know all the VMs could be created, we start reserving them
	servers = dict()
	for vm in vms:
	    server, vm_urn = self._allocate_vm(vm, slice_urn, slice_name, end_time)
	    vm_name, hrn_type = urn_to_hrn(vm['name'])
	    if servers.has_key(server):
	    	servers[server].append({'name':vm_urn, 'expires':end_time, 'status':'allocated'})
	    else:
		servers[server] = list()
		servers[server].append({'name':vm_urn, 'expires':end_time, 'status':'allocated'})
	return servers


    def delete_vms_in_slice(self, slice_urn):
	slice_hrn, urn_type = urn_to_hrn(slice_urn)
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
	    raise vt_exception.VTAMNoVMsInSlice(slice_name)
	deleted_vms = list()	
	for vm in vms:
	    vm_hrn = 'geni.gpo.gcf.' + slice_name + '.' + vm.name
	    vm_urn = hrn_to_urn(vm_hrn, 'sliver')
	    deleted_vm = self.delete_vm(vm_urn, get_leaf(urn_to_hrn(slice_urn)))
	    deleted_vms.append(deleted_vm)
	db_session.expunge_all()
	return deleted_vms


    def delete_vm(self, vm_urn, slice_name=None):
	vm_hrn, urn_type = urn_to_hrn(vm_urn)
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
		deleted_vm = self._unnallocate_vm(vm.id)
		if not deleted_vm:
		    deleted_vm = dict()
		    deleted_vm = dict()
                    deleted_vm['name'] = vm_urn
                    deleted_vm['expires'] = None
                    deleted_vm['error'] = "The requested VM doesn't exists, it may have expired"
	     else:
		deleted_vm = dict()
		deleted_vm['name'] = vm_urn
		deleted_vm['expires'] = None
		deleted_vm['error'] = "The requested VM doesn't exists, it may have expired"
	return deleted_vm


    def _unnallocate_vm(self, vm_id):
	#Delete the entry in the table of allocated vm's
	vm = db_session.query(VMAllocated).filter(VMAllocated.id == vm_id).first()
	deleted_vm = dict()
	deleted_vm['name'] = vm.name
	deleted_vm['expires'] = vm.expires
	db_session.delete(vm)
	db_session.commit()
	db_session.expunge(vm)
	return deleted_vm	


    def _destroy_vm_with_expiration(self, vm_id):
	vm_expires = db_session.query(VMExpires).filter(VMExpires.vm_id == vm_id).first()
	if vm_expires != None:
	    db_session.delete(vm_expires)
	    db_session.commit()
	    db_session.expunge(vm_expires)
	    vm = db_session.query(XenVM).filter(XenVM.virtualmachine_ptr_id == vm_id).first()
	    server = vm.xenserver_associations
	    server_uuid = server.uuid
	    db_session.expunge(vm)
	    deleted_vm = self._destroy_vm(vm_id, server_uuid)
	    return deleted_vm
	else:
	    return None



    def _destroy_vm(self, vm_id, server_uuid):
	try:
            VTDriver.PropagateActionToProvisioningDispatcher(vm_id, server_uuid, Action.PROVISIONING_VM_DELETE_TYPE)
	    return "success"
        except Exception as e:
            return "error" 
    

    def _allocate_vm(self, requested_vm, slice_urn, slice_name, end_time):
	vm = VMAllocated()
	vm.name = requested_vm['name']
	vm.memory = int(requested_vm['memory_mb'])
	vm.discSpaceGB = float(requested_vm['hd_size_mb'])/1024
	vm.projectId = requested_vm['project_id']
	vm.sliceId = slice_urn
	vm.sliceName = slice_name
	vm.operatingSystemType = requested_vm['operating_system_type'] 
	vm.operatingSystemVersion = requested_vm['operating_system_version']
	vm.operatingSystemDistribution = requested_vm['operating_system_distribution']
	vm.hypervisor = requested_vm['hypervisor']
	vm.hdSetupType = requested_vm['hd_setup_type']
        vm.hdOriginPath = requested_vm['hd_origin_path']
        vm.virtualizationSetupType = requested_vm['virtualization_setup_type']
	vm.expires = end_time
 
        server = db_session.query(VTServer).filter(VTServer.name == requested_vm['server_name']).first()
        vm.serverId = server.id

	db_session.add(vm)
	db_session.commit()
	
	for interface in requested_vm['interfaces']:
	    allocated_interface = VMAllocatedNetworkInterfaces()
	    allocated_interface.allocated_vm_id = vm.id
	    allocated_interface.name = interface['name']
	    allocated_interface.mac = interface['mac']
	    allocated_interface.ip = interface['ip']
	    allocated_interface.gw = interface['gw']
	    allocated_interface.dns1 = interface['dns1']
	    allocated_interface.dns2 = interface['dns2']
	    allocated_interface.msk = interface['mask']
	    allocated_interface.isMgmt = interface['ismgmt']
	    db_session.add(allocated_interface)
	    db_session.commit()
	    db_session.expunge(allocated_interface)
	db_session.expunge(vm)

	vm_hrn = 'geni.gpo.gcf.' + vm.sliceName + '.' + vm.name
	vm_urn = hrn_to_urn(vm_hrn, 'sliver')

	return server.name, vm_urn


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
	allocated_vms = db_session.query(VMAllocated).filter(VMAllocated.sliceId == slice_urn).all()	
	vms_params = list()
	servers = list()
	project = None
	for allocated_vm in allocated_vms:
	    server = db_session.query(VTServer).filter(VTServer.id == allocated_vm.serverId).first()
	    params = dict()
	    params['name'] = allocated_vm.name
            params['uuid'] = uuid.uuid4()
            params['state'] = "creating"
            params['project-id'] = allocated_vm.projectId
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
	    interfaces = list()
	    for allocated_interface in allocated_vm.interfaces:
	    	interface = dict()
	    	interface['gw'] = allocated_interface.gw
            	interface['mac'] = allocated_interface.mac
            	interface['name'] = allocated_interface.name
            	interface['dns1'] = allocated_interface.dns1
            	interface['dns2'] = allocated_interface.dns2
            	interface['ip'] = allocated_interface.ip
            	interface['mask'] = allocated_interface.mask
	    	interfaces.append(interface)
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
	    raise vt_exception.VTAMNoSliversInSlice(slice_urn)
	for key in created_vms.keys():
	    for created_vm in created_vms[key]:
	    	vm_hrn, urn_type = urn_to_hrn(created_vm['name'])
	    	vm_name = get_leaf(vm_hrn)
	    	slice_name = get_leaf(get_authority(vm_hrn))
	    	vm = db_session.query(VMAllocated).filter(VMAllocated.name == vm_name).filter(VMAllocated.sliceName == slice_name).first()
	    	db_session.delete(vm)
	    	db_session.commit()
	    	vm_expires = VMExpires()
	    	vm_expires.expires = end_time
	    	created_vm['expires'] = end_time 
		db_session.expunge_all()
	return created_vms
	

    def _create_vms(self, vm_params, slice_urn, project_name):
	created_vms = list()
	slice_hrn, urn_type = urn_to_hrn(slice_urn)
        slice_name = get_leaf(slice_hrn)
	provisioningRSpecs, actions = VMManager.getActionInstance(vm_params,project_name,slice_name)
	vm_results = dict()
        for provisioningRSpec, action in zip(provisioningRSpecs, actions):
	    ServiceThread.startMethodInNewThread(ProvisioningDispatcher.processProvisioning,provisioningRSpec,'SFA.OCF.VTM')
	    vm = provisioningRSpec.action[0].server.virtual_machines[0]
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
            VTDriver.PropagateActionToProvisioningDispatcher(vm_id, server_uuid, Action.PROVISIONING_VM_START_TYPE)
            return {'name':vm_urn, 'status':status, 'expires':expiration}
        except Exception as e:
            return {'name':vm_urn, 'status':status, 'expires':expiration, 'error': 'Could not Start the VM'}


    def stop_vm(self, vm_urn=None, vm_name=None, slice_name=None):
	if vm_urn:
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
            VTDriver.PropagateActionToProvisioningDispatcher(vm_id, server_uuid, Action.PROVISIONING_VM_STOP_TYPE)
            return {'name':vm_urn, 'status':status, 'expires':expiration}
        except Exception as e:
            return {'name':vm_urn, 'status':status, 'expires':expiration, 'error': 'Could not Stop the VM'}

   
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
            VTDriver.PropagateActionToProvisioningDispatcher(vm_id, server_uuid, Action.PROVISIONING_VM_REBOOT_TYPE)
            return {'name':vm_urn, 'status':status, 'expires':expiration}
        except Exception as e:
            return {'name':vm_urn, 'status':status, 'expires':expiration, 'error': 'Could not Restart the VM'}


    def emergency_stop(self, slice_urn):	
	slice_name = get_leaf(urn_to_hrn(slice_urn)[0])
	vms = db_session.query(VirtualMachine).filter(VirtualMachine.sliceName == slice_name).all()
	stopped_vms = list()
	for vm in vms:
	    stopped_vms.append(self.stop_vm(None, vm.name, vm.sliceName))
	db_session.expunge_all()
	return stopped_vms


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
	     self._unnallocate_vm(vm.id)
	db_session.expunge_all()
	return


# ----------------------------------------------------
# ------------------ database stuff ------------------
# ----------------------------------------------------
from sqlalchemy import DateTime, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import exists

# initialize sqlalchemy
VTAMDB_ENGINE = pm.getService('config').get('vtamrm.dbpath')

db_engine = create_engine(VTAMDB_ENGINE, pool_recycle=6000)
db_session_factory = sessionmaker(autoflush=True, bind=db_engine, expire_on_commit=False) # the class which can create sessions (factory pattern)
db_session = scoped_session(db_session_factory) # still a session creator, but it will create _one_ session per thread and delegate all method calls to it

