import amsoil.core.pluginmanager as pm

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from datetime import datetime, timedelta

from interfaces.servernetworkinterfaces import VTServerNetworkInterfaces
from interfaces.networkinterface import NetworkInterface

from resources.server import VTServer
from resources.vm import VirtualMachine
from resources.vmexpires import VMExpires
from resources.vmallocated import VMAllocated

from ranges.serveriprange import VTServerIpRange
from ranges.servermacrange import VTServerMacRange
from ranges.ip4range import Ip4Range
from ranges.macrange import MacRange

import utils.vtexceptions as vt_exception
from utils.xrn import hrn_to_urn, urn_to_hrn, get_leaf, get_authority


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

    def GetNodes(self,slice=None,authority=None,uuid=None):
	servers = db_session.query(VTServer).all()
        if uuid:
            for server in servers:
                if str(server.uuid) == str(uuid):
		    db_session.expunge_all()
                    return server
	    db_session.expunge_all()
            return None
        else:    
	    db_session.expunge_all()
	    return servers


    def GetIpRange(self,vt_server_id):
	ip_range_ids = db_session.query(VTServerIpRange).filter(VTServerIpRange.vtserver_id == vt_server_id).all()
	if not ip_range_ids:
	    db_session.expunge_all()
	    return None
	ip_range = list()
	for ip_range_id in ip_range_ids:
	    ip_range_record = db_session.query(IpRange).filter(Ip4Range.id == int(ip_range_id.ip4range_id)).all()
	    if not ip_range_record:
		db_session.expunge_all()
		return None
	    ip_range.append({'startIp':ip_range_record[0].startIp, 'endIp':ip_range_record[0].endIp})
	db_session.expunge_all()
	return ip_range


    def GetMacRange(self,vt_server_id):
	mac_range_ids = db_session.query(VTServerMacRange).filter(VTServerMacRange.vtserver_id == vt_server_id).all()
	if not mac_range_ids:
	    db_session.expunge_all()
	    return None
	mac_range = list()
	for mac_range_id in mac_range_ids:
	    mac_range_record = db_session.query(MacRange).filter(MacRange.id == int(mac_range_id.macrange_id)).all()
	    if not mac_range_record:
		db_session.expunge_all()
		return None
	    mac_range.append({'startMac':mac_range_record[0].startMac, 'endMac':mac_range_record[0].endMac})
	db_session.expunge_all()
	return mac_range
	

    def GetNetworkInterfaces(self,vt_server_id):
	network_interface_ids = db_session.query(VTServerNetworkInterfaces).filter(VTServerNetworkInterfaces.vtserver_id == vt_server_id).all()
	if not network_interface_ids:
	    db_session.expunge_all()
	    return None
	network_interfaces = list()
	for network_interface_id in network_interface_ids:
	    network_interface = db_session.query(NetworkInterfaces).filter(NetworkInterfaces.id == int(network_interface_id.networkinterface_id)).filter(NetworkInterfaces.isBridge == 1).all()
	    if network_interface:
	        interfaces = list()
	        for interface in network_interface:
		    interfaces.append({'isMgmt':interface.isMgmt, 'name':interface.name, 'port':int(interface.port) if interface.port else None, 'switchID': interface.switchID})
	        network_interfaces.append(interfaces)
	db_session.expunge_all()
	return network_interfaces


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
	    vm_hrn = vm.projectId + '.' + slice_name + '.' + vm.name
	    vm_urn = hrn_to_urn(vm_hrn, 'sliver')
	    deleted_vm = self.delete_vm(vm_urn)
	    deleted_vms.append(deleted_vm)
	db_session.expunge_all()
	return deleted_vms


    def delete_vm(self, vm_urn, slice_name=None):
	vm_hrn, urn_type = urn_to_hrn(vm_urn)
	if not slice_name:
	    slice_name = get_leaf(get_authority(vm_hrn))
	vm_name = get_leaf(vm_hrn)
	project = get_leaf(get_authority(get_authority(vm_hrn)))
	vm = db_session.query(VirtualMachine).filter(VirtualMachine.name == vm_name).filter(VirtualMachine.sliceName == slice_name).filter(VirtualMachine.projectId == project).first()
	if vm != None:
	     db_session.expunge(vm)
	     deleted_vm = self._destroy_vm_with_expiration(vm.id)
	else:
	     db_session.expunge(vm)
	     vm = db_session.query(VMAllocated).filter(VMAllocated.name == vm_name).first()
	     deleted_vm = dict()
	     if vm != None:
		db_session.expunge(vm)
		deleted_vm = self._unnallocate_vm(vm.id)
	     else:
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
	    #TODO:somehow get the server_uuid or receive it from the params
	    self._destroy_vm(vm_id, server_uuid)


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
	db_session.expunge(vm)

	vm_hrn = vm.projectId + '.' + vm.sliceName + '.' + vm.name
	vm_urn = hrn_to_urn(vm_hrn, 'sliver')

	return server.name, vm_urn


    def create_allocated_vms(self, slice_urn):
	allocated_vms = db_session.query(VMAllocated).filter(VMAllocated.sliceId == slice_urn).all()
	
	for allocated_vm in allocated_vms:
	    params = dict()
	    #TODO:take params in the corresponding format
	    self._create_vm(params)
	    db_session.delete(allocated_vm)
	    db_session.commit()
	db_session.expunge_all()
	#TODO: Wait untill all "ongoing" are received
	#TODO: Return "success" or "error"
	

    def create_vms(self, vm_params):
        #TODO:Modify properly this code
	provisioningRSpecs = VMSfaManager.getActionInstance(vm_params,projectName,sliceName)
        for provisioningRSpec in provisioningRSpecs:
	    ServiceThread.startMethodInNewThread(ProvisioningDispatcher.processProvisioning,provisioningRSpec,'SFA.OCF.VTM')


    def _create_vm(self, vm):
	#TODO: Generate the properly xml from the vm data and call the Provisioning Dispatcher
	pass


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
Base = declarative_base() # get the base class for the ORM, which includes the metadata object (collection of table descriptions)

# We should limit the session's scope (lifetime) to one request. Yet, here we have a different solution.
# In order to avoid side effects (from someone changing a database object), we expunge_all() objects when we hand out objects to other classes.
# So, we can leave the session as it is, because there are no objects in it anyway.

Base.metadata.create_all(db_engine) # create the tables if they are not there yet

