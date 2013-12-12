from communication.client.xmlrpc import XmlRpcClient
from controller.actions.action import ActionController
from controller.drivers.virt import VTDriver
from resources.virtualmachine import VirtualMachine
from utils.action import Action
from utils.xmlhelper import XmlHelper
import logging

class ProvisioningResponseDispatcher():
	"""
	Handles the Agent responses when action status changes
	"""
	
	@staticmethod
	def process(rspec):
		"""
		Process provisioning response.
		"""
		logging.debug("PROCESSING RESPONSE process() STARTED...")
		actions = rspec.response.provisioning.action
		for action in actions:
			try:
				action_model = ActionController.getAction(action.id)
			except Exception as e:
				logging.error("No action in DB with the incoming uuid\n%s", e)
				return
			# If the response is for an action either in QUEUED or ONGOING status, 
			# then SUCCESS or FAILED actions are finished
			if action_model.getStatus() is Action.QUEUED_STATUS or Action.ONGOING_STATUS:
				logging.debug("The incoming response has id: %s and NEW status: %s",action_model.uuid,action_model.status)
				action_model.status = action.status
				action_model.description = action.description
				# Complete information required for the Plugin: action type and VM
				ActionController.completeActionRspec(action, action_model)
				# XXX: Implement this method or some other doing this job
				vm = VTDriver.getVMbyUUID(action_model.getObjectUUID())
				controller=VTDriver.getDriver(vm.vtserver.getVirtTech())
				# Update VM after obtaining a response code
				fail_on_create_vm = ProvisioningResponseDispatcher.__update_vm_after_response(action_model, vm)
				try:
					logging.debug("Sending response to Plugin in sendAsync")
					XmlRpcClient.callRPCMethod(vm.getCallBackURL(), "sendAsync", XmlHelper.craftXmlClass(rspec))
					if fail_on_create_vm:
						controller.deleteVM(vm)
				except Exception as e:
					logging.error("Could not connect to Plugin in sendAsync\n%s",e)
					return
			# If response is for a finished action
			else:
				try:
					# XXX: What should be done if this happen?
					logging.error("Received response for an action in wrong state\n")
					XmlRpcClient.callRPCMethod(vm.getCallBackURL(), "sendAsync", XmlHelper.getProcessingResponse(Action.ACTION_STATUS_FAILED_TYPE, action, "Received response for an action in wrong state"))
				except Exception as e:
					logging.error(e)
					return
	
	@staticmethod
	def __update_vm_after_response(action_model, vm):
		"""
		Dispatches to one or another method to update VM
		status after a response is obtained.
		"""
		action_status = action_model.getStatus()
		action_type = action_type
		if action_status == Action.SUCCESS_STATUS:
			ProvisioningResponseDispatcher.__update_vm_after_SUCCESS(action_type, vm)
		elif action_status == Action.ONGOING_STATUS:
			ProvisioningResponseDispatcher.update_vm_after_ONGOING(action_type, vm)
		elif action_status == Action.FAILED_STATUS:
			# Return result of fail_on_create_vm
			return ProvisioningResponseDispatcher.__update_vm_after_FAILED(action_type, vm)
		else:
			vm.setState(VirtualMachine.UNKNOWN_STATE)
	
	@staticmethod
	def __update_vm_after_SUCCESS(action_type, vm):
		if action_type == Action.PROVISIONING_VM_CREATE_TYPE:
			vm.setState(VirtualMachine.CREATED_STATE)
		elif action_type is Action.PROVISIONING_VM_START_TYPE or Action.PROVISIONING_VM_REBOOT_TYPE:
			vm.setState(VirtualMachine.RUNNING_STATE)
		elif action_type == Action.PROVISIONING_VM_STOP_TYPE:
			vm.setState(VirtualMachine.STOPPED_STATE)
		elif action_type == Action.PROVISIONING_VM_DELETE_TYPE:
			controller = VTDriver.getDriver(vm.vtserver.getVirtTech())
			controller.deleteVM(vm)
	
	@staticmethod
	def update_vm_after_ONGOING(action_model, vm):
		if action_type == Action.PROVISIONING_VM_CREATE_TYPE:
			vm.setState(VirtualMachine.CREATING_STATE)
		elif action_type == Action.PROVISIONING_VM_START_TYPE:
			vm.setState(VirtualMachine.STARTING_STATE)
		elif action_type == Action.PROVISIONING_VM_STOP_TYPE:
			vm.setState(VirtualMachine.STOPPING_STATE)
		elif action_type == Action.PROVISIONING_VM_DELETE_TYPE:
			vm.setState(VirtualMachine.DELETING_STATE)
		elif action_type == Action.PROVISIONING_VM_REBOOT_TYPE:
			vm.setState(VirtualMachine.REBOOTING_STATE)
	
	@staticmethod
	def __update_vm_after_FAILED(action_model, vm):
		if  action_type == Action.PROVISIONING_VM_START_TYPE:
			vm.setState(VirtualMachine.STOPPED_STATE)
		elif action_type == Action.PROVISIONING_VM_STOP_TYPE:
			vm.setState(VirtualMachine.RUNNING_STATE)
		elif action_type == Action.PROVISIONING_VM_REBOOT_TYPE:
			vm.setState(VirtualMachine.STOPPED_STATE)
		elif action_type == Action.PROVISIONING_VM_CREATE_TYPE:
			# VM deleted after sending response to the Plugin because callBackUrl is required
			# Return fail_on_create_vm = True
			return True
		else:
			vm.setState(VirtualMachine.FAILED_STATE)
