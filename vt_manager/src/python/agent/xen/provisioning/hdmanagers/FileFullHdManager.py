import os
import sys
import shutil
import string
import subprocess
import re
from settings.settingsLoader import OXA_FILEHD_CACHE_VMS,OXA_FILEHD_REMOTE_VMS,OXA_FILEHD_CACHE_TEMPLATES,OXA_FILEHD_REMOTE_TEMPLATES,OXA_FILEHD_USE_CACHE,OXA_FILEHD_NICE_PRIORITY,OXA_FILEHD_CREATE_SPARSE_DISK,OXA_FILEHD_IONICE_CLASS, OXA_FILEHD_IONICE_PRIORITY,OXA_FILEHD_DD_BS_KB, OXA_DEFAULT_SWAP_SIZE_MB
from utils.AgentExceptions import *
from utils.Logger import Logger
from xen.provisioning.configurators.irati.IratiDebianVMConfigurator import IratiDebianVMConfigurator
from xen.provisioning.configurators.spirent.SpirentCentOSVMConfigurator import SpirentCentOSVMConfigurator
from xen.provisioning.configurators.debian7.DebianWheezyVMConfigurator import DebianWheezyVMConfigurator

'''
	@author: msune

	This hd manager is cloning a complete hard disk image
'''

OXA_FILEHD_HD_TMP_MP="/tmp/oxa/hd"

