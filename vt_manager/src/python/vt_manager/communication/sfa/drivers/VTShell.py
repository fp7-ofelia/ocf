from vt_manager.models.VirtualMachine import VirtualMachine
from vt_manager.models.VTServer import VTServer
from vt_manager.models.Action import Action
from vt_manager.models.expiring_components import ExpiringComponents

from vt_manager.communication.sfa.util.xrn import Xrn, hrn_to_urn, get_leaf

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

	def GetNodes(self,slice=None,authority=None,uuid=None):
		servers = VTServer.objects.all()
		if uuid:
			for server in servers:
				if str(server.uuid) == str(uuid):
					return server
			return None
		if not slice: 
		    return servers
		else:
		    slice_servers = list()
		    for server in servers:
			vms = server.getChildObject().getVMs(sliceName=slice, projectName = authority)
                        if vms:
			    slice_servers.append(server)
                    return slice_servers

	def GetSlice(self,slicename,authority):

		name = slicename # or uuid...
		servers = self.GetNodes()
		slices = dict()
		List = list()
		for server in servers:
			child_server = server.getChildObject()
			vms = child_server.getVMs(sliceName=name, projectName = authority)
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

	def CreateSliver(self,vm_params,projectName,sliceName,expiration):
		#processes = list()
		provisioningRSpecs = VMSfaManager.getActionInstance(vm_params,projectName,sliceName)
		for provisioningRSpec in provisioningRSpecs:
		    #waiter,event = Pipe()
		    #process = SfaCommunicator(provisioningRSpec.action[0].id,event,provisioningRSpec)
		    #processes.append(process)
		    #process.start()
                    ServiceThread.startMethodInNewThread(ProvisioningDispatcher.processProvisioning,provisioningRSpec,'SFA.OCF.VTM') #UrlUtils.getOwnCallbackURL())
                    if expiration:
                        ExpiringComponents.objects.create(slice=sliceName, authority=projectName, expires=expiration).save()
                         
		#waiter.recv()
		return 1
 
	def GetSlices(server_id,user=None):
		#TODO: Get all the vms from a node and from an specific user
		pass

        def convert_to_uuid(self,requested_attributes):
                for slivers in requested_attributes:
                        servers = VTServer.objects.filter(name=get_leaf(slivers['component_id']))
		        slivers['component_id'] = servers[0].uuid
                return requested_attributes
