import shutil
import os
import jinja2 
import string

from xen.provisioning.HdManager import HdManager
from settings.settingsLoader import OXA_XEN_SERVER_KERNEL,OXA_XEN_SERVER_INITRD,OXA_DEBIAN_INTERFACES_FILE_LOCATION,OXA_DEBIAN_UDEV_FILE_LOCATION, OXA_DEBIAN_HOSTNAME_FILE_LOCATION, OXA_DEBIAN_SECURITY_ACCESS_FILE_LOCATION
from utils.Logger import Logger


class OfeliaVMConfigurator:
	
	logger = Logger.getLogger()

	''' Private methods '''
	@staticmethod
	def __configureInterfacesFile(vm,iFile):
		#Loopback
		iFile.write("auto lo\niface lo inet loopback\n\n")
		#Interfaces
		for inter in vm.xen_configuration.interfaces.interface  :
			if inter.ismgmt:
				#is a mgmt interface
				interfaceString = "auto "+inter.name+"\n"+\
				"iface "+inter.name+" inet static\n"+\
				"\taddress "+inter.ip +"\n"+\
				"\tnetmask "+inter.mask+"\n"

				if inter.gw != None and inter.gw != "":
					interfaceString +="\tgateway "+inter.gw+"\n"

				if inter.dns1 != None and inter.dns1 != "":
					interfaceString+="\tdns-nameservers "+inter.dns1

					if inter.dns2 != None and inter.dns2 != "":
						interfaceString+=" "+inter.dns2
				interfaceString +="\n\n"

				iFile.write(interfaceString)			 
			else:
				#is a data interface
				iFile.write("auto "+inter.name+"\n\n")


	@staticmethod
	def __configureUdevFile(vm,uFile):
		for inter in vm.xen_configuration.interfaces.interface:
			uFile.write('SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="'+inter.mac+'", ATTR{dev_id}=="0x0", ATTR{type}=="1", KERNEL=="eth*", NAME="'+inter.name+'"\n')

	@staticmethod
	def __configureHostname(vm,hFile):
		hFile.write(vm.name)		
	
	
	@staticmethod
	def __createParavirtualizationFileHdConfigFile(vm,env):
                template_name = "paraVirtualizedFileHd.pt"
                template = env.get_template(template_name)	

		#Set vars&render		
		output = template.render(
		kernelImg=OXA_XEN_SERVER_KERNEL,
		initrdImg=OXA_XEN_SERVER_INITRD,
		hdFilePath=HdManager.getHdPath(vm),
		swapFilePath=HdManager.getSwapPath(vm),
		vm=vm)	
			
		#write file
		cfile = open(HdManager.getConfigFilePath(vm),'w')
		cfile.write(output)
		cfile.close()



	''' Public methods '''

	@staticmethod
	def getIdentifier():
		return	OfeliaVMConfigurator.__name__ 

	@staticmethod
	def configureNetworking(vm,path):
		#Configure interfaces and udev settings	
		try:

			try:
				#Backup current files
				shutil.copy(path+OXA_DEBIAN_INTERFACES_FILE_LOCATION,path+OXA_DEBIAN_INTERFACES_FILE_LOCATION+".bak")	
				shutil.copy(path+OXA_DEBIAN_UDEV_FILE_LOCATION,path+OXA_DEBIAN_UDEV_FILE_LOCATION+".bak")
			except Exception as e:
				pass

			with open(path+OXA_DEBIAN_INTERFACES_FILE_LOCATION,'w') as openif:
				OfeliaVMConfigurator.__configureInterfacesFile(vm,openif)
			with open(path+OXA_DEBIAN_UDEV_FILE_LOCATION,'w') as openudev:
				OfeliaVMConfigurator.__configureUdevFile(vm,openudev)
		except Exception as e:
			OfeliaVMConfigurator.logger.error(str(e))
			raise Exception("Could not configure interfaces or Udev file")

	@staticmethod
	def configureLDAPSettings(vm,path):
		try:
			file = open(path+OXA_DEBIAN_SECURITY_ACCESS_FILE_LOCATION, "r")
			text = file.read() 
			file.close() 
			file = open(path+OXA_DEBIAN_SECURITY_ACCESS_FILE_LOCATION, "w")
			#Scape spaces and tabs
		        projectName = string.replace(vm.project_name,' ','_')
			projectName = string.replace(projectName,'\t','__')
			file.write(text.replace("__projectId","@proj_"+vm.project_id+"_"+projectName))
			file.close() 
		except Exception as e:
			OfeliaVMConfigurator.logger.error("Could not configure LDAP file!! - "+str(e))

	@staticmethod
	def configureHostname(vm,path):
		try:
			with open(path+OXA_DEBIAN_HOSTNAME_FILE_LOCATION,'w') as openhost:
				OfeliaVMConfigurator.__configureHostname(vm, openhost)
		except Exception as e:
			OfeliaVMConfigurator.logger.error("Could not configure hostname;skipping.. - "+str(e))

	@staticmethod
	def createVmConfigurationFile(vm):

		#get env
		template_dirs = []
		template_dirs.append(os.path.join(os.path.dirname(__file__), 'templates/'))
		env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dirs))

		if vm.xen_configuration.hd_setup_type == "file-image" and vm.xen_configuration.virtualization_setup_type == "paravirtualization" :
			OfeliaVMConfigurator.__createParavirtualizationFileHdConfigFile(vm,env)
		else:
			raise Exception("type of file or type of virtualization not supported for the creation of xen vm configuration file")	
	
