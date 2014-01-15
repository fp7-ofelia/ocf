class VirtTechClass: 
    VIRT_TECH_TYPE_XEN = "xen"
    VIRT_TECH_CHOICES = (
        (VIRT_TECH_TYPE_XEN, 'XEN'),
    )
    @staticmethod
    def validate_virt_tech(value):
        for tuple in VirtTechClass.VIRT_TECH_CHOICES:
            if value in tuple:
                return
        raise Exception("Virtualization Type not valid")
            
class OSDistClass():
    OS_DIST_TYPE_DEBIAN = "Debian"
    OS_DIST_TYPE_UBUNTU = "Ubuntu"
    OS_DIST_TYPE_REDHAT = "RedHat"
    OS_DIST_CHOICES = (
        (OS_DIST_TYPE_DEBIAN, 'Debian'),
        (OS_DIST_TYPE_UBUNTU, 'Ubuntu'),
        (OS_DIST_TYPE_REDHAT, 'RedHat'),
    )
    @staticmethod        
    def validate_os_dist(value):	
        for tuple in OSDistClass.OS_DIST_CHOICES:
            if value in tuple:
                return
        raise Exception("OS Distribution not valid")

class OSVersionClass():
    OS_VERSION_TYPE_50 = "5.0"
    OS_VERSION_TYPE_60 = "6.0"
    OS_VERSION_CHOICES = (
        (OS_VERSION_TYPE_50, '5.0'),
        (OS_VERSION_TYPE_60, '6.0'),
    )
    @staticmethod
    def validate_os_version(value):
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
    def validate_os_type(value):
        for tuple in OSTypeClass.OS_TYPE_CHOICES:
            if value in tuple:
                return
        raise Exception("OS Type not valid")

class HDSetupTypeClass():
    HD_SETUP_TYPE_FILE_IMAGE = "file-image"
    HD_SETUP_TYPE_LV = "logical-volume-image"
    HD_SETUP_TYPE_CHOICES = (
        (HD_SETUP_TYPE_FILE_IMAGE, 'File image'),
        (HD_SETUP_TYPE_LV, 'Logical Volume Image'),
    )
    @staticmethod
    def validate_hd_setup_type(value):
        for tuple in HDSetupTypeClass.HD_SETUP_TYPE_CHOICES:
            if value in tuple:
                return  
        raise Exception("HD Setup Type not valid")

class VirtTypeClass():
    VIRTUALIZATION_SETUP_TYPE_PARAVIRTUALIZATION= "paravirtualization"
    VIRTUALIZATION_SETUP_TYPE_HAV = "hardware-assisted-virtualization"
    VIRTUALIZATION_SETUP_TYPE = (
        (VIRTUALIZATION_SETUP_TYPE_PARAVIRTUALIZATION, 'Paravirtualization'),
        (VIRTUALIZATION_SETUP_TYPE_HAV, 'Hardware-assisted virtualization'),
    )
    @staticmethod
    def validate_virt_type(value):
        for tuple in VirtTypeClass.VIRTUALIZATION_SETUP_TYPE:
            if value in tuple:
                return  
        raise Exception("Virtualization Type not valid")
