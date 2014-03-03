from communications.XmlRpcClient import XmlRpcClient
from provisioning.ProvisioningDispatcher import ProvisioningDispatcher
from utils.AgentExceptions import *
from utils.Logger import Logger
from xen.provisioning.HdManager import HdManager
from xen.provisioning.VMConfigurator import VMConfigurator
from xen.XendManager import XendManager
import sys

"""
	@author: msune

	XenProvisioningDispatcher routines
"""

class XenProvisioningDispatcher(ProvisioningDispatcher):

	logger = Logger.getLogger()
	
	@staticmethod
	def __on_success(message = None):
		"""
		Perform operations on success
		"""
		if message:
			XenProvisioningDispatcher.logger.info(str(message))
		# Send asynchronous notification on success
		XmlRpcClient.sendAsyncProvisioningActionStatus(id, "SUCCESS", "")
	
	@staticmethod
	def __on_error(message = None):
		"""
		Perform operations on error
		"""
		if message:
			XenProvisioningDispatcher.logger.error(str(message))
		# Send asynchronous notification on error
		XmlRpcClient.sendAsyncProvisioningActionStatus(id, "FAILED", str(message))
	
	# Inventory routines
	@staticmethod
	def create_vm(id,vm):
		"""
		Create VM from image
		"""
		pathToMountPoint = ""
		XenProvisioningDispatcher.logger.info("Initiating creation process for VM: "+vm.name+" under project: "+vm.project_id+" and slice: "+vm.slice_id)
		try:
			# Clone HD
			HdManager.clone(vm)
			XenProvisioningDispatcher.logger.debug("HD cloned successfully...")
			# Mount copy
			pathToMountPoint = HdManager.mount(vm)
			XenProvisioningDispatcher.logger.debug("Mounting at:"+pathToMountPoint)
			XenProvisioningDispatcher.logger.debug("HD mounted successfully...")
			# Configure VM OS
			VMConfigurator.configureVmDisk(vm,pathToMountPoint)
			# Umount copy
			HdManager.umount(vm,pathToMountPoint)
			XenProvisioningDispatcher.logger.debug("HD unmounted successfully...")
			# Synthesize config file
			VMConfigurator.createVmConfigurationFile(vm)
			XenProvisioningDispatcher.logger.debug("XEN configuration file created successfully...")
			XenProvisioningDispatcher.__on_success("VM named %s has been created." % vm.name)
		except Exception as e:
			XenProvisioningDispatcher.logger.error(str(e))
			# Send async notification
			try:
				HdManager.umount(vm,pathToMountPoint)
			except:
				pass
			try:
				# Delete VM disc and conf file if the error is not due because
				# the VM already exists
				if not isinstance(e,VMalreadyExists):
					XenProvisioningDispatcher.delete_vm(id,vm)
			except:
				pass
			XenProvisioningDispatcher.__on_error(e)
			return

	@staticmethod
	def modify_vm(id,vm):
		# Check existence of VM
		raise Exception("Not implemented")
	
	@staticmethod
	def delete_vm(id,vm):
		try:
			try:
				# If it wasn't stopped, stop it
				XendManager.stopDomain(vm)	
			except Exception as e:
				pass
			# Trigger HD deletion in remote	
			HdManager.delete(vm)
			XenProvisioningDispatcher.__on_success()
		except Exception as e:
			XenProvisioningDispatcher.__on_error(e)
			return
	
	# Scheduling routines
	@staticmethod
	def start_vm(id,vm):
		try:
			# Trigger	
			HdManager.startHook(vm)	
			XendManager.startDomain(vm)
			XenProvisioningDispatcher.__on_success("VM named %s has been started." % vm.name)
		except Exception as e:
			XenProvisioningDispatcher.__on_error(e)
			return
	
	@staticmethod
	def reboot_vm(id,vm):
		try:
			# Just try to reboot
			HdManager.rebootHook(vm)
			XendManager.rebootDomain(vm)
			XenProvisioningDispatcher.__on_success("VM named %s has been rebooted." % vm.name)
		except Exception as e:
			XenProvisioningDispatcher.__on_error(e)
			return
	
	@staticmethod
	def stop_vm(id, vm, hard_stop = None):
		try:
			# Try to stop domain
			XendManager.stopDomain(vm)
			if hard_stop:
				HdManager.stopHook(vm)
			XenProvisioningDispatcher.__on_success("VM named %s has been stopped." % vm.name)
		except Exception as e:
			XenProvisioningDispatcher.__on_error(e)
			return
	
	@staticmethod
	def hardstop_vm(id, vm):
		return stop_vm(id, vm, "hard_stop")
