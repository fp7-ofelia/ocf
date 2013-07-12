from datetime import datetime, timedelta

import amsoil.core.pluginmanager as pm

import vtexceptions as vt_exception

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from VTServer import VTServer
from VTServerIpRange import VTServerIpRange
from VTServerMacRange import VTServerMacRange
from VTServerNetworkInterfaces import VTServerNetworkInterfaces
from IpRange import IpRange
from MacRange import MacRange
from NetworkInterfaces import NetworkInterfaces
from NetworkInterfacesConnections import NetworkInterfacesConnections
from VirtualMachine import VirtualMachine
from IpSlot import IpSlot
from MacSlot import MacSlot
from NetworkInterfaceIp import NetworkInterfaceIp
from XenVM import XenVM
from XenServer import XenServer
from XenServerVM import XenServerVM
from VMExpires import VMExpires

from xrn import hrn_to_urn, urn_to_hrn

class VTResourceManager(object):

    config = pm.getService("config")
    worker = pm.getService('worker')

    RESERVATION_TIMEOUT = config.get("vtam.max_reservation_duration") # sec in the allocated state
    MAX_VM_DURATION = config.get("vtam.max_vm_duration") # sec in the provisioned state (you can always call renew)

    EXPIRY_CHECK_INTERVAL = 10 # sec

    def __init__(self):
	super(VTResourceManager, self).__init__()
        # register callback for regular updates
        worker.addAsReccurring("vtresourcemanager", "expire_vm", None, self.EXPIRY_CHECK_INTERVAL)

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
	    ip_range_record = db_session.query(IpRange).filter(IpRange.id == int(ip_range_id.ip4range_id)).all()
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


    def reserve_vm(self, vms, slice_urn, end_time):
	for vm in vms:
	    #check if the vm name already exists
	    if db_session.query(VirtualMachine).filter(VirtualMachine.name == vm['name']).filter(VirtualMachine.sliceName == urn_to_hrn(slice_urn, 'slice')).first() != None:
	    	raise VTAMVmNameAlreadyTaken(vm['name'])
	    #check if the server is one of the given servers
	    if db_session.query(VTServer).filter(VTServer.name == vm['server_name']).first() == None:
		raise VTAMServerNotFound(vm['server_name'])
#XXX: Deprecated, interface is assigned automatically
#	    for interface in vm['interfaces']:
	    	#check if the interface exists
#	    	if db_session.query(NetworkInterfaces).filter(NetworkInterfaces.name == interface['name']).first() != None:
#                    raise VTAMInterfaceNotFound(interface['name'])
	    	#check if the ip exists
#	    	if db_session.query(IpSlot).filter(IpSlot.ip == interface['ip']).first() != None:
#		    raise VTAMIpNotFound(interface['ip'])
	    	#check if the mac exists
#	    	if db_session.query(MacSlot).filter(MacSlot.mac == interface['mac']).first() != None:
#		    raise VTAMMacNotFound(interface['mac'])
	    	#check if ip and mac are taken
