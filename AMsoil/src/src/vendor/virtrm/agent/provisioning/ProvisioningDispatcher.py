'''
	@author: msune
	
	Provisioning dispatcher. Selects appropiate Driver for VT tech
'''

from communications.XmlRpcClient import XmlRpcClient
from utils.Logger import Logger
from utils.VmMutexStore import VmMutexStore
import threading

class ProvisioningDispatcher: 
	
	logger = Logger.getLogger()
	
	@staticmethod
	def __get_dispatcher(vtype):
		
		#Import of Dispatchers must go here to avoid import circular dependency 		
		from xen.provisioning.XenProvisioningDispatcher import XenProvisioningDispatcher
		if vtype == "xen": 
			return XenProvisioningDispatcher
		else:
			raise Exception("Virtualization type not supported by the agent")
	
	@staticmethod
	def __dispatch_action(dispatcher, action, vm):
		# Inventory
		if action.type_ == "create":
			return dispatcher.create_vm(action.id, vm)
		if action.type_ == "modify" :
			return dispatcher.modify_vm(action.id, vm)
		if action.type_ == "delete" :
			return dispatcher.delete_vm(action.id, vm)
		# Scheduling 
		if action.type_ == "start":
			return dispatcher.start_vm(action.id, vm)
		if action.type_ == "reboot" :
			return dispatcher.reboot_vm(action.id, vm)
		if action.type_ == "stop" :
			return dispatcher.stop_vm(action.id, vm)
		if action.type_ == "hardStop" :
			return dispatcher.hardstop_vm(action.id, vm)
		raise Exception("Unknown action type")
	
	@staticmethod
	def process(provisioning):
		for action in provisioning.action:
			vm = action.server.virtual_machines[0]
			try:
				dispatcher = ProvisioningDispatcher.__get_dispatcher(vm.virtualization_type)	
			except Exception as e:
				XmlRpcClient.sendAsyncProvisioningActionStatus(action.id, "FAILED", str(e))
				ProvisioningDispatcher.logger.error(str(e))	
				return
			try:
				# Acquire VM lock
				VmMutexStore.lock(vm)
				# Send async notification
				XmlRpcClient.sendAsyncProvisioningActionStatus(action.id, "ONGOING", "")
				ProvisioningDispatcher.__dispatch_action(dispatcher,action,vm)	
			except Exception as e:
				ProvisioningDispatcher.logger.error(str(e))
				raise e
			finally:
				# Release VM lock
				VmMutexStore.unlock(vm)
	
	# Abstract methods definition for ProvisioningDispatchers
	# Inventory
	@staticmethod
	def create_vm(id,vm):
		raise Exception("Abstract method cannot be called")	
	@staticmethod
	def modify_vm(id,vm):
		raise Exception("Abstract method cannot be called")
	@staticmethod
	def delete_vm(id,vm):
		raise Exception("Abstract method cannot be called")	
	
	# Scheduling
	def start_vm(id,vm):
		raise Exception("Abstract method cannot be called")	
	def reboot_vm(id,vm):
		raise Exception("Abstract method cannot be called")	
	def stop_vm(id,vm):
		raise Exception("Abstract method cannot be called")	
	def hardstop_vm(id,vm):
		raise Exception("Abstract method cannot be called")	
