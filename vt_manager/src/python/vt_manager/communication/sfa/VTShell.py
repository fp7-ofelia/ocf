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
		#TODO: what happens with the names? There are not easier ways to obtain a vm and a server?

		name = slicename # or uuid...
		servers = self.GetNodes()
		for server in servers:
			child_server = server.getChildObject()
			vm = child_server.getVMs(name=name)
			if vm:
				return {'node_id':server.uuid,'slice_id':vm.id}
		
		raise Exception("Record not found")

	def StartSlice(self,server_uuid,vm_id):
		return 1
		return self.__crudVM(server_uuid,vm_id,Action.PROVISIONING_VM_START_TYPE)

	def StopSlice(self,server_uuid,vm_id):
		return 1
		return self.__crudVM(server_id,vm_id,Action.PROVISIONING_VM_STOP_TYPE)
	
	def RebootSlice(self,server_uuid,vm_id):
		return 1
                return self.__crudVM(server_id,vm_uuid,Action.PROVISIONING_VM_REBOOT_TYPE)

	def DeleteSlice(self,server_uuid,vm_id):
		return 1
                return self.__crudVM(server_id,vm_id,Action.PROVISIONING_VM_DELETE_TYPE)

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

	def CreateSliver(self,vm_params):
		#XXX: My idea here is to use the dict structure vm_params to create a provisioning rspec and send it only to the agent.
 
		pass
	def GetSlices(server_id,user=None):
		#XXX: Get all the vms from a node and from an specific user
		
		pass
