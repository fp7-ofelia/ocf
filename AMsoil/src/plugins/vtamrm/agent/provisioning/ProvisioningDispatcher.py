'''
	@author: msune
	
	Provisioning dispatcher. Selects appropiate Driver for VT tech
'''

import threading

from communications.XmlRpcClient import XmlRpcClient
from utils.VmMutexStore import VmMutexStore
from utils.Logger import Logger
 
class ProvisioningDispatcher: 
	
	logger = Logger.getLogger()

	@staticmethod
	def __getProvisioningDispatcher(vtype):

		#Import of Dispatchers must go here to avoid import circular dependecy 		
		from xen.provisioning.XenProvisioningDispatcher import XenProvisioningDispatcher

		if vtype == "xen": 
			return XenProvisioningDispatcher 
		else:
			raise Exception("Virtualization type not supported by the agent")	
	
	@staticmethod
	def __dispatchAction(dispatcher,action,vm):
		#Inventory
		if action.type_ == "create":
			return dispatcher.createVMfromImage(action.id,vm)
		if action.type_ == "modify" :
			return dispatcher.modifyVM(action.id,vm)
		if action.type_ == "delete" :
			return dispatcher.deleteVM(action.id,vm)

		#Scheduling 
		if action.type_ == "start":
			return dispatcher.startVM(action.id,vm)
		if action.type_ == "reboot" :
			return dispatcher.rebootVM(action.id,vm)
		if action.type_ == "stop" :
			return dispatcher.stopVM(action.id,vm)
		if action.type_ == "hardStop" :
			return dispatcher.hardStopVM(action.id,vm)
		raise Exception("Unknown action type")


	@staticmethod
	def processProvisioning(provisioning):
		for action in provisioning.action:
			vm = action.server.virtual_machines[0]
			try:
				dispatcher = ProvisioningDispatcher.__getProvisioningDispatcher(vm.virtualization_type)	
			except Exception as e:
				XmlRpcClient.sendAsyncProvisioningActionStatus(action.id,"FAILED",str(e))
				ProvisioningDispatcher.logger.error(str(e))	
				return

			try:
				#Acquire VM lock
				VmMutexStore.lock(vm)
				#Send async notification
				XmlRpcClient.sendAsyncProvisioningActionStatus(action.id,"ONGOING","")
	
				ProvisioningDispatcher.__dispatchAction(dispatcher,action,vm)	
			except Exception as e:
				ProvisioningDispatcher.logger.error(str(e))
				raise e
			finally:
				#Release VM lock
				VmMutexStore.unlock(vm)


	##Abstract methods definition for ProvisioningDispatchers
	#Inventory
	@staticmethod
	def createVMfromImage(id,vm):
		raise Exception("Abstract method cannot be called")	
	@staticmethod
	def modifyVM(id,vm):
		raise Exception("Abstract method cannot be called")
	@staticmethod
	def deleteVM(id,vm):
		raise Exception("Abstract method cannot be called")	
	
	#Scheduling
	def startVM(id,vm):
		raise Exception("Abstract method cannot be called")	
	def rebootVM(id,vm):
		raise Exception("Abstract method cannot be called")	
	def stopVM(id,vm):
		raise Exception("Abstract method cannot be called")	
	def hardStopVM(id,vm):
		raise Exception("Abstract method cannot be called")	