class FileFullHdManager(object):
	'''
	File-type Hard Disk management routines
	'''
	
	logger = Logger.getLogger()

	#Enables/disables the usage of Cache directory
	__useCache=OXA_FILEHD_USE_CACHE

	##Utils
	@staticmethod
	def subprocessCall(command, priority=OXA_FILEHD_NICE_PRIORITY, ioPriority=OXA_FILEHD_IONICE_PRIORITY, ioClass=OXA_FILEHD_IONICE_CLASS, stdout=None):
		try:
			wrappedCmd = "/usr/bin/nice -n "+str(priority)+" /usr/bin/ionice -c "+str(ioClass)+" -n "+str(ioPriority)+" "+command
			FileFullHdManager.logger.debug("Executing: "+wrappedCmd) 
			subprocess.check_call(wrappedCmd, shell=True, stdout=stdout)
		except Exception as e:
			FileFullHdManager.logger.error("Unable to execute command: "+command)
			raise e




	#Debug string 
	@staticmethod
	def debugVM(vm):
		return " project:"+vm.project_id+", slice:"+vm.slice_id+", name:"+vm.name
	

	#Paths
	''' Returns the container directory for the VM in remote FS'''
	@staticmethod
	def getRemoteHdDirectory(vm):
		return  OXA_FILEHD_REMOTE_VMS+vm.project_id+"/"+vm.slice_id+"/"
	
	''' Returns the container directory for the VM in remote Cache, if used'''
	@staticmethod
	def getHdDirectory(vm):
		if FileFullHdManager.__useCache: 
			return  OXA_FILEHD_CACHE_VMS+vm.project_id+"/"+vm.slice_id+"/"
		else:
			return  OXA_FILEHD_REMOTE_VMS+vm.project_id+"/"+vm.slice_id+"/"
	
	''' Returns the path of the hd file in Cache, if used'''
	@staticmethod
	def getHdPath(vm):
		if FileFullHdManager.__useCache: 
			return OXA_FILEHD_CACHE_VMS+vm.project_id+"/"+vm.slice_id+"/"+vm.name+".img"
		else:
			return OXA_FILEHD_REMOTE_VMS+vm.project_id+"/"+vm.slice_id+"/"+vm.name+".img"
		
	''' Returns the path of the hd file in Remote'''
	@staticmethod
	def getRemoteHdPath(vm):
		return OXA_FILEHD_REMOTE_VMS+vm.project_id+"/"+vm.slice_id+"/"+vm.name+".img"
	
	''' Returns the path of the swap hd file in Cache, if used'''
	@staticmethod
	def getSwapPath(vm):
		if FileFullHdManager.__useCache: 
			return OXA_FILEHD_CACHE_VMS+vm.project_id+"/"+vm.slice_id+"/"+vm.name+"_swap"+".img"
		else:
			return OXA_FILEHD_REMOTE_VMS+vm.project_id+"/"+vm.slice_id+"/"+vm.name+"_swap"+".img"
			
	''' Returns the path of the swap hd file in Remote'''
	@staticmethod
	def getRemoteSwapPath(vm):
		return OXA_FILEHD_REMOTE_VMS+vm.project_id+"/"+vm.slice_id+"/"+vm.name+"_swap"+".img"
	
	''' Returns the path of the config file in Cache, if used'''
	@staticmethod
	def getConfigFilePath(vm):
		if FileFullHdManager.__useCache: 
			return OXA_FILEHD_CACHE_VMS+vm.project_id+"/"+vm.slice_id+"/"+vm.name+".conf"
		else:
			return OXA_FILEHD_REMOTE_VMS+vm.project_id+"/"+vm.slice_id+"/"+vm.name+".conf"
	
	''' Returns the path of the config file in Remote'''
	@staticmethod
	def getRemoteConfigFilePath(vm):
		return OXA_FILEHD_REMOTE_VMS+vm.project_id+"/"+vm.slice_id+"/"+vm.name+".conf"
			
	''' Returns the path of the temporally mounted Hd in the dom0 filesystem'''
	@staticmethod
	def getTmpMountedHdPath(vm):
		return OXA_FILEHD_HD_TMP_MP+vm.name+"_"+vm.uuid+"/"

	''' Returns the path of the templates origin''' 
	@staticmethod
	def getTemplatesPath(vm):
		if FileFullHdManager.__useCache: 
			return	OXA_FILEHD_CACHE_TEMPLATES
		else:
			return  OXA_FILEHD_REMOTE_TEMPLATES



	##Hooks
	'''Pre-start Hook'''
	@staticmethod
	def startHook(vm):
		if not FileFullHdManager.isVMinCacheFS(vm):
			FileFullHdManager.moveVMToCacheFS(vm)

	'''Pre-reboot Hook'''
	@staticmethod
	def rebootHook(vm):
		return

	'''Post-stop Hook'''
	@staticmethod
	def stopHook(vm):
		if FileFullHdManager.isVMinCacheFS(vm):
			FileFullHdManager.moveVMToRemoteFS(vm)



	##Hd management routines

	@staticmethod
	def __fileTemplateExistsOrImportFromRemote(filepath):
		
		#if Cache is not used skip
		if not FileFullHdManager.__useCache:
			return True	
	
		#Check cache
		if os.path.exists(OXA_FILEHD_CACHE_TEMPLATES+filepath):
			return True
		path = os.path.dirname(filepath)

		#Check remote	
		if os.path.exists(OXA_FILEHD_REMOTE_TEMPLATES+path):
			#import from remote to cache
			FileFullHdManager.logger.info("Importing image to cache directory:"+OXA_FILEHD_REMOTE_TEMPLATES+path+"->"+OXA_FILEHD_CACHE_TEMPLATES+path)
			try:
				#Copy all 
				FileFullHdManager.subprocessCall("/bin/cp "+ str(OXA_FILEHD_REMOTE_TEMPLATES+path)+" "+str(OXA_FILEHD_CACHE_TEMPLATES+path))
			except Exception as e:
				return False
			return True
		
		return False
	
	@staticmethod
	def clone(vm):

		##Check file existance in CACHE		
		#FileFullHdManager.logger.debug("Checking:"+FileFullHdManager.getHdPath(vm))
		if os.path.exists(FileFullHdManager.getHdPath(vm)):
			raise VMalreadyExists("Another VM with the same name exists in the same project and slice:"+FileFullHdManager.debugVM(vm))

		#FileFullHdManager.logger.debug("Checking:"+FileFullHdManager.getRemoteHdPath(vm))
		##Check file existance in REMOTE 
		if os.path.exists(FileFullHdManager.getRemoteHdPath(vm)):
			raise VMalreadyExists("Another VM with the same name exists in the same project and slice:"+FileFullHdManager.debugVM(vm))

		if FileFullHdManager.__fileTemplateExistsOrImportFromRemote(vm.xen_configuration.hd_origin_path):
			path= ""
			try:
				#TODO: user authentication 	
				template_path=FileFullHdManager.getTemplatesPath(vm)+vm.xen_configuration.hd_origin_path
				#template_swap_path=FileFullHdManager.getTemplatesPath(vm)+vm.xen_configuration.hd_origin_path+"_swap"
				vm_path=FileFullHdManager.getHdPath(vm)
				#swap_path=FileFullHdManager.getSwapPath(vm)

				FileFullHdManager.logger.debug("Trying to clone from:"+template_path+"->>"+vm_path)

				if not os.path.exists(os.path.dirname(vm_path)):	
					os.makedirs(os.path.dirname(vm_path))
				
				#Clone HD
				FileFullHdManager.subprocessCall("/bin/cp "+str(template_path)+" "+str(vm_path))
			
			except Exception as e:
				FileFullHdManager.logger.error("Could not clone image to working directory: "+str(e)) 
				raise Exception("Could not clone image to working directory"+FileFullHdManager.debugVM(vm))
				
		else:
			raise Exception("Could not find origin hard-disk to clone"+FileFullHdManager.debugVM(vm))	

	@staticmethod
	def delete(vm):
		if not FileFullHdManager.isVMinRemoteFS(vm):
			FileFullHdManager.moveVMToRemoteFS(vm)
		os.remove(FileFullHdManager.getRemoteHdPath(vm)) 
		#os.remove(FileFullHdManager.getRemoteSwapPath(vm)) 
		os.remove(FileFullHdManager.getRemoteConfigFilePath(vm)) 
			
	#Mount/umount routines
	@staticmethod
	def mount(vm):
		path = FileFullHdManager.getTmpMountedHdPath(vm)

		if not os.path.isdir(path):
			os.makedirs(path)		
	
		vm_path=FileFullHdManager.getHdPath(vm)
		if vm.xen_configuration.configurator == IratiDebianVMConfigurator.getIdentifier():
			FileFullHdManager.subprocessCall('/bin/mount -o loop,offset=44040192 '+str(vm_path)+" "+str(path))
                elif vm.xen_configuration.configurator == DebianWheezyVMConfigurator.getIdentifier():
                        #Is exactly the same as Irati Images but The current Wheezy VMs are being tested 
                        FileFullHdManager.subprocessCall('/bin/mount -o loop,offset=44040192 '+str(vm_path)+" "+str(path))	
		else:
			FileFullHdManager.subprocessCall('/bin/mount -o loop,offset=1048576 '+str(vm_path)+" "+str(path))	
	
		return path

	@staticmethod
	def umount(path):
		FileFullHdManager.subprocessCall('/bin/umount -d '+str(path))
		#remove dir
		os.removedirs(path)	
		

	#Cache-Remote warehouse methods 
	@staticmethod
	def isVMinRemoteFS(vm):
		return os.path.exists(FileFullHdManager.getRemoteHdPath(vm)) 
	
	@staticmethod
	def isVMinCacheFS(vm):
		return os.path.exists(FileFullHdManager.getHdPath(vm))
		
	@staticmethod
	def moveVMToRemoteFS(vm):
	
		#if Cache is not used skip
		if not FileFullHdManager.__useCache:
			return	
	
		if FileFullHdManager.isVMinCacheFS(vm): 
			#create dirs if do not exist already
			try:
				os.makedirs(FileFullHdManager.getRemoteHdDirectory(vm))
			except Exception as e:
				pass
			#Move all files
			shutil.move(FileFullHdManager.getHdPath(vm),FileFullHdManager.getRemoteHdPath(vm)) 
			#shutil.move(FileFullHdManager.getSwapPath(vm),FileFullHdManager.getRemoteSwapPath(vm))
			shutil.move(FileFullHdManager.getConfigFilePath(vm),FileFullHdManager.getRemoteConfigFilePath(vm)) 
		else:
			raise Exception("Cannot find VM in CACHE FS"+FileFullHdManager.debugVM(vm) )	
	
	@staticmethod
	def moveVMToCacheFS(vm):
		#if Cache is not used skip
		if not FileFullHdManager.__useCache:
			return	
	
		if FileFullHdManager.isVMinRemoteFS(vm): 

			if FileFullHdManager.isVMinCacheFS(vm): 
				raise Exception("Machine is already in Cache FS"+FileFullHdManager.debugVM(vm))
				
			#create dirs if do not exist already
			try:
				os.makedirs(FileFullHdManager.getHdDirectory(vm))
			except Exception as e:
				pass
	
			#Move all files
			shutil.move(FileFullHdManager.getRemoteHdPath(vm),FileFullHdManager.getHdPath(vm)) 
			#shutil.move(FileFullHdManager.getRemoteSwapPath(vm),FileFullHdManager.getSwapPath(vm))
			shutil.move(FileFullHdManager.getRemoteConfigFilePath(vm),FileFullHdManager.getConfigFilePath(vm))
			
		else:
			raise Exception("Cannot find VM in REMOTE FS"+FileFullHdManager.debugVM(vm))
	

