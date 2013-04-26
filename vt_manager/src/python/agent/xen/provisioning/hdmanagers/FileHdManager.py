import os
import sys
import shutil
import string
import subprocess
import re
from settings.settingsLoader import OXA_FILEHD_CACHE_VMS,OXA_FILEHD_REMOTE_VMS,OXA_FILEHD_CACHE_TEMPLATES,OXA_FILEHD_REMOTE_TEMPLATES,OXA_FILEHD_USE_CACHE,OXA_FILEHD_NICE_PRIORITY,OXA_FILEHD_CREATE_SPARSE_DISK,OXA_FILEHD_IONICE_CLASS, OXA_FILEHD_IONICE_PRIORITY,OXA_FILEHD_DD_BS_KB, OXA_DEFAULT_SWAP_SIZE_MB
from utils.AgentExceptions import *
from utils.Logger import Logger

'''
	@author: msune

	File-type Hd management routines
'''

OXA_FILEHD_HD_TMP_MP="/tmp/oxa/hd"

class FileHdManager(object):
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
			FileHdManager.logger.debug("Executing: "+wrappedCmd) 
			subprocess.check_call(wrappedCmd, shell=True, stdout=stdout)
		except Exception as e:
			FileHdManager.logger.error("Unable to execute command: "+command)
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
		if FileHdManager.__useCache: 
			return  OXA_FILEHD_CACHE_VMS+vm.project_id+"/"+vm.slice_id+"/"
		else:
			return  OXA_FILEHD_REMOTE_VMS+vm.project_id+"/"+vm.slice_id+"/"
	
	''' Returns the path of the hd file in Cache, if used'''
	@staticmethod
	def getHdPath(vm):
		if FileHdManager.__useCache: 
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
		if FileHdManager.__useCache: 
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
		if FileHdManager.__useCache: 
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
		if FileHdManager.__useCache: 
			return	OXA_FILEHD_CACHE_TEMPLATES
		else:
			return  OXA_FILEHD_REMOTE_TEMPLATES



	##Hooks
	'''Pre-start Hook'''
	@staticmethod
	def startHook(vm):
		if not FileHdManager.isVMinCacheFS(vm):
			FileHdManager.moveVMToCacheFS(vm)

	'''Pre-reboot Hook'''
	@staticmethod
	def rebootHook(vm):
		return

	'''Post-stop Hook'''
	@staticmethod
	def stopHook(vm):
		if FileHdManager.isVMinCacheFS(vm):
			FileHdManager.moveVMToRemoteFS(vm)



	##Hd management routines

	@staticmethod
	def __fileTemplateExistsOrImportFromRemote(filepath):
		
		#if Cache is not used skip
		if not FileHdManager.__useCache:
			return True	
	
		#Check cache
		if os.path.exists(OXA_FILEHD_CACHE_TEMPLATES+filepath):
			return True
		path = os.path.dirname(filepath)

		#Check remote	
		if os.path.exists(OXA_FILEHD_REMOTE_TEMPLATES+path):
			#import from remote to cache
			FileHdManager.logger.info("Importing image to cache directory:"+OXA_FILEHD_REMOTE_TEMPLATES+path+"->"+OXA_FILEHD_CACHE_TEMPLATES+path)
			try:
				#Copy all 
				FileHdManager.subprocessCall("/bin/cp "+ str(OXA_FILEHD_REMOTE_TEMPLATES+path)+" "+str(OXA_FILEHD_CACHE_TEMPLATES+path))
			except Exception as e:
				return False
			return True
		
		return False
	
	@staticmethod
	def clone(vm):

		##Check file existance in CACHE		
		#FileHdManager.logger.debug("Checking:"+FileHdManager.getHdPath(vm))
		if os.path.exists(FileHdManager.getHdPath(vm)):
			raise VMalreadyExists("Another VM with the same name exists in the same project and slice:"+FileHdManager.debugVM(vm))

		#FileHdManager.logger.debug("Checking:"+FileHdManager.getRemoteHdPath(vm))
		##Check file existance in REMOTE 
		if os.path.exists(FileHdManager.getRemoteHdPath(vm)):
			raise VMalreadyExists("Another VM with the same name exists in the same project and slice:"+FileHdManager.debugVM(vm))

		if FileHdManager.__fileTemplateExistsOrImportFromRemote(vm.xen_configuration.hd_origin_path):
			path= ""
			try:
				#TODO: user authentication 	
				template_path=FileHdManager.getTemplatesPath(vm)+vm.xen_configuration.hd_origin_path
				template_swap_path=FileHdManager.getTemplatesPath(vm)+vm.xen_configuration.hd_origin_path+"_swap"
				vm_path=FileHdManager.getHdPath(vm)
				swap_path=FileHdManager.getSwapPath(vm)

				FileHdManager.logger.debug("Trying to clone from:"+template_path+"->>"+vm_path)

				if not os.path.exists(os.path.dirname(vm_path)):	
					os.makedirs(os.path.dirname(vm_path))
				
				count = (vm.xen_configuration.hd_size_mb*1024)/OXA_FILEHD_DD_BS_KB
				if (vm.xen_configuration.hd_size_mb*1024)/OXA_FILEHD_DD_BS_KB > 0:
					FileHdManager.logger.warning("HD size will be normalized")
				count =int(count) 	
				
				#Create HD
				FileHdManager.logger.info("Creating disks...")
				if OXA_FILEHD_CREATE_SPARSE_DISK:
					FileHdManager.logger.info("Main disk will be created as Sparse disk...")
					FileHdManager.subprocessCall("/bin/dd if=/dev/zero of="+str(vm_path)+" bs="+str(OXA_FILEHD_DD_BS_KB)+"k count=1 seek="+str(count))
				else:
					FileHdManager.subprocessCall("/bin/dd if=/dev/zero of="+str(vm_path)+" bs="+str(OXA_FILEHD_DD_BS_KB)+"k count="+str(count))
				
				#Create Swap and mkswap
				FileHdManager.logger.info("Creating swap disk...")
				swapCount=int((OXA_DEFAULT_SWAP_SIZE_MB*1024)/OXA_FILEHD_DD_BS_KB)
				FileHdManager.subprocessCall("/bin/dd if=/dev/zero of="+str(swap_path)+" bs="+str(OXA_FILEHD_DD_BS_KB)+"k count="+str(swapCount))
				FileHdManager.logger.info("Creating swap filesystem...")
				FileHdManager.subprocessCall("/sbin/mkswap "+str(swap_path))
					
				#Format 
				FileHdManager.logger.info("Creating EXT3 fs...")
				FileHdManager.subprocessCall("/sbin/mkfs.ext3 -F -q "+str(vm_path))
					
				#Untar disk contents
				FileHdManager.logger.info("Uncompressing disk contents...")
				path = FileHdManager.mount(vm) #mount
				with open(os.devnull, 'w') as opendev:
					FileHdManager.subprocessCall("/bin/tar -xvf "+str(template_path)+" -C "+str(path),stdout=opendev)
					
			except Exception as e:
				FileHdManager.logger.error("Could not clone image to working directory: "+str(e)) 
				raise Exception("Could not clone image to working directory"+FileHdManager.debugVM(vm))
			finally:
				try:
					FileHdManager.umount(path)
				except:
					pass
				
		else:
			raise Exception("Could not find origin hard-disk to clone"+FileHdManager.debugVM(vm))	

	@staticmethod
	def delete(vm):
		if not FileHdManager.isVMinRemoteFS(vm):
			FileHdManager.moveVMToRemoteFS(vm)
		os.remove(FileHdManager.getRemoteHdPath(vm)) 
		os.remove(FileHdManager.getRemoteSwapPath(vm)) 
		os.remove(FileHdManager.getRemoteConfigFilePath(vm)) 
			
	#Mount/umount routines
	@staticmethod
	def mount(vm):
		path = FileHdManager.getTmpMountedHdPath(vm)

		if not os.path.isdir(path):
			os.makedirs(path)		
	
		vm_path=FileHdManager.getHdPath(vm)
		FileHdManager.subprocessCall('/bin/mount -o loop '+str(vm_path)+" "+str(path))	
	
		return path

	@staticmethod
	def umount(path):
		FileHdManager.subprocessCall('/bin/umount -d '+str(path))
		#remove dir
		os.removedirs(path)	
		

	#Cache-Remote warehouse methods 
	@staticmethod
	def isVMinRemoteFS(vm):
		return os.path.exists(FileHdManager.getRemoteHdPath(vm)) 
	
	@staticmethod
	def isVMinCacheFS(vm):
		return os.path.exists(FileHdManager.getHdPath(vm))
		
	@staticmethod
	def moveVMToRemoteFS(vm):
	
		#if Cache is not used skip
		if not FileHdManager.__useCache:
			return	
	
		if FileHdManager.isVMinCacheFS(vm): 
			#create dirs if do not exist already
			try:
				os.makedirs(FileHdManager.getRemoteHdDirectory(vm))
			except Exception as e:
				pass
			#Move all files
			shutil.move(FileHdManager.getHdPath(vm),FileHdManager.getRemoteHdPath(vm)) 
			shutil.move(FileHdManager.getSwapPath(vm),FileHdManager.getRemoteSwapPath(vm))
			shutil.move(FileHdManager.getConfigFilePath(vm),FileHdManager.getRemoteConfigFilePath(vm)) 
		else:
			raise Exception("Cannot find VM in CACHE FS"+FileHdManager.debugVM(vm) )	
	
	@staticmethod
	def moveVMToCacheFS(vm):
		#if Cache is not used skip
		if not FileHdManager.__useCache:
			return	
	
		if FileHdManager.isVMinRemoteFS(vm): 

			if FileHdManager.isVMinCacheFS(vm): 
				raise Exception("Machine is already in Cache FS"+FileHdManager.debugVM(vm))
				
			#create dirs if do not exist already
			try:
				os.makedirs(FileHdManager.getHdDirectory(vm))
			except Exception as e:
				pass
	
			#Move all files
			shutil.move(FileHdManager.getRemoteHdPath(vm),FileHdManager.getHdPath(vm)) 
			shutil.move(FileHdManager.getRemoteSwapPath(vm),FileHdManager.getSwapPath(vm))
			shutil.move(FileHdManager.getRemoteConfigFilePath(vm),FileHdManager.getConfigFilePath(vm))
			
		else:
			raise Exception("Cannot find VM in REMOTE FS"+FileHdManager.debugVM(vm))
	

