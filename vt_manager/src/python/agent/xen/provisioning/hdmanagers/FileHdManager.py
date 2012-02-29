import os
import sys
import shutil
import string
import subprocess
from settings.settingsLoader import OXA_FILEHD_CACHE_VMS,OXA_FILEHD_REMOTE_VMS,OXA_FILEHD_CACHE_TEMPLATES,OXA_FILEHD_REMOTE_TEMPLATES,OXA_FILEHD_USE_CACHE,OXA_FILEHD_COPY_OPERATIONS_NICE_PRIORITY,OXA_FILEHD_CREATE_SPARSE_DISK,OXA_FILEHD_COPY_IONICE_CLASS, OXA_FILEHD_COPY_IONICE_PRIORITY

'''
	@author: msune

	File-type Hd management routines
'''

OXA_FILEHD_HD_TMP_MP="/tmp/oxa/hd"

class FileHdManager(object):

	#Enables/disables the usage of Cache directory
	__useCache=OXA_FILEHD_USE_CACHE

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
			print "Importing image to cache directory:"+OXA_FILEHD_REMOTE_TEMPLATES+path+"->"+OXA_FILEHD_CACHE_TEMPLATES+path
			try:
				#Copy all 
				#shutil.copytree(OXA_FILEHD_REMOTE_TEMPLATES+path, OXA_FILEHD_CACHE_TEMPLATES+path)
				print "/bin/cp "+OXA_FILEHD_REMOTE_TEMPLATES+path+" "+OXA_FILEHD_CACHE_TEMPLATES+path
				if subprocess.call(["/usr/bin/ionice", "-c", OXA_FILEHD_COPY_IONICE_CLASS, "-n", OXA_FILEHD_COPY_IONICE_PRIORITY,"/bin/cp",OXA_FILEHD_REMOTE_TEMPLATES+path, OXA_FILEHD_CACHE_TEMPLATES+path], preexec_fn=lambda : os.nice(OXA_FILEHD_COPY_OPERATIONS_NICE_PRIORITY)) > 0:
					raise Exception("Cannot import template")

				
			except Exception as e:
				return False
			return True
		
		return False
	
	@staticmethod
	def clone(vm):

		##Check file existance in CACHE		
		if os.path.exists(FileHdManager.getHdPath(vm)):
			raise Exception("Another VM with the same name exists in the same project and slice:"+FileHdManager.debugVM(vm))

		if os.path.exists(FileHdManager.getRemoteHdPath(vm)):
			raise Exception("Another VM with the same name exists in the same project and slice:"+FileHdManager.debugVM(vm))

		if FileHdManager.__fileTemplateExistsOrImportFromRemote(vm.xen_configuration.hd_origin_path):
			path= ""
			try:
				#TODO: user authentication 	
				template_path=FileHdManager.getTemplatesPath(vm)+vm.xen_configuration.hd_origin_path
				template_swap_path=FileHdManager.getTemplatesPath(vm)+vm.xen_configuration.hd_origin_path+"_swap"
				vm_path=FileHdManager.getHdPath(vm)
				swap_path=FileHdManager.getSwapPath(vm)

				print "Trying to clone from:"+template_path+"->>"+vm_path

				if not os.path.exists(os.path.dirname(vm_path)):	
					os.makedirs(os.path.dirname(vm_path))
				
				size = (vm.xen_configuration.hd_size_mb/1024)*1024
				if vm.xen_configuration.hd_size_mb %1024 > 0:
					print "[Warning] HD size is not multiple of 1024; will be modified to:"+str(size)
				
				#Create HD
				print "Creating disks..."
				if OXA_FILEHD_CREATE_SPARSE_DISK:
					print "Main disk will be created as Sparse disk..."
					if subprocess.call(["/usr/bin/ionice", "-c", str(OXA_FILEHD_COPY_IONICE_CLASS), "-n", str(OXA_FILEHD_COPY_IONICE_PRIORITY), "/bin/dd","if=/dev/zero","of="+vm_path,"bs=1M","count=1","seek="+str(size)], preexec_fn=lambda : os.nice(OXA_FILEHD_COPY_OPERATIONS_NICE_PRIORITY)) > 0:
						print "Failed to create Disk"
						raise Exception("")
				else:
					if subprocess.call(["/usr/bin/ionice", "-c", str(OXA_FILEHD_COPY_IONICE_CLASS), "-n", str(OXA_FILEHD_COPY_IONICE_PRIORITY),"/bin/dd","if=/dev/zero","of="+vm_path,"bs=1M","count="+str(size)], preexec_fn=lambda : os.nice(OXA_FILEHD_COPY_OPERATIONS_NICE_PRIORITY)) > 0:
						print "Failed to create Disk"
						raise Exception("")
				
				#Create Swap
				if subprocess.call(["/usr/bin/ionice", "-c", str(OXA_FILEHD_COPY_IONICE_CLASS), "-n", str(OXA_FILEHD_COPY_IONICE_PRIORITY),"/bin/dd","if=/dev/zero","of="+swap_path,"bs=1M","count=512"], preexec_fn=lambda : os.nice(OXA_FILEHD_COPY_OPERATIONS_NICE_PRIORITY)) > 0:
					print "Failed to create Swap"
					raise Exception("")
				#Format
				print "Creating EXT3 fs..."
				if subprocess.call(["/usr/bin/ionice", "-c", str(OXA_FILEHD_COPY_IONICE_CLASS), "-n", str(OXA_FILEHD_COPY_IONICE_PRIORITY),"/sbin/mkfs.ext3","-F","-q",vm_path], preexec_fn=lambda : os.nice(OXA_FILEHD_COPY_OPERATIONS_NICE_PRIORITY)) > 0:
					print "Failed to format disk" 
					raise Exception("")
				
				#Untar disk contents
				print "Uncompressing disk contents..."
				path = FileHdManager.mount(vm)
				with open(os.devnull, 'w') as opendev:
					if subprocess.call(["/usr/bin/ionice", "-c", str(OXA_FILEHD_COPY_IONICE_CLASS), "-n", str(OXA_FILEHD_COPY_IONICE_PRIORITY),"/bin/tar","-xvf",template_path,"-C",path],stdout=opendev, preexec_fn=lambda : os.nice(OXA_FILEHD_COPY_OPERATIONS_NICE_PRIORITY)) > 0:
						print "Failed to uncompress disk contents"
						raise Exception("")
					
			except Exception as e:
				print e 
				raise Exception("Could not clone image to working directory"+FileHdManager.debugVM(vm))
			finally:
				FileHdManager.umount(path)
				
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
		#print '/bin/mount'+' -o loop '+vm_path+" "+path
		subprocess.call(['/bin/mount','-o','loop',vm_path,path])	
	
		return path

	@staticmethod
	def umount(path):
		subprocess.call(['/bin/umount',path])	
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
	

