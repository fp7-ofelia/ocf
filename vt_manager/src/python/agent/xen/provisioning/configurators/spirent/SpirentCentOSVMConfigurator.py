import shutil
import os
import jinja2 
import string
import subprocess
import re

from xen.provisioning.HdManager import HdManager
from settings.settingsLoader import OXA_XEN_SERVER_KERNEL,OXA_XEN_SERVER_INITRD, OXA_REDHAT_INTERFACES_FILE_LOCATION,OXA_REDHAT_UDEV_FILE_LOCATION, OXA_REDHAT_HOSTNAME_FILE_LOCATION, OXA_DEBIAN_SECURITY_ACCESS_FILE_LOCATION, OXA_SPIRENT_NPORTS_PER_GROUP, OXA_SPIRENT_NTPSERVER, OXA_SPIRENT_NPORTGROUPS, OXA_SPIRENT_LSERVER, OXA_SPIRENT_STCA_INI_PATH, OXA_SPIRENT_ADMIN_CONF_PATH

from utils.Logger import Logger



class SpirentCentOSVMConfigurator:
	
	logger = Logger.getLogger()

	''' Private methods '''
	@staticmethod
	def __configureInterfacesFile(vm, path):
		#Interfaces
		for inter in vm.xen_configuration.interfaces.interface  :

			print "Processing interface:"+inter.name
			iFile =	open(path+OXA_REDHAT_INTERFACES_FILE_LOCATION+"ifcfg-"+inter.name, "w")

			if inter.ismgmt:
				interfaceString = "DEVICE="+inter.name+"\n"+\
					"HWADDR="+inter.mac+"\n"+\
					"TYPE=Ethernet\n"+\
					"BOOTPROTO=static\n"+\
					"ONBOOT=yes\n"+\
					"NM_CONTROLLED=yes\n"
	
				#is a mgmt interface
				interfaceString += "IPADDR="+inter.ip +"\n"+\
				"NETMASK="+inter.mask +"\n";

				if inter.dns1 != None and inter.dns1 != "":
					interfaceString +="DNS1="+inter.dns1+"\n"
					
				if inter.dns2 != None and inter.dns2 != "":
					interfaceString +="DNS2="+inter.dns2+"\n"
				
				if inter.gw != None and inter.gw != "":
					interfaceString +="GATEWAY="+inter.gw+"\n"
				interfaceString +="\n"
			else:
				interfaceString = "DEVICE="+inter.name+"\n"+\
					"HWADDR="+inter.mac+"\n"+\
					"TYPE=Ethernet\n"+\
					"ONBOOT=no\n"+\
					"NM_CONTROLLED=yes\n"+\
					"BOOTPROTO=dhcp\n"
				
			iFile.write(interfaceString)			 
			os.close(iFile)
			
			print "Processing interface:"+inter.name+"FINISHED"

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

	@staticmethod
	def __configureTestPorts(vm, configFile):
		configString = "[CFG]\n"
		#Interfaces
		for inter in vm.xen_configuration.interfaces.interface  :

			if inter.ismgmt:
				#is a mgmt interface
				configString += "ADMIN_PORT="+inter.name+"\n"
			else:
				configString += "TEST_PORT="+inter.name+"\n"

		configFile.write(configString+"[END]")			 

	@staticmethod
	def __configureAdmin(vm, configFile):
		configString = ""
		gwString = ""
		for iface in vm.xen_configuration.interfaces.interface:
			if iface.ismgmt:
				inter = iface;
				break;

		if OXA_SPIRENT_NPORTS_PER_GROUP == "":
			raise Exception("OXA_SPIRENT_NPORTS_PER_GROUP variable not set")
		configString += "NPORTS_PER_GROUP="+OXA_SPIRENT_NPORTS_PER_GROUP+"\n"
		if OXA_SPIRENT_NTPSERVER == "":
			raise Exception("OXA_SPIRENT_NTPSERVER variable not set")
		configString += "NTPSERVER="+OXA_SPIRENT_NTPSERVER+"\n"
		configString += "HOSTNAME="+vm.name+"\n"
		configString +=	"IPADDR="+inter.ip+"\n"
		configString += "PROMISC=on\n"
		configString += "DRIVERMODE=sockets\n"
		configString += "NETMASK="+inter.mask+"\n"
		configString += "ADDR_MODE=static\n"
		configString += "PORT_SPEED=1000M\n"
		configString += "DEVICE="+inter.name+"\n"
		if OXA_SPIRENT_NPORTGROUPS == "":
			raise Exception("OXA_SPIRENT_NPORTGROUPS variable not set")
		configString += "NPORTGROUPS="+OXA_SPIRENT_NPORTGROUPS+"\n"
		if OXA_SPIRENT_LSERVER == "":
			raise Exception("OXA_SPIRENT_LSERVER variable not set")
		configString += "LSERVERP="+OXA_SPIRENT_LSERVER+"\n"
		if inter.gw != None:
			gwString = inter.gw
		configString += "GATEWAY="+gwString+"\n"

		configFile.write(configString)
			

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
				os.system("rm -f "+path+"/"+OXA_REDHAT_INTERFACES_FILE_LOCATION+"ifcfg-eth*") 
				SpirentCentOSVMConfigurator.__configureInterfacesFile(vm, path)
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
		configPath = OXA_SPIRENT_STCA_INI_PATH 
		try:
			with open(path+configPath,'w') as configFile:
				SpirentCentOSVMConfigurator.__configureTestPorts(vm, configFile)
		except Exception as e:
			SpirentCentOSVMConfigurator.logger.error("Could not configure test ports... - "+str(e))
			raise e

	
	@staticmethod
	def _configureAdmin(vm,path):
		configPath = OXA_SPIRENT_ADMIN_CONF_PATH
		try:
			with open(path+configPath,'w') as configFile:
				SpirentCentOSVMConfigurator.__configureAdmin(vm, configFile)
		except Exception as e:
			SpirentCentOSVMConfigurator.logger.error("Could not configure admin file... - "+str(e))
			raise e

	#Public methods
	@staticmethod
	def createVmConfigurationFile(vm):

		#get env
		template_dirs = []
		template_dirs.append(os.path.join(os.path.dirname(__file__),'templates/'))
		env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dirs))
		if vm.xen_configuration.hd_setup_type == "full-file-image" and vm.xen_configuration.virtualization_setup_type == "hvm" :
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
		#SpirentCentOSVMConfigurator._configureTestPorts(vm,path)
		SpirentCentOSVMConfigurator.logger.info("Test-ports configured successfully...")

		#Configure Admin file
		#SpirentCentOSVMConfigurator._configureAdmin(vm,path)
		SpirentCentOSVMConfigurator.logger.info("Admin file configured successfully...")
