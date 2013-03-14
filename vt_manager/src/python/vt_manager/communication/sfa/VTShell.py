from vt_manager.models.VirtualMachine import VirtualMachine
from vt_manager.models.VTServer import VTServer
from vt_manager.models.Action import Action

from vt_manager.controller.drivers.VTDriver import VTDriver
from vt_manager.communication.sfa.vm_utils.VMSfaManager import VMSfaManager
from vt_manager.communication.sfa.vm_utils.SfaCommunicator import SfaCommunicator
from vt_manager.utils.ServiceThread import ServiceThread

import threading
import time

from vt_manager.controller.dispatchers.xmlrpc.ProvisioningDispatcher import ProvisioningDispatcher
from vt_manager.utils.UrlUtils import UrlUtils
#XXX:To implement SfaCommunicator for a better use of SFA CreateSliver and Start/Stop/Delete/Update slice
#from vt_manager.common.middleware.thread_local import thread_locals, push
#from multiprocessing import Pipe

class VTShell:

        def __init__(self):
                pass

	def GetNodes(self,slice = None):
		servers = VTServer.objects.all()
		if not slice: 
		    return servers
		else:
		    slice_servers = list()
		    for server in servers:
                        if server.getChildObject().getVMs(sliceName=slice):
			    slice_servers.append(server)
                    return slice_servers

	def GetSlice(self,slicename):

		name = slicename # or uuid...
		servers = self.GetNodes()
		slices = dict()
		for server in servers:
			List = list()
			child_server = server.getChildObject()
			vms = child_server.getVMs(sliceName=name)
			for vm in vms:
				List.append({'vm-name':vm.name,'vm-state':vm.state,'vm-id':vm.id, 'node-id':server.uuid, 'node-name':server.name})
			        	
		slices['vms'] = List
		return slices	

	def StartSlice(self,server_uuid,vm_id):
		return self.__crudVM(server_uuid,vm_id,Action.PROVISIONING_VM_START_TYPE)

	def StopSlice(self,server_uuid,vm_id):
		return self.__crudVM(server_uuid,vm_id,Action.PROVISIONING_VM_STOP_TYPE)
	
	def RebootSlice(self,server_uuid,vm_id):
                return self.__crudVM(server_uuid,vm_id,Action.PROVISIONING_VM_REBOOT_TYPE)

	def DeleteSlice(self,server_uuid,vm_id):
                return self.__crudVM(server_uuid,vm_id,Action.PROVISIONING_VM_DELETE_TYPE)

	def __crudVM(self,server_uuid,vm_id,action):
		try:
			VTDriver.PropagateActionToProvisioningDispatcher(vm_id, server_uuid, action)
		except Exception as e:	
			raise e
		return 1

	def CreateSliver(self,vm_params):
		#processes = list()
		provisioningRSpecs = VMSfaManager.getActionInstance(vm_params)
		for provisioningRSpec in provisioningRSpecs:
		    #waiter,event = Pipe()
		    #process = SfaCommunicator(provisioningRSpec.action[0].id,event,provisioningRSpec)
		    #processes.append(process)
		    #process.start()
                    ServiceThread.startMethodInNewThread(ProvisioningDispatcher.processProvisioning,provisioningRSpec,UrlUtils.getOwnCallbackURL())
		#waiter.recv()
		return 1
 
	def GetSlices(server_id,user=None):
		#TODO: Get all the vms from a node and from an specific user
		pass

