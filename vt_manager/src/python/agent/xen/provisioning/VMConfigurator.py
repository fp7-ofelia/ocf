from xen.provisioning.configurators.DebianVMConfigurator import DebianVMConfigurator

'''
	@author: msune

	Configurator redirector	
'''


class VMConfigurator:
	
	@staticmethod
	def __getConfiguratorByOsType(os_type,os_distribution):

		if os_type == "GNU/Linux" and os_distribution == "Debian" :
			return DebianVMConfigurator
	

	
	@staticmethod
	def __configureNetworking(vm,path):
		#Call Appropiate configurator according to VM OS type	
		configurator = VMConfigurator.__getConfiguratorByOsType(vm.operating_system_type,vm.operating_system_distribution)
		configurator.configureNetworking(vm,path)
	@staticmethod
	def __configureLDAPSettings(vm,path):
		configurator = VMConfigurator.__getConfiguratorByOsType(vm.operating_system_type,vm.operating_system_distribution)
		configurator.configureLDAPSettings(vm,path)

	@staticmethod
	def __configureHostname(vm,path):
		configurator = VMConfigurator.__getConfiguratorByOsType(vm.operating_system_type,vm.operating_system_distribution)
		configurator.configureHostname(vm,path)


	##Public methods
	@staticmethod
	def configureVm(vm,pathToMountPoint):
		#Configure networking
		VMConfigurator.__configureNetworking(vm,pathToMountPoint)
		print "Network configured successfully..."
	
		#Configure LDAP settings 
		VMConfigurator.__configureLDAPSettings(vm,pathToMountPoint)
		print "Authentication configured successfully..."
	
		#Configure Hostname
		VMConfigurator.__configureHostname(vm,pathToMountPoint)
					
	@staticmethod
	def createVmConfigurationFile(vm):
		configurator = VMConfigurator.__getConfiguratorByOsType(vm.operating_system_type,vm.operating_system_distribution)
		configurator.createVmConfigurationFile(vm)
			



