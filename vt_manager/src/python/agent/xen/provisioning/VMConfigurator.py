from xen.provisioning.configurators.ofelia.OfeliaVMConfigurator import OfeliaVMConfigurator
from xen.provisioning.configurators.mediacat.MediacatVMConfigurator import MediacatVMConfigurator
from utils.Logger import Logger

'''
	@author: msune

	Configurator redirector	
'''


class VMConfigurator:
	
	logger = Logger.getLogger()
	
	@staticmethod
	def __getConfiguratorByOsType(configurator):
	
		if configurator != None and configurator != "":
			if configurator == MediacatVMConfigurator.getIdentifier():
				return MediacatVMConfigurator;
			else:
				raise Exception("Unknown configurator")	
		else:
			return OfeliaVMConfigurator
	

	
	@staticmethod
	def __configureNetworking(vm,path):
		#Call Appropiate configurator according to VM OS type	
		configurator = VMConfigurator.__getConfiguratorByOsType(vm.xen_configuration.configurator)
		configurator.configureNetworking(vm,path)
	@staticmethod
	def __configureLDAPSettings(vm,path):
		configurator = VMConfigurator.__getConfiguratorByOsType(vm.xen_configuration.configurator)
		configurator.configureLDAPSettings(vm,path)

	@staticmethod
	def __configureHostname(vm,path):
		configurator = VMConfigurator.__getConfiguratorByOsType(vm.xen_configuration.configurator)
		configurator.configureHostname(vm,path)


	##Public methods
	@staticmethod
	def configureVm(vm,pathToMountPoint):
		#Configure networking
		VMConfigurator.__configureNetworking(vm,pathToMountPoint)
		XenProvisioningDispatcher.logger.info("Network configured successfully...")
		
		#Configure LDAP settings 
		VMConfigurator.__configureLDAPSettings(vm,pathToMountPoint)
		XenProvisioningDispatcher.logger.info("Authentication configured successfully...")
	
		#Configure Hostname
		VMConfigurator.__configureHostname(vm,pathToMountPoint)
					
	@staticmethod
	def createVmConfigurationFile(vm):
		configurator = VMConfigurator.__getConfiguratorByOsType(vm.xen_configuration.configurator)
		configurator.createVmConfigurationFile(vm)
			



