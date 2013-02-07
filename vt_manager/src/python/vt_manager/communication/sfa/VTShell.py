from vt_manager.models.VTServer import VTServer
from vt_manager.controller.drivers.VTDriver import VTDriver

class VTShell:

        def __init__(self):
                pass

	def GetNodes(self):
		servers = VTServer.objects.all()
		return servers

	def crudVM(self,server_uuid,vm_id,action):
		#XXX: First approach
		#XXX: The required vars could be obtained by the RSpec or another function
		#XXX: We could create some kind of SFAActions in this function.
		try:
			VTDriver.PropagateActionToProvisioningDispatcher(vm_id, server_uuid, action)
		except Exception as e:	
			raise e
		
		return 1
