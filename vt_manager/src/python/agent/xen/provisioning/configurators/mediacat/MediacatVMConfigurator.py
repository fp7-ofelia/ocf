import shutil
import os
import jinja2 
import subprocess

from xen.provisioning.hdmanagers.LVMHdManager import LVMHdManager
from xen.provisioning.HdManager import HdManager
from settings.settingsLoader import OXA_XEN_SERVER_KERNEL,OXA_XEN_SERVER_INITRD,OXA_DEBIAN_INTERFACES_FILE_LOCATION,OXA_DEBIAN_UDEV_FILE_LOCATION

class MediacatVMConfigurator:

	''' Private methods '''
	@staticmethod
	def __createParavirtualizationVM(vm):
		swap = 0
                if len(vm.xen_configuration.users.user) == 1 and vm.xen_configuration.users.user[0].name == "root":
                        passwd = str(vm.xen_configuration.users.user[0].password)
		
		if vm.xen_configuration.memory_mb < 1024:
			swap = vm.xen_configuration.memory_mb*2
		else:
			swap = 1024
		
		p = subprocess.Popen(['/usr/bin/xen-create-image','--hostname=' + vm.name,'--size=' + str(vm.xen_configuration.hd_size_gb) + 'Gb','--swap=' + str(swap) + 'Mb','--memory=' + str(vm.xen_configuration.memory_mb) + 'Mb','--arch=amd64','--password=' + passwd,'--output=' + LVMHdManager.getConfigFileDir(vm), '--role=udev'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		p.wait()

	@staticmethod
        def __createHVMFileHdConfigFile(vm,env):
                template_name = "mediacatHVMFileHd.pt"
                template = env.get_template(template_name)

                #Set vars&render
                output = template.render(
                kernelImg=OXA_XEN_SERVER_KERNEL,
                initrdImg=OXA_XEN_SERVER_INITRD,
                vm=vm)

                #write file
                cfile = open(HdManager.getConfigFilePath(vm),'w')
                cfile.write(output)
		cfile.close()
	

	#Public methods	
	@staticmethod
	def getIdentifier():
		return	MediacatVMConfigurator.__name__ 

	@staticmethod
        def configureVmDisk(vm,path):
                return

	@staticmethod
	def createVmConfigurationFile(vm):
                #get env
                template_dirs = []
                template_dirs.append(os.path.join(os.path.dirname(__file__), 'templates/'))
                env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dirs))

		if vm.xen_configuration.hd_setup_type == "logical-volume-image" and vm.xen_configuration.virtualization_setup_type == "paravirtualization":
			MediacatVMConfigurator.__createParavirtualizationVM(vm)
		elif vm.xen_configuration.hd_setup_type == "logical-volume-image" and vm.xen_configuration.virtualization_setup_type == "hardware-assisted-virtualization":
                        MediacatVMConfigurator.__createHVMFileHdConfigFile(vm,env) 
		else:
			raise Exception("type of file or type of virtualization not supported for the creation of xen vm configuration file")	
	
