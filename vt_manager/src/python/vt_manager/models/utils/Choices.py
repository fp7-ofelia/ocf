
class VirtTechClass: 
	
	VIRT_TECH_TYPE_XEN = "xen"
	VIRT_TECH_CHOICES = (
		(VIRT_TECH_TYPE_XEN, 'XEN'),
	)
	
	@staticmethod
	def validateVirtTech(value):
		for tuple in VirtTechClass.VIRT_TECH_CHOICES:
			if value in tuple:
				return
		raise Exception("Virtualization Type not valid")

    	
class OSDistClass():
	
	OS_DIST_TYPE_DEBIAN = "Debian"
	OS_DIST_TYPE_UBUNTU = "Ubuntu"
	OS_DIST_TYPE_REDHAT = "RedHat"
	OS_DIST_TYPE_CENTOS = "CentOS"
	
	OS_DIST_CHOICES = (
		(OS_DIST_TYPE_DEBIAN, 'Debian'),
		(OS_DIST_TYPE_UBUNTU, 'Ubuntu'),
		(OS_DIST_TYPE_REDHAT, 'RedHat'),
		(OS_DIST_TYPE_CENTOS, 'CentOS'),
	)
	@staticmethod	
	def validateOSDist(value):
		for tuple in OSDistClass.OS_DIST_CHOICES:
			if value in tuple:
				return
		raise Exception("OS Distribution not valid")


class OSVersionClass():

	OS_VERSION_TYPE_50 = "5.0"
	OS_VERSION_TYPE_60 = "6.0"
	OS_VERSION_TYPE_62 = "6.2"
	OS_VERSION_TYPE_70 = "7.0"
	
	OS_VERSION_CHOICES = (
		(OS_VERSION_TYPE_50, '5.0'),
		(OS_VERSION_TYPE_60, '6.0'),
		(OS_VERSION_TYPE_62, '6.2'),
		(OS_VERSION_TYPE_70, '7.0'),
	)
	@staticmethod
	def validateOSVersion(value):
		for tuple in OSVersionClass.OS_VERSION_CHOICES:
			if value in tuple:
				return
		raise Exception("OS Version not valid")

class OSTypeClass():
	
	OS_TYPE_TYPE_GNULINUX = "GNU/Linux"
	OS_TYPE_TYPE_WINDOWS = "Windows"
	
	OS_TYPE_CHOICES = (
		(OS_TYPE_TYPE_GNULINUX, 'GNU/Linux'),
		(OS_TYPE_TYPE_WINDOWS, 'Windows'),
	)
	@staticmethod
	def validateOSType(value):
		for tuple in OSTypeClass.OS_TYPE_CHOICES:
			if value in tuple:
				return
			
		raise Exception("OS Type not valid")

