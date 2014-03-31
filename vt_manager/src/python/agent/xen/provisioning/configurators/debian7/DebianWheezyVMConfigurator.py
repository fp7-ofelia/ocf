import shutil
import os
import jinja2 
import string
import subprocess
import re

from xen.provisioning.HdManager import HdManager
from settings.settingsLoader import OXA_XEN_SERVER_KERNEL,OXA_XEN_SERVER_INITRD,OXA_DEBIAN_INTERFACES_FILE_LOCATION,OXA_DEBIAN_UDEV_FILE_LOCATION, OXA_DEBIAN_HOSTNAME_FILE_LOCATION, OXA_DEBIAN_SECURITY_ACCESS_FILE_LOCATION
from utils.Logger import Logger


class DebianWheezyVMConfigurator:
	
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
	def __createFullvirtualizationFileHdConfigFile(vm,env):
                template_name = "fullVirtualizedFileHd.pt"
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
		return	DebianWheezyVMConfigurator.__name__ 

	@staticmethod
	def _configureNetworking(vm,path):
		#Configure interfaces and udev settings	
		try:

			try:
				#Backup current files
				shutil.copy(path+OXA_DEBIAN_INTERFACES_FILE_LOCATION,path+OXA_DEBIAN_INTERFACES_FILE_LOCATION+".bak")	
				shutil.copy(path+OXA_DEBIAN_UDEV_FILE_LOCATION,path+OXA_DEBIAN_UDEV_FILE_LOCATION+".bak")
			except Exception as e:
				pass

			with open(path+OXA_DEBIAN_INTERFACES_FILE_LOCATION,'w') as openif:
				DebianWheezyVMConfigurator.__configureInterfacesFile(vm,openif)
			with open(path+OXA_DEBIAN_UDEV_FILE_LOCATION,'w') as openudev:
				DebianWheezyVMConfigurator.__configureUdevFile(vm,openudev)
		except Exception as e:
			DebianWheezyVMConfigurator.logger.error(str(e))
			raise Exception("Could not configure interfaces or Udev file")

	@staticmethod
	def _configureLDAPSettings(vm,path):
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
			DebianWheezyVMConfigurator.logger.error("Could not configure LDAP file!! - "+str(e))

	@staticmethod
	def _configureHostName(vm,path):
		try:
			with open(path+OXA_DEBIAN_HOSTNAME_FILE_LOCATION,'w') as openhost:
				DebianWheezyVMConfigurator.__configureHostname(vm, openhost)
		except Exception as e:
			DebianWheezyVMConfigurator.logger.error("Could not configure hostname;skipping.. - "+str(e))
	@staticmethod
	def _configureSSHServer(vm,path):
		try:
			DebianWheezyVMConfigurator.logger.debug("Regenerating SSH keys...\n Deleting old keys...")
			subprocess.check_call("rm -f "+path+"/etc/ssh/ssh_host_*", shell=True, stdout=None)
			#subprocess.check_call("chroot "+path+" dpkg-reconfigure openssh-server ", shell=True, stdout=None)
			
			DebianWheezyVMConfigurator.logger.debug("Creating SSH1 key; this may take some time...")
			subprocess.check_call("ssh-keygen -q -f "+path+"/etc/ssh/ssh_host_key -N '' -t rsa1", shell=True, stdout=None)
			DebianWheezyVMConfigurator.logger.debug("Creating SSH2 RSA key; this may take some time...")
			subprocess.check_call("ssh-keygen -q -f "+path+"/etc/ssh/ssh_host_rsa_key -N '' -t rsa", shell=True, stdout=None)
			DebianWheezyVMConfigurator.logger.debug("Creating SSH2 DSA key; this may take some time...")
			subprocess.check_call("ssh-keygen -q -f "+path+"/etc/ssh/ssh_host_dsa_key -N '' -t dsa", shell=True, stdout=None)
		except Exception as e:
			DebianWheezyVMConfigurator.logger.error("Fatal error; could not regenerate SSH keys. Aborting to prevent VM to be unreachable..."+str(e))
			raise e


	#Public methods
	@staticmethod
	def createVmConfigurationFile(vm):

		#get env
		template_dirs = []
		template_dirs.append(os.path.join(os.path.dirname(__file__), 'templates/'))
		env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dirs))

		if vm.xen_configuration.hd_setup_type == "full-file-image" and vm.xen_configuration.virtualization_setup_type == "hvm" :
			DebianWheezyVMConfigurator.__createFullvirtualizationFileHdConfigFile(vm,env)
		else:
			raise Exception("type of file or type of virtualization not supported for the creation of xen vm configuration file")	

	@staticmethod
	def configureVmDisk(vm, path):
		
		if not path or not re.match(r'[\s]*\/\w+\/\w+\/.*', path,re.IGNORECASE): #For security, should never happen anyway
			raise Exception("Incorrect vm path")

		#Configure networking
		DebianWheezyVMConfigurator._configureNetworking(vm,path)
		DebianWheezyVMConfigurator.logger.info("Network configured successfully...")
		
		#Configure LDAP settings 
		DebianWheezyVMConfigurator._configureLDAPSettings(vm,path)
		DebianWheezyVMConfigurator.logger.info("Authentication configured successfully...")
	
		#Configure Hostname
		DebianWheezyVMConfigurator._configureHostName(vm,path)
		DebianWheezyVMConfigurator.logger.info("Hostname configured successfully...")
		
		#Regenerate SSH keys
		DebianWheezyVMConfigurator._configureSSHServer(vm,path)
		DebianWheezyVMConfigurator.logger.info("SSH have been keys regenerated...")
