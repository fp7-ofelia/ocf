import shutil
import os
import jinja2 

from xen.provisioning.HdManager import HdManager
from settings import OXA_DEBIANCONF_XEN_SERVER_KERNEL,OXA_DEBIANCONF_XEN_SERVER_INITRD,OXA_DEBIANCONF_DEBIAN_INTERFACES_FILE_LOCATION,OXA_DEBIANCONF_DEBIAN_UDEV_FILE_LOCATION

class DebianVMConfigurator:

	''' Private methods '''
	@staticmethod
	def __configureInterfacesFile(vm,iFile):
		#Loopback
		iFile.write("auto lo\niface lo inet loopback\n\n")
		#Interfaces
		for inter in vm.xen_configuration.interfaces.interface  :
			if inter.ismgmt:
				#is a mgmt interface
				iFile.write(
				"auto "+inter.name+"\n"+
				"iface "+inter.name+" inet static\n"+
				"\taddress "+inter.ip +"\n"+
				"\tnetmask "+inter.mask+"\n"+
				"\tgateway "+inter.gw+"\n"+
				"\tdns-nameservers "+inter.dns1+" "+inter.dns2+"\n\n"
				) 
			else:
				iFile.write("auto "+inter.name)

	@staticmethod
	def __configureUdevFile(vm,uFile):
		for inter in vm.xen_configuration.interfaces.interface:
			uFile.write('SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="'+inter.mac+'", ATTR{dev_id}=="0x0", ATTR{type}=="1", KERNEL=="eth*", NAME="'+inter.name+'"\n')

	
	@staticmethod
	def __createParavirtualizationFileHdConfigFile(vm,env):
                template_name = "paraVirtualizedFileHd.pt"
                template = env.get_template(template_name)	

		#Set vars&render		
		output = template.render(
		kernelImg=OXA_DEBIANCONF_XEN_SERVER_KERNEL,
		initrdImg=OXA_DEBIANCONF_XEN_SERVER_INITRD,
		hdFilePath=HdManager.getHdPath(vm),
		swapFilePath=HdManager.getSwapPath(vm),
		vm=vm)	
			
		#write file
		cfile = open(HdManager.getConfigFilePath(vm),'w')
		cfile.write(output)

	''' Public methods '''
	@staticmethod
	def configureNetworking(vm,path):
		#Configure interfaces and udev settings	
		try:

			try:
				#Backup current files
				shutil.copy(path+OXA_DEBIANCONF_DEBIAN_INTERFACES_FILE_LOCATION,path+OXA_DEBIANCONF_DEBIAN_INTERFACES_FILE_LOCATION+".bak")	
				shutil.copy(path+OXA_DEBIANCONF_DEBIAN_UDEV_FILE_LOCATION,path+OXA_DEBIANCONF_DEBIAN_UDEV_FILE_LOCATION+".bak")
			except Exception as e:
				pass

			DebianVMConfigurator.__configureInterfacesFile(vm,open(path+OXA_DEBIANCONF_DEBIAN_INTERFACES_FILE_LOCATION,'w'))
			DebianVMConfigurator.__configureUdevFile(vm,open(path+OXA_DEBIANCONF_DEBIAN_UDEV_FILE_LOCATION,'w'))
		except Exception as e:
			print e
			raise Exception("Could not configure interfaces or Udev file")

	@staticmethod
	def configureLDAPSettings(vm,path):
		pass


	@staticmethod
	def createVmConfigurationFile(vm):

		#get env
		template_dirs = []
		template_dirs.append(os.path.join(os.path.dirname(__file__), 'templates/'))
		env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dirs))

		if vm.xen_configuration.hd_setup_type == "file-image" and vm.xen_configuration.virtualization_setup_type == "paravirtualization" :
			DebianVMConfigurator.__createParavirtualizationFileHdConfigFile(vm,env)
		else:
			raise Exception("type of file or type of virtualization not supported for the creation of xen vm configuration file")	
		
