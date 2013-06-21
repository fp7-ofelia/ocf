import shutil
import os
import jinja2 
import string
import subprocess
import re

from xen.provisioning.HdManager import HdManager
from settings.settingsLoader import OXA_XEN_SERVER_KERNEL, OXA_XEN_SERVER_INITRD, OXA_REDHAT_INTERFACES_FILE_LOCATION, OXA_REDHAT_UDEV_FILE_LOCATION, OXA_REDHAT_HOSTNAME_FILE_LOCATION, OXA_DEBIAN_SECURITY_ACCESS_FILE_LOCATION
from utils.Logger import Logger



class SpirentCentOSVMConfigurator:
	
	logger = Logger.getLogger()

	''' Private methods '''
	@staticmethod
	def __configureInterfacesFile(vm, path):
		#Interfaces
		for inter in vm.xen_configuration.interfaces.interface  :
			iFile = os.open(path+OXA_REDHAT_INTERFACES_LOCATION+"ifcfg-"+inter.name, w)

			interfaceString = "DEVICE="+inter.name+"\n"+\
					"HWADDR="+inter.mac+"\n"+\
					"BOOTPROTO=none\nONBOOT=yes\nUSERCTL=no\n"
				
			if inter.ismgmt:
				#is a mgmt interface
				interfaceString += "IPADDR="+inter.ip +"\n"+\
				"NETMASK="+inter.mask +"\n";

				if inter.gw != None and inter.gw != "":
					interfaceString +="GATEWAY="+inter.gw+"\n"
				interfaceString +="\n"

				
			iFile.write(interfaceString)			 
			os.close(iFile)

	@staticmethod
	def __configureHostname(vm,hFile):
		hFile.write(vm.name)		
	
	
	@staticmethod
	def __createConfigFile(vm,env):
                template_name = "spirentSTCVMTemplate.pt"
               	template = env.get_template(template_name)	

		#Set vars&render		
		output = template.render(
		kernelImg=OXA_XEN_SERVER_KERNEL,
		initrdImg=OXA_XEN_SERVER_INITRD,
		hdFilePath=HdManager.getHdPath(vm),
		#swapFilePath=HdManager.getSwapPath(vm),
		vm=vm)	
			
		#write file
		cfile = open(HdManager.getConfigFilePath(vm),'w')
		cfile.write(output)
		cfile.close()



	''' Public methods '''

	@staticmethod
	def getIdentifier():
		return	SpirentCentOSVMConfigurator.__name__ 

	@staticmethod
	def _configureNetworking(vm,path):
		#Configure interfaces
		try:
			try:
				#Remove all files under/etc/sysconfig/network-scripts/ifcfg-*
				os.system("rm -f "+path+"/"+OXA_REDHAT_INTERFACES_LOCATION+"ifcfg-*")			 
				SpirentCentOSVMConfigurator.__configureInterfacesFiles(vm, path)
			except Exception as e:
				pass

		except Exception as e:
			SpirentCentOSVMConfigurator.logger.error(str(e))
			raise Exception("Could not configure interfaces")

	@staticmethod
	def _configureHostName(vm,path):
		try:
			with open(path+OXA_REDHAT_HOSTNAME_FILE_LOCATION,'w') as openhost:
				SpirentCentOSVMConfigurator.__configureHostname(vm, openhost)
		except Exception as e:
			SpirentCentOSVMConfigurator.logger.error("Could not configure hostname;skipping.. - "+str(e))

	@staticmethod
	def _configureTestPorts(vm,path):
		try:
			pass	
		except Exception as e:
			SpirentCentOSVMConfigurator.logger.error("Could not configure test ports... - "+str(e))
			raise e

	

	#Public methods
	@staticmethod
	def createVmConfigurationFile(vm):

		#get env
		template_dirs = []
		template_dirs.append(os.path.join(os.path.dirname(__file__),'../templates/'))
		env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dirs))
		if vm.xen_configuration.hd_setup_type == "file-full-image" and vm.xen_configuration.virtualization_setup_type == "hvm" :
			SpirentCentOSVMConfigurator.__createConfigFile(vm,env)
		else:
			raise Exception("type of file or type of virtualization not supported for the creation of xen vm configuration file")	

	@staticmethod
	def configureVmDisk(vm, path):
		
		if not path or not re.match(r'[\s]*\/\w+\/\w+\/.*', path,re.IGNORECASE): #For security, should never happen anyway
			raise Exception("Incorrect vm path")

		#Configure networking
		SpirentCentOSVMConfigurator._configureNetworking(vm,path)
		SpirentCentOSVMConfigurator.logger.info("Network configured successfully...")
		
		#Configure Hostname
		SpirentCentOSVMConfigurator._configureHostName(vm,path)
		SpirentCentOSVMConfigurator.logger.info("Hostname configured successfully...")

		#Configure Test-Ports
		SpirentCentOSVMConfigurator._configureTestPorts(vm,path)
		SpirentCentOSVMConfigurator.logger.info("Test-ports configured successfully...")
