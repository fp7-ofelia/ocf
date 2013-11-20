import sys
from xen.provisioning.HdManager import HdManager
from xen.XendManager import XendManager
from xen.provisioning.VMConfigurator import VMConfigurator
from provisioning.ProvisioningDispatcher import ProvisioningDispatcher
from communications.XmlRpcClient import XmlRpcClient
from utils.Logger import Logger
from utils.AgentExceptions import *

'''
	@author: msune

	XenProvisioningDispatcher routines
'''

class XenProvisioningDispatcher(ProvisioningDispatcher):

	logger = Logger.getLogger()

	##Inventory routines
	@staticmethod
	def createVMfromImage(id,vm):
		pathToMountPoint = ""	
		XenProvisioningDispatcher.logger.info("Initiating creation process for VM: "+vm.name+" under project: "+vm.project_id+" and slice: "+vm.slice_id)
		try:
			#Clone HD
			HdManager.clone(vm)
			XenProvisioningDispatcher.logger.debug("HD cloned successfully...")
			
			#Mount copy
			pathToMountPoint=HdManager.mount(vm)
			XenProvisioningDispatcher.logger.debug("Mounting at:"+pathToMountPoint)
			XenProvisioningDispatcher.logger.debug("HD mounted successfully...")
			
			#Configure VM OS
			VMConfigurator.configureVmDisk(vm,pathToMountPoint)

			#Umount copy
			HdManager.umount(vm,pathToMountPoint)
			XenProvisioningDispatcher.logger.debug("HD unmounted successfully...")
	
			#Synthesize config file
			VMConfigurator.createVmConfigurationFile(vm)
			XenProvisioningDispatcher.logger.debug("XEN configuration file created successfully...")
			
			XenProvisioningDispatcher.logger.info("Creation of VM "+vm.name+" has been successful!!")
			#Send async notification
			XmlRpcClient.sendAsyncProvisioningActionStatus(id,"SUCCESS","")
		except Exception as e:
			XenProvisioningDispatcher.logger.error(str(e))
			#Send async notification
			try:
				HdManager.umount(vm,pathToMountPoint)
			except:
				pass
			try:
				#Delete VM disc and conf file if the error is not due because
				#the VM already exists
				if not isinstance(e,VMalreadyExists):
					XenProvisioningDispatcher.deleteVM(id,vm)
			except:
				pass
			XmlRpcClient.sendAsyncProvisioningActionStatus(id,"FAILED",str(e))
			return

	@staticmethod
	def modifyVM(id,vm):
		#Check existance of VM
		raise Exception("Not implemented")

	@staticmethod
	def deleteVM(id,vm):
		try:
			try:
				#if it wasn't stopped, do it
				XendManager.stopDomain(vm)	
			except Exception as e:
				pass
			
			#Trigger Hd Deletion in Remote	
			HdManager.delete(vm)	

			#Send async notification
			XmlRpcClient.sendAsyncProvisioningActionStatus(id,"SUCCESS","")
		except Exception as e:
			XenProvisioningDispatcher.logger.error(str(e))
			#Send async notification
			XmlRpcClient.sendAsyncProvisioningActionStatus(id,"FAILED",str(e))
			return
	
	##Scheduling routines
	@staticmethod
	def startVM(id,vm):
		try:
			#Trigger	
			HdManager.startHook(vm)	
			XendManager.startDomain(vm)
	
			XenProvisioningDispatcher.logger.info("VM named "+vm.name+" has been started.")
			#Send async notification
			XmlRpcClient.sendAsyncProvisioningActionStatus(id,"SUCCESS","")
		except Exception as e:
			XenProvisioningDispatcher.logger.error(str(e))
			#Send async notification
			XmlRpcClient.sendAsyncProvisioningActionStatus(id,"FAILED",str(e))
			return

	@staticmethod
	def rebootVM(id,vm):
		try:
			#Just try to reboot
			HdManager.rebootHook(vm)
			XendManager.rebootDomain(vm)
	
			XenProvisioningDispatcher.logger.info("VM named "+vm.name+" has been rebooted.")
			#Send async notification
			XmlRpcClient.sendAsyncProvisioningActionStatus(id,"SUCCESS","")
		except Exception as e:
			XenProvisioningDispatcher.logger.error(str(e))
			#Send async notification
			XmlRpcClient.sendAsyncProvisioningActionStatus(id,"FAILED",str(e))
			return

	@staticmethod
	def stopVM(id,vm):
		try:
			#Just try to stop
			XendManager.stopDomain(vm)
	
			XenProvisioningDispatcher.logger.info("VM named "+vm.name+" has been stopped.")
			#Send async notification
			XmlRpcClient.sendAsyncProvisioningActionStatus(id,"SUCCESS","")
		except Exception as e:
			XenProvisioningDispatcher.logger.error(str(e))
			#Send async notification
			XmlRpcClient.sendAsyncProvisioningActionStatus(id,"FAILED",str(e))
			return

	@staticmethod
	def hardStopVM(id,vm):
		try:
			#First stop domain
			XendManager.stopDomain(vm)	
			HdManager.stopHook(vm)	
		
			XenProvisioningDispatcher.logger.info("VM named "+vm.name+" has been stopped.")
			#Send async notification
			XmlRpcClient.sendAsyncProvisioningActionStatus(id,"SUCCESS","")
		except Exception as e:
			XenProvisioningDispatcher.logger.error(str(e))
			#Send async notification
			XmlRpcClient.sendAsyncProvisioningActionStatus(id,"FAILED",str(e))
			return

