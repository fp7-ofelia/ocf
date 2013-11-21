import os
import sys
import shutil
import string
import subprocess

'''
	@author: msune

	Abstract class that handles Hd management routines.

'''

class HdManager(object):
	@staticmethod
	def __getHdManager(hdtype):

		#Import of Dispatchers must go here to avoid import circular dependecy 		
		from xen.provisioning.hdmanagers.FileHdManager import FileHdManager
		from xen.provisioning.hdmanagers.FileFullHdManager import FileFullHdManager
		from xen.provisioning.hdmanagers.LVMHdManager import LVMHdManager

		if hdtype == "file-image": 
			return FileHdManager
		elif hdtype == "full-file-image":
			return FileFullHdManager
		elif hdtype == "logical-volume-image":
			return LVMHdManager
		else:
			raise Exception("HD type not yet supported by XEN agent")	

	##Public methods
	@staticmethod
	def getHdPath(vm):
		man = HdManager.__getHdManager(vm.xen_configuration.hd_setup_type)		
		return man.getHdPath(vm)
	@staticmethod
	def getSwapPath(vm):
		man = HdManager.__getHdManager(vm.xen_configuration.hd_setup_type)		
		return man.getSwapPath(vm)
	
	@staticmethod
	def getConfigFilePath(vm):
		man = HdManager.__getHdManager(vm.xen_configuration.hd_setup_type)		
		return man.getConfigFilePath(vm)
	
	@staticmethod
	def clone(vm):
		man = HdManager.__getHdManager(vm.xen_configuration.hd_setup_type)		
		return man.clone(vm)
	
	@staticmethod
	def mount(vm):
		man = HdManager.__getHdManager(vm.xen_configuration.hd_setup_type)		
		return man.mount(vm)
	
	@staticmethod
	def umount(vm,path):
		man = HdManager.__getHdManager(vm.xen_configuration.hd_setup_type)		
		return man.umount(path)
	
	@staticmethod
	def delete(vm):
		man = HdManager.__getHdManager(vm.xen_configuration.hd_setup_type)		
		return man.delete(vm)

	#Hooks
	@staticmethod
	def startHook(vm):
		man = HdManager.__getHdManager(vm.xen_configuration.hd_setup_type)		
		return man.startHook(vm)
	@staticmethod
	def stopHook(vm):
		man = HdManager.__getHdManager(vm.xen_configuration.hd_setup_type)		
		return man.stopHook(vm)
	@staticmethod
	def rebootHook(vm):
		man = HdManager.__getHdManager(vm.xen_configuration.hd_setup_type)		
		return man.rebootHook(vm)



	
