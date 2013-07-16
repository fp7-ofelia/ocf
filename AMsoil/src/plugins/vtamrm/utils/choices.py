from utils import settings


class VirtTechClass: 
    @staticmethod
    def validateVirtTech(value):
	for tuple in settings.VIRT_TECH_CHOICES:
	    if value in tuple:
		return
	raise Exception("Virtualization Type not valid")

    	
class OSDistClass():
    @staticmethod	
    def validateOSDist(value):
	for tuple in settings.OS_DIST_CHOICES:
   	    if value in tuple:
		return
	raise Exception("OS Distribution not valid")


class OSVersionClass():
    @staticmethod
    def validateOSVersion(value):
	for tuple in settings.OS_VERSION_CHOICES:
      	    if value in tuple:
		return
	raise Exception("OS Version not valid")


class OSTypeClass():
    @staticmethod
    def validateOSType(value):
	for tuple in settings.OS_TYPE_CHOICES:
	    if value in tuple:
		return
	raise Exception("OS Type not valid")


class HDSetupTypeClass():
    @staticmethod
    def validate_hd_setup_type(value):
        for tuple in settings.HD_SETUP_TYPE_CHOICES:
            if value in tuple:
                return  
        raise Exception("HD Setup Type not valid")


class VirtTypeClass():
    @staticmethod
    def validate_virt_type(value):
        for tuple in settings.VIRTUALIZATION_SETUP_TYPE_CHOICES:
            if value in tuple:
                return  
        raise Exception("Virtualization Type not valid")
