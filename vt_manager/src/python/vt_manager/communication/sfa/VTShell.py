from vt_manager.models.VTServer import VTServer
from vt_manager.models.VirtualMachine import VirtualMachine
from vt_manager.models.Action import Action

from vt_manager.controller.drivers.VTDriver import VTDriver

class VTShell:

        def __init__(self):
                pass

	def GetNodes(self):
		servers = VTServer.objects.all()
		return servers

	#XXX: Slice Methods
	#XXX: Slice == VM
	#XXX: We should create an specific sfa action type
	def GetSlice(self,slicename):
		#XXX: Don't worry about exceptions, they are treated above(VTSfaDriver class)
		vm = VirtualMachine.objects.get(name = slicename)
		return vm

	def StartSlice(self,server_uuid,vm_uuid)
		return self.__crudVM(server_uuid,vm_uuid,Action.PROVISIONING_VM_START_TYPE)

	def StopSlice(self,server_uuid,vm_uuid):
		return self.__crudVM(server_uuid,vm_uuid,Action.PROVISIONING_VM_STOP_TYPE)
	
	def RebootSlice(self,server_uuid,vm_uuid):
                return self.__crudVM(server_uuid,vm_uuid,Action.PROVISIONING_VM_REBOOT_TYPE)

	def DeleteSlice(self,server_uuid,vm_uuid):
                return self.__crudVM(server_uuid,vm_uuid,Action.PROVISIONING_VM_DELETE_TYPE)

	def __crudVM(self,server_uuid,vm_id,action):
		#XXX: First approach
		#XXX: The required params could be obtained by the RSpec or another function
		#XXX: We could create some kind of SFAActions in this function.
		#TODO: In propagate action, is the connection holded until the action in the vm is done? How to do it?
		#TODO: Raise exceptions to SFA Faults
		try:
			VTDriver.PropagateActionToProvisioningDispatcher(vm_id, server_uuid, action)
		except Exception as e:	
			raise e
		return 1

	def create_sliver (slice_urn, slice_hrn, creds, rspec_string, users, options):

		aggregate = DummyAggregate(self)
	        slices = DummySlices(self)
	        sfa_peer = slices.get_sfa_peer(slice_hrn)
	        slice_record=None
	        if users:
        	    slice_record = users[0].get('slice_record', {})

        	# parse rspec
        	rspec = RSpec(rspec_string)
        	requested_attributes = rspec.version.get_slice_attributes()

        	# ensure slice record exists
        	slice = slices.verify_slice(slice_hrn, slice_record, sfa_peer, options=options)
        	# ensure user records exists
        	#users = slices.verify_users(slice_hrn, slice, users, sfa_peer, options=options)

        	# add/remove slice from nodes
        	requested_slivers = []
        	for node in rspec.version.get_nodes_with_slivers():
            		hostname = None
            		if node.get('component_name'):
                		hostname = node.get('component_name').strip()
            		elif node.get('component_id'):
                		hostname = xrn_to_hostname(node.get('component_id').strip())
            		if hostname:
                		requested_slivers.append(hostname)
        	requested_slivers_ids = []
        	for hostname in requested_slivers:
            		try:
               			node_id = self.shell.GetNodes({'hostname': hostname})[0]['node_id']
            		except:
               			node_id = []
            		requested_slivers_ids.append(node_id)
        	nodes = slices.verify_slice_nodes(slice, requested_slivers_ids)
	
		return aggregate.get_rspec(slice_xrn=slice_urn, version=rspec.version)