#	    	if db_session.query(MacSlot).filter(MacSlot.mac == inteface['mac']).first().isExcluded == 1:
#		    raise VTAMMacAlreadyTaken(interface['mac'])
#	    	if db_session.query(IpSlot).filter(IpSlot.ip == interface['ip'].first().isExcluded == 1:
#		    raise VTAMIpAlreadyTaken(interface['ip'])
	    db_session.expunge_all()
	max_duration = self.RESERVATION_TIMEOUT
	max_end_time = datetime.utcnow() + timedelta(0, max_duration)
        if end_time == None:
            end_time = max_end_time
        if (end_time > max_end_time):
            raise VTMaxVMDurationExceeded(vm_name)

	#once we know all the VMs could be created, we start creating them
	allocated_vms = list()
	for vm in vms:
	    ip, ip_id = self._reserve_ip()
	    mac, mac_id = self._reserve_mac()
	    server = self._allocate_vm(vm, slice_urn, ip_id, mac_id, end_time)
	    #TODO: allocated_vms organizated into every server?
	    allocated_vms.append({'vm_name':urn_to_hrn(vm['name'], 'sliver'), 'ip':ip, 'mac':mac, 'server':server})
	#check after the expiration time if the VMs continues allocated
	return allocated_vms


    def delete_slice(self, slice_urn):
	# get all the vms from the given slice and delete them
	vms = db_session.query(VirtualMachine).filter(VirtualMachine.SliceName == urn_to_hrn(slice_urn, 'slice')).all()
	deleted_vms = list()	
	for vm in vms:
	    self.delete_vm(vm.name)
	    deleted_vms.append(vm.name)
	db_session.expunge_all()
	return deleted_vms


    def delete_vm(self, slice_urn, vm_urn):
	vm = db_session.query(VirtualMachine).filter(VirtualMachine.name == urn_to_hrn(vm_urn, 'sliver')).filter(VirtualMachine.sliceName == urn_to_hrn(slice_urn, 'slice')).first()
	deleted_vm = vm.name
	self._delete_vm_from_uuid(vm.uuid)
	db_session.expunge_all()
	return deleted_vm

    def _delete_vm_from_uuid(self, uuid):
	vm = db_session.query(VirtualMachine).filter(VirtualMachine.uuid == uuid).first()
	self._destroy_vm(vm)
	vm_network = db_session.query(VMNetworkInterface).filter(VMNetworkInterface.virtualmachine_id == vm.id).first()
	network = db_session.query(NetworkInterfaces).filter(NetworkInterfaces.id == vm_network.networkinterface_id).first()
	net_ip = db_session.query(NetworkInterfaceIp).filter(NetworkInterfaceIp.networkinterface_id == network.id).first()
	expires = db_session.query(VMExpires).filter(VMExpires.vm_id == vm.id).first()
	self._free_mac(network.mac_id)
	self._free_ip(net_ip.ip4slot_id)
	db_session.delete(vm)
	db_session.delete(network)
	db_session.delete(vm_network)
	db_session.delete(net_ip)
	db_session.delete(expires)
	db_session.commit()
	db_session.expunge_all()


    def _destroy_vm(self, vm):
	pass


    def _reserve_ip(self, requested_ip):
	ip = db_session.query(IpSlot).filter(IpSlot.isExcluded == 0).first()
	ip.isExcluded = 1
	db_session.commit()
        db_session.expunge(ip)
	return ip.ip, ip.id
	

    def _reserve_mac(self, requested_mac):
	mac = db_session.query(MacSlot).filter(MacSlot.isExcluded == 0).first()
        mac.isExcluded = 1
        db_session.commit()
        db_session.expunge(mac)
	return mac.mac, mac.id

    def _allocate_vm(self, requested_vm, slice_urn, ip_id, mac_id, end_time):
	vm = VirtualMachine()
	vm.name = requested_vm['name']
	vm.uuid = requestd_vm['uuid']
	vm.memory = int(requested_vm['memory_mb'])
	vm.discSpaceGB = float(requested_vm['hd_size_mb'])/1024
	vm.projectId = requested_vm['project_id']
	vm.sliceId = requested_vm['slice_id']
	vm.sliceName = requested_vm['slice_name']
	vm.operatingSystemType = requested_vm['operating_system_type'] 
	vm.operatingSystemVersion = requested_vm['operating_system_version']
	vm.operatingSystemDistribution = requested_vm['operating_system_distribution']
	vm.status = 'allocated'

	db_session.add(vm)
	db_session.commit()
	db_session.expunge(vm)

	xen_vm = XenVM()
	xen_vm.virtualmachine_ptr_id = vm.id
	xen_vm.hdSetupType = requested_vm['hd_setup_type']
	xen_vm.hdOriginPath = requested_vm['hd_origin_path']
	xen_vm.virtualizationSetupType = requested_vm['virtualization_setup_type']

	db_session.add(xen_vm)
	db_session.commit()
	db_session.expunge(xen_vm)

	server = db_session.query(VTServer).filter(VTServer.name == requested_vm['server_name']).first()
	xen_server_vm = XenServerVM()
	xen_server_vm.xenserver_id = server.id
	xen_server_vm.xenvm_id = xen_vm.id

	network_interface_ids = db_session.query(VTServerNetworkInterfaces).filter(VTServerNetworkInterfaces.vtserver_id == vt_server_id).all()
	for network_interface_id in network_interface_ids:
	    network = db_session.query(NetworkInterfaces).filter(NetworkInterfaces.id == network_interface_id).filter(NetworkInterfaces.isMgmt == 0).first()
	    if network != None:
		network_interface = NetworkInterfaces()
		network_interface.name = network.name + '-slave'
	        network_interface.mac_id = mac_id
	        network_interface.isMgmt = network.isMgmt
	        network_interface.isBridge = 0  
	        db_session.add(network_interface)
                db_session.commit()
                db_session.expunge(network_interface)
		db_session.expunge(network)

	    	network_interface_ip = NetworkInterfaceIp()
	    	network_interface_ip.networkinterface_id = network_interface.id
	    	network_interface_ip.ip4slot_id = ip_id
	   	db_session.add(network_interface_ip)
	    	db_session.commit()
	    	db_session.expunge(network_interface_ip)

	    	vm_network_interface = VMNetworkInterface()
	    	vm_network_interface.virtualmachine_id = vm.id
	    	vm_network_interface.networkinterface_id = network_interface.id
	    	db_session.add(vm_network_interface)
	    	db_session.commit()
	        db_session.expunge(vm_network_interface)
        expires = VMExpires()
	expires.vm_id = vm.id
	expires.expires = end_time
	db_session.add(expires)
	db_session.commit()
	db_session.expunge_all()
	return server.name


    def create_allocated_vms(self, slice_urn):
	allocated_vms = db_session.query(VirutalMachines).filter(VirtualMachines.sliceName = slice_urn).filter(status = "allocated").all() #TODO: try with urn_to_hrn or hrn_to_urn!!!!!
	for allocated_vm in allocated_vms:
	    allocated_vm.status = "ongoing" #a status indicating that the VM is being created, but still isn't ready
	    db_session.add(allocated_vm)
	    db_session.commit()
	    self._create_vm(allocated_vm)
	db_session.expunge_all()
	#TODO: Wait untill all "ongoing" are received
	#TODO: Return "success" or "error"
	

    def _create_vm(self, vm):
	#TODO: Generate the properly xml from the vm data and call the Provisioning Dispatcher
	pass

    def _free_vm(vm_id):
	vm = db_session.query(VirtualMachine).filter(VirtualMachine.id == vm_id).first()
	self._delete_vm_from_uuid(vm.uuid)
	db_session.expunge(vm)

    def _free_ip(self, ip_id):
	ip = db_session.query(IpSlot).filter(IpSlot.id == ip_id).first()
	ip.isExcluded = 0
	db_session.commit()
	db_session.expunge(ip)

    def _free_mac(self, marc_id):
	mac = db_session.query(MacSlot).filter(MacSlot.id == mac_id).first()
        mac.isExcluded = 0
        db_session.commit()
        db_session.expunge(mac)	


    @worker.outsideprocess
    def expire_vm(self, params):
        vms = db_session.query(VMExpires).filter(VMExpires.expires >= datetime.utcnow()).all()
        for vm in vms:
            self._free_vms(vm.vm_id)
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

