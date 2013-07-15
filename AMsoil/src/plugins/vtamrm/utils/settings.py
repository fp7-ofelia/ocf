'''@author: SergioVidiella'''


'''Virtualization Technology settings'''
VIRT_TECH_TYPE_XEN = "xen"

VIRT_TECH_CHOICES = (
    (VIRT_TECH_TYPE_XEN, 'XEN'),
)


'''OS Distribution settings'''
OS_DIST_TYPE_DEBIAN = "Debian"
OS_DIST_TYPE_UBUNTU = "Ubuntu"
OS_DIST_TYPE_REDHAT = "RedHat"

OS_DIST_CHOICES = (
    (OS_DIST_TYPE_DEBIAN, 'Debian'),
    (OS_DIST_TYPE_UBUNTU, 'Ubuntu'),
    (OS_DIST_TYPE_REDHAT, 'RedHat'),
)


'''OS Version settings'''
OS_VERSION_TYPE_50 = "5.0"
OS_VERSION_TYPE_60 = "6.0"

OS_VERSION_CHOICES = (
    (OS_VERSION_TYPE_50, '5.0'),
    (OS_VERSION_TYPE_60, '6.0'),
)


'''OS Type settings'''
OS_TYPE_TYPE_GNULINUX = "GNU/Linux"
OS_TYPE_TYPE_WINDOWS = "Windows"

OS_TYPE_CHOICES = (
    (OS_TYPE_TYPE_GNULINUX, 'GNU/Linux'),
    (OS_TYPE_TYPE_WINDOWS, 'Windows'),
)


'''HD Setup Type settings'''
HD_SETUP_TYPE_FILE_IMAGE = "file-image"
HD_SETUP_TYPE_LV = "logical-volume-image"

HD_SETUP_TYPE_CHOICES = (
    (HD_SETUP_TYPE_FILE_IMAGE, 'File image'),
    (HD_SETUP_TYPE_LV, 'Logical Volume Image'),
)


'''Virtualization Type settings'''
VIRTUALIZATION_SETUP_TYPE_PARAVIRTUALIZATION= "paravirtualization"
VIRTUALIZATION_SETUP_TYPE_HAV = "hardware-assisted-virtualization"

VIRTUALIZATION_SETUP_TYPE_CHOICES = (
    (VIRTUALIZATION_SETUP_TYPE_PARAVIRTUALIZATION, 'Paravirtualization'),
    (VIRTUALIZATION_SETUP_TYPE_HAV, 'Hardware-assisted virtualization'),
)


'''Action status Types'''
QUEUED_STATUS = "QUEUED"
ONGOING_STATUS= "ONGOING"
SUCCESS_STATUS  = "SUCCESS"
FAILED_STATUS   = "FAILED"

POSSIBLE_STATUS = (
    QUEUED_STATUS,
    ONGOING_STATUS,
    SUCCESS_STATUS,
    FAILED_STATUS
)


'''Action type Types'''
##Monitoring
#Servers
MONITORING_SERVER_VMS_TYPE="listActiveVMs"

MONITORING_TYPES = (
    #Server
    MONITORING_SERVER_VMS_TYPE,
)

#VMs
##Provisioning 
#VM provisioning actions        
PROVISIONING_VM_CREATE_TYPE = "create"
PROVISIONING_VM_START_TYPE = "start"
PROVISIONING_VM_DELETE_TYPE = "delete"
PROVISIONING_VM_STOP_TYPE = "hardStop"
PROVISIONING_VM_REBOOT_TYPE = "reboot"

PROVISIONING_TYPES = (
    #VM
    PROVISIONING_VM_CREATE_TYPE,
    PROVISIONING_VM_START_TYPE,
    PROVISIONING_VM_DELETE_TYPE,
    PROVISIONING_VM_STOP_TYPE,
    PROVISIONING_VM_REBOOT_TYPE,
)

'''All possible types '''
POSSIBLE_TYPES = (
    #Monitoring
    #Server
    MONITORING_SERVER_VMS_TYPE,

    ##Provisioning
    #VM
    PROVISIONING_VM_CREATE_TYPE,
    PROVISIONING_VM_START_TYPE,
    PROVISIONING_VM_DELETE_TYPE,
    PROVISIONING_VM_STOP_TYPE,
    PROVISIONING_VM_REBOOT_TYPE,
)

