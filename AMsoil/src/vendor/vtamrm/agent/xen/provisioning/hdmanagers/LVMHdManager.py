import os
import sys
import shutil
import string
import subprocess
from settings.settingsLoader import OXA_FILEHD_CACHE_VMS,OXA_FILEHD_REMOTE_VMS,OXA_FILEHD_CACHE_TEMPLATES,OXA_FILEHD_REMOTE_TEMPLATES,OXA_FILEHD_USE_CACHE

'''
	@author: luismi-borja

	Logical volume-type Hd management routines
'''

OXA_FILEHD_HD_TMP_MP="/tmp/oxa/hd"

class LVMHdManager(object):

	#Enables/disables the usage of Cache directory
	__useCache=OXA_FILEHD_USE_CACHE

	#Debug string 
	@staticmethod
	def debugVM(vm):
		return " project:"+vm.project_id+", slice:"+vm.slice_id+", name:"+vm.name

	'''Private Method'''
	@staticmethod
        def __create(vm):
		p = subprocess.Popen(['/sbin/lvdisplay', '/dev/vservers/' + vm.name + '-disk'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		ret = p.wait()		
		if ret == 0:
			raise Exception("This machine already exists:" + LVMHdManager.debugVM(vm))	
                if vm.xen_configuration.virtualization_setup_type == "hardware-assisted-virtualization":
                        p = subprocess.Popen(['/sbin/lvcreate', '/dev/vservers', '-L', '20G', '-n', vm.name + '-disk'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                	p.wait()
		return

	
	##Hooks
	'''Pre-start Hook'''
	@staticmethod
	def startHook(vm):
		return
	
	'''Pre-reboot Hook'''
	@staticmethod
	def rebootHook(vm):
		return

	'''Post-stop Hook'''
	@staticmethod
	def stopHook(vm):
		return

	@staticmethod
	def delete(vm):
		subprocess.call(['/usr/bin/xen-delete-image', vm.name])
		os.remove(LVMHdManager.getConfigFilePath(vm))
	
	''' Returns the path of the config file directory in Cache, if used'''
        @staticmethod
        def getConfigFileDir(vm):
                if LVMHdManager.__useCache:
                        return OXA_FILEHD_CACHE_VMS+vm.project_id+"/"+vm.slice_id
                else:
                        return OXA_FILEHD_REMOTE_VMS+vm.project_id+"/"+vm.slice_id


	''' Returns the path of the config file in Cache, if used'''
        @staticmethod
        def getConfigFilePath(vm):
                if LVMHdManager.__useCache:
                        return OXA_FILEHD_CACHE_VMS+vm.project_id+"/"+vm.slice_id+"/"+vm.name+".cfg"
                else:
                        return OXA_FILEHD_REMOTE_VMS+vm.project_id+"/"+vm.slice_id+"/"+vm.name+".cfg"
	
	@staticmethod
        def clone(vm):
		return 

	#Mount/umount routines
        @staticmethod
        def mount(vm):
                LVMHdManager.__create(vm)
		return 

        @staticmethod
        def umount(path):
		return

